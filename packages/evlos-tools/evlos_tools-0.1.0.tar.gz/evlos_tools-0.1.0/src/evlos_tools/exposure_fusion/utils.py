import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from loguru import logger


def deinterleave_image(
    interleaved_image: np.ndarray, num_exposures: int = 4
) -> list[np.ndarray]:
    """
    Deinterleaves an multi-exposure interleaved image into separate exposure images.
    Args:
        interleaved_image (np.ndarray): The interleaved input image.
        num_exposures (int): Number of exposures interleaved in the image.
    Returns:
        list[np.ndarray] (list[[H, W]]): A list of deinterleaved exposure images.
    """
    exposures = []
    for i in range(num_exposures):
        exposures.append(interleaved_image[i::num_exposures, :])
    return exposures


def preprocess(exposures: list[np.ndarray]) -> np.ndarray:
    """
    Preprocesses a list of grayscale exposure images for model input.
    Args:
        exposures (list[np.ndarray], list[[H, W]]): List of input exposure images.
    Returns:
        np.ndarray (N, 1, H, W): Preprocessed burst images ready for ONNX/TensorRT model input.
    """
    burst_images = (
        np.expand_dims(np.stack(exposures, axis=0), axis=1).astype(np.float32) / 255.0
    )
    return burst_images  # Shape: (N, 1, H, W)


def mertens_fusion(exposures, output_dir):
    logger.debug("  - Running OpenCV Mertens Exposure Fusion")

    # Mertens also expects 3-channel images
    exposures_bgr = [cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) for img in exposures]

    merge_mertens = cv2.createMergeMertens(
        exposure_weight=1.0, contrast_weight=1.0, saturation_weight=0.0
    )
    fused_image = merge_mertens.process(exposures_bgr)

    # Convert the final fused BGR image back to grayscale
    result_8bit = np.clip(
        cv2.cvtColor(fused_image, cv2.COLOR_BGR2GRAY) * 255, 0, 255
    ).astype(np.uint8)

    return result_8bit


def analyze_exposure_quality(
    exposures,
    exposure_times,
    bit_depth=8,
    noise_floor_dn=10,
    saturation_headroom_dn=5,
    overlap_target=0.2,
):
    logger.info("\n--- Exposure Quality Analysis ---")
    max_val = 2**bit_depth - 1
    usable_bands = []

    for i, img in enumerate(exposures):
        total_pixels = img.size
        saturated_pixels = np.sum(img >= (max_val - saturation_headroom_dn))
        underexposed_pixels = np.sum(img <= noise_floor_dn)
        saturation_percent = (saturated_pixels / total_pixels) * 100
        underexposure_percent = (underexposed_pixels / total_pixels) * 100

        usable_start = (
            np.min(img[img > noise_floor_dn]) if np.any(img > noise_floor_dn) else 0
        )
        usable_end = (
            np.max(img[img < (max_val - saturation_headroom_dn)])
            if np.any(img < (max_val - saturation_headroom_dn))
            else max_val
        )
        usable_bands.append((usable_start, usable_end))

        logger.info(f"\n[Exposure {i}: {exposure_times[i]:.1f} us]")
        logger.info(
            f"  - Saturated % (>{max_val - saturation_headroom_dn}): {saturation_percent:.2f}%"
        )
        logger.info(
            f"  - In Noise Floor % (<{noise_floor_dn}): {underexposure_percent:.2f}%"
        )
        logger.info(f"  - Usable Band (DN): {usable_start} - {usable_end}")

    logger.info("\n--- Overlap Analysis & Judgement ---")
    for i in range(len(exposures) - 1):
        band_current = usable_bands[i]
        band_next = usable_bands[i + 1]

        overlap_start = max(band_current[0], band_next[0])
        overlap_end = min(band_current[1], band_next[1])
        overlap_width = max(0, overlap_end - overlap_start)

        band_current_width = band_current[1] - band_current[0]
        overlap_percent = (
            (overlap_width / band_current_width) * 100 if band_current_width > 0 else 0
        )

        logger.info(
            f"\n[Overlap between Exp {i} ({exposure_times[i]:.1f}us) and Exp {i + 1} ({exposure_times[i + 1]:.1f}us)]"
        )
        logger.info(
            f"  - Overlap Region (DN): {overlap_start} - {overlap_end} (Width: {overlap_width})"
        )
        logger.info(
            f"  - Overlap Percentage: {overlap_percent:.1f}% (Target: >{overlap_target * 100}%)"
        )

        # Automated Judgement
        judgement = []
        if saturation_percent > 10.0:
            judgement.append("High saturation, consider shortening exposure.")
        if underexposure_percent > 50.0:
            judgement.append("High noise floor, consider lengthening exposure.")
        if overlap_percent < overlap_target * 100:
            judgement.append("Poor overlap with next exposure.")
        if not judgement:
            judgement.append("Looks well-placed.")
        logger.info(f"  - Judgement: {' '.join(judgement)}")

    return usable_bands


def save_annotated_histograms(
    exposures, exposure_times, usable_bands, output_dir, bit_depth=8
):
    logger.info("\n  - Generating and saving annotated exposure histograms...")
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(exposures)))
    max_val = 2**bit_depth

    for i, img in enumerate(exposures):
        hist = cv2.calcHist([img], [0], None, [max_val], [0, max_val])
        max_x = np.argmax(hist)
        max_y = hist[max_x][0]
        ax.plot(
            hist, color=colors[i], label=f"{exposure_times[i]:.1f} us Exposure", lw=2
        )
        ax.annotate(
            f"Maximum value: {max_y:.2f}",
            xy=(max_x, max_y),
            xytext=(max_x - 1, max_y - 1),
            arrowprops=dict(facecolor="red"),
        )
        # Shade the usable band
        ax.axvspan(usable_bands[i][0], usable_bands[i][1], color=colors[i], alpha=0.15)

    ax.set_title("Annotated Exposure Histograms with Usable Bands", fontsize=16)
    ax.set_xlabel("Pixel Intensity (0-255)")
    ax.set_ylabel("Pixel Count (Log Scale)")
    ax.set_xlim([0, max_val])
    ax.set_yscale("log")
    ax.grid(True, which="both", ls="--", alpha=0.3)
    ax.legend()
    path = os.path.join(output_dir, "exposure_histograms_annotated.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved to {path}")


def calculate_and_print_hdr_metrics(image, method_name):
    total_pixels = image.size
    contrast = np.std(image)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    prob = hist / total_pixels
    entropy = -np.sum(prob * np.log2(prob + 1e-9))
    clipped_white = np.sum(image == 255)
    clipped_black = np.sum(image == 0)
    clipped_white_percent = (clipped_white / total_pixels) * 100
    clipped_black_percent = (clipped_black / total_pixels) * 100
    logger.info(f"--- Metrics for HDR Result: {method_name} ---")
    logger.info(f"  - Contrast (Std Dev): {contrast:.2f}")
    logger.info(f"  - Entropy (Detail):   {entropy:.2f}")
    logger.info(f"  - Clipped White (255):{clipped_white_percent:.2f}%")
    logger.info(f"  - Clipped Black (0):  {clipped_black_percent:.2f}%")


def run_opencv_mertens_fusion(exposures, output_dir):
    logger.info("Running OpenCV Mertens Exposure Fusion")

    # Mertens also expects 3-channel images
    exposures_bgr = [cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) for img in exposures]

    merge_mertens = cv2.createMergeMertens(exposure_weight=1.0)
    fused_image = merge_mertens.process(exposures_bgr)

    # Convert the final fused BGR image back to grayscale
    result_8bit = np.clip(
        cv2.cvtColor(fused_image, cv2.COLOR_BGR2GRAY) * 255, 0, 255
    ).astype(np.uint8)

    path = os.path.join(output_dir, "05_hdr_result_opencv_mertens_fusion.bmp")
    cv2.imwrite(path, result_8bit)
    logger.info(f"Saved to {path}")
    calculate_and_print_hdr_metrics(result_8bit, "OpenCV Mertens Fusion")


# --- Stage 3: Main Execution and Saving Results ---

if __name__ == "__main__":
    """
    - Contrast (Std Dev): 29.90
    - Entropy (Detail):   6.61
    - Clipped White (255):0.00%
    - Clipped Black (0):  0.10%
    """
    # --- Parameters ---
    EXPOSURE_TIMES = [175.0, 88.0, 55.0, 30.0]
    EXPOSURE_TIMES_NP = np.array(EXPOSURE_TIMES, dtype=np.float32)
    BIT_DEPTH = 8

    # --- Analysis & Judgement Parameters ---
    NOISE_FLOOR_DN = 5  # Pixels below this are considered in the noise floor
    SATURATION_HEADROOM_DN = 5  # Pixels above (255 - this) are considered saturated
    OVERLAP_TARGET_PERCENT = 0.30  # Target 30% overlap between usable bands

    # --- Input Directory ---
    # ROOT_DIR = "C:/Users/Administrator/Downloads/evlos/ipex/Democam Archive/NG/temp"
    ROOT_DIR = "E:/DemoCam3 Files Arif/Picture/GL41400051025"
    OUTPUT_DIR = "C:/Users/Administrator/Downloads/Exposure Fusion Picture"

    # --- Optional: Specify a single image to process ---
    # If IMAGE_NAME is None, it will process all images in the ROOT_DIR
    IMAGE_NAME = "2025-08-13_14-59-32_534.bmp"

    if IMAGE_NAME:
        ROOT_DIR = os.path.join(ROOT_DIR, IMAGE_NAME)
        OUTPUT_DIR = os.path.join(OUTPUT_DIR, IMAGE_NAME)

        # --- Create Output Directory ---
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"Created output directory: {OUTPUT_DIR}")

        # --- Generate and Process Data ---
        print("\n1. Deinterleaving  data (UINT8)...")
        interleaved_image = cv2.imread(
            ROOT_DIR,
            cv2.IMREAD_UNCHANGED,
        )
        exposures = deinterleave_image(interleaved_image, len(EXPOSURE_TIMES))

        # --- Calculate and Report Metrics ---
        print("\n2. Saving input images...")
        interleaved_path = os.path.join(OUTPUT_DIR, "00_input_interleaved.bmp")
        cv2.imwrite(interleaved_path, interleaved_image)
        for i, img in enumerate(exposures):
            filename = f"01_exposure_{i}_{int(EXPOSURE_TIMES[i])}us.bmp"
            filepath = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(filepath, img)

        print("\n3. Analyzing individual exposures and providing judgement...")
        usable_bands = analyze_exposure_quality(
            exposures,
            EXPOSURE_TIMES,
            BIT_DEPTH,
            NOISE_FLOOR_DN,
            SATURATION_HEADROOM_DN,
            OVERLAP_TARGET_PERCENT,
        )
        save_annotated_histograms(
            exposures, EXPOSURE_TIMES, usable_bands, OUTPUT_DIR, BIT_DEPTH
        )

        # --- Run and Compare HDR Methods ---
        print("\n4. Running HDR and Fusion algorithms...")
        # run_opencv_hdr(exposures, EXPOSURE_TIMES_NP, OUTPUT_DIR, method='debevec')
        # run_opencv_hdr(exposures, EXPOSURE_TIMES_NP, OUTPUT_DIR, method='robertson')
        run_opencv_mertens_fusion(exposures, OUTPUT_DIR)

        print(
            f"\nProcessing complete. All images, metrics, and plots saved in the '{OUTPUT_DIR}' directory."
        )
    else:
        IMAGE_NAMES = os.listdir(ROOT_DIR)

        for image_name in IMAGE_NAMES:
            root_path = os.path.join(ROOT_DIR, image_name)
            output_path = os.path.join(OUTPUT_DIR, image_name)
            # --- Create Output Directory ---
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                print(f"Created output directory: {output_path}")

            # --- Generate and Process Data ---
            print("\n1. Deinterleaving  data (UINT8)...")
            interleaved_image = cv2.imread(
                root_path,
                cv2.IMREAD_UNCHANGED,
            )
            exposures = deinterleave_image(interleaved_image, len(EXPOSURE_TIMES))

            # --- Calculate and Report Metrics ---
            print("\n2. Saving input images...")
            interleaved_path = os.path.join(output_path, "00_input_interleaved.bmp")
            cv2.imwrite(interleaved_path, interleaved_image)
            for i, img in enumerate(exposures):
                filename = f"01_exposure_{i}_{int(EXPOSURE_TIMES[i])}us.bmp"
                filepath = os.path.join(output_path, filename)
                cv2.imwrite(filepath, img)

            print("\n3. Analyzing individual exposures and providing judgement...")
            usable_bands = analyze_exposure_quality(
                exposures,
                EXPOSURE_TIMES,
                BIT_DEPTH,
                NOISE_FLOOR_DN,
                SATURATION_HEADROOM_DN,
                OVERLAP_TARGET_PERCENT,
            )
            save_annotated_histograms(
                exposures, EXPOSURE_TIMES, usable_bands, output_path, BIT_DEPTH
            )

            # --- Run and Compare HDR Methods ---
            print("\n4. Running HDR and Fusion algorithms...")
            # run_opencv_hdr(exposures, EXPOSURE_TIMES_NP, output_path, method='debevec')
            # run_opencv_hdr(exposures, EXPOSURE_TIMES_NP, output_path, method='robertson')
            run_opencv_mertens_fusion(exposures, output_path)

            print(
                f"\nProcessing complete. All images, metrics, and plots saved in the '{output_path}' directory."
            )
