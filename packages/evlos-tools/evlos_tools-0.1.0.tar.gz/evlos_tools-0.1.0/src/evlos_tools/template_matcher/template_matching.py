import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import torch
import numpy as np
from matplotlib import pyplot as plt
from loguru import logger
from datetime import datetime
from torchvision.transforms.v2 import InterpolationMode
import torchvision.transforms.v2 as v2
from feature_matching.lightglue.utils import rbd
from feature_matching.lightglue import viz2d


def get_size(max_size: int, h: int, w: int):
    """Get the size of the image after resizing."""
    scale = max_size / max(h, w)
    if scale < 1:
        h = int(h * scale)
        w = int(w * scale)
    return (h, w)


def image_preprocess(image: np.ndarray) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Transform the image while maintaining aspect ratio and return the scale factor.
    Args:
        image (np.ndarray): The input image.
    Returns:
        image (torch.Tensor): The transformed image.
        scale (torch.Tensor): The scale factor.
    """
    h, w = image.shape

    if image.ndim == 2:
        image = np.expand_dims(image, axis=2)  # HxW to HxWx1
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    extractor_transformations = v2.Compose(
        [
            v2.ToImage(),
            v2.ToDtype(torch.uint8, scale=True),
        ]
    )

    new_h, new_w = get_size(1024, h, w)
    logger.debug(f"Resized image shape: {(new_h, new_w)}")
    new_h = 384  #! TEMP
    new_w = 1024  # force width to 2048
    image = extractor_transformations(image)
    image = v2.functional.resize(
        image,
        size=(new_h, new_w),
        interpolation=InterpolationMode.BILINEAR,
        antialias=True,
    )
    image = v2.ToDtype(torch.float32, scale=True)(image)
    scale = torch.Tensor([image.shape[-1] / w, image.shape[-2] / h])
    return image, scale


def image_preprocess_cv2(image: np.ndarray) -> tuple[np.ndarray, tuple[float, float]]:
    """
    Transform the image while maintaining aspect ratio and return the scale factor.
    Args:
        image (np.ndarray): The input image.
    Returns:
        image (np.ndarray): The transformed image.
        scale (tuple[float, float]): The scale factor for x and y axes.
    """
    h, w = image.shape

    if image.ndim == 2:
        image = np.expand_dims(image, axis=2)  # HxW to HxWx1
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # new_h, new_w = get_size(1024, h, w)
    # logger.debug(f"Resized image shape: {(new_h, new_w)}")
    new_h = 288  #! TEMP
    new_w = 768  # force width to 2048
    image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    scale = (image.shape[1] / w, image.shape[0] / h)  # (scale_x, scale_y)
    # HWC to CHW
    image = np.transpose(image, (2, 0, 1))
    return np.expand_dims(image, axis=0) / 255.0, scale


def scale_4_points(pts: np.ndarray, scale: tuple[float, float]) -> np.ndarray:
    """
    Scale the 4 points of the oriented bounding box (OBB) by the given scale factors.
    Args:
        pts (np.ndarray): The OBB points with shape (N, 2).
        scale (tuple[float, float]): The scale factors for x and y axes.
    Returns:
        np.ndarray: The scaled OBB points.
    """
    pts[:, 0] /= scale[0]
    pts[:, 1] /= scale[1]
    return pts


def orb_template_matching(
    source_image: np.ndarray, target_image: np.ndarray, visualize: bool = False
) -> np.ndarray:
    """
    Performs ORB feature matching to find multiple objects of the target image within the source image. Partially adapted for multiple targets.
    Args:
        source_image (np.ndarray): The grayscale image in which to search for the target.
        target_image (np.ndarray): The grayscale template image to search for.
        visualize (bool): Whether to save intermediate visualization images.
    Returns:
        np.ndarray: The oriented bounding box (OBB) coordinates of detected objects in the source image.
    """
    ORB_FEATURES = 12_000  #! Config
    MIN_MATCH_COUNT = 35  #! Config based number of pins

    if visualize is True:
        output_dir = "pipeline/test_template_matching"
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Visualization images will be saved to: {output_dir}")
        now = datetime.now()
        time = now.strftime("%Y-%m-%d-%H:%M:%S.%f")[:-5]

    # --- 1. Initialize ORB Detector ---
    orb = cv2.ORB_create(nfeatures=ORB_FEATURES)

    # --- 2. Find Keypoints and Descriptors for the Template ---
    kp_template, des_template = orb.detectAndCompute(target_image, None)

    if des_template is None:
        raise ValueError("Could not compute descriptors for the template image.")

    # --- 3. Find Keypoints and Descriptors for the Scene ---
    kp_scene, des_scene = orb.detectAndCompute(source_image, None)

    # --- 4. Match Descriptors using a k-NN Matcher ---

    # method 1: FLANN based matcher
    # FLANN_INDEX_LSH = 6
    # index_params= dict(algorithm = FLANN_INDEX_LSH,
    #                    table_number = 6,
    #                    key_size = 12,
    #                    multi_probe_level = 1)
    # search_params = dict(checks=50)
    # flann = cv2.FlannBasedMatcher(index_params, search_params)
    # all_matches = flann.knnMatch(des_template, des_scene, k=2)

    # method 2: Brute-Force matcher
    # More suitable for low number of features
    bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING2, crossCheck=False)
    all_matches = bf.knnMatch(des_template, des_scene, k=2)

    # --- 5. Lowe's Ratio Test to Filter Good Matches ---
    good_matches = []
    # Check if all_matches is not empty and its elements are iterable
    if all_matches and all(
        isinstance(m, (list, tuple)) and len(m) == 2 for m in all_matches
    ):
        for m, n in all_matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
    else:
        # Handle the case where matches are not in pairs, perhaps by taking all of them
        # This part might need adjustment based on what knnMatch returns in this edge case.
        raise ValueError("knnMatch did not return pairs of matches as expected.")

    if len(good_matches) >= MIN_MATCH_COUNT:
        logger.debug(f"Found {len(good_matches)} good matches after ratio test.")
    else:
        logger.warning(
            f"Not enough good matches ({len(good_matches)}) found - skipping detection."
        )

    # --- 6. Visualize All Good Matches Before Detection Loop ---
    # This image shows every potential match that the algorithm will consider.
    # It can be crowded but gives a good overview.
    # if visualize is True:
    #     all_matches_img = cv2.drawMatches(
    #         target_image,
    #         kp_template,
    #         source_image,
    #         kp_scene,
    #         good_matches,
    #         None,
    #         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    #     )
    #     cv2.imwrite(
    #         os.path.join(output_dir, f"orb_all_good_matches_{time}.webp"),
    #         all_matches_img,
    #         [cv2.IMWRITE_WEBP_QUALITY, 50],
    #     )

    # --- 7. Iteratively Find and Draw Bounding Boxes ---
    detected_count = 0

    scene_with_boxes = source_image.copy()
    matches_to_process = list(good_matches)

    while len(matches_to_process) >= MIN_MATCH_COUNT:
        # We no longer need to check used_scene_kp_indices because we remove matches as we go
        current_matches = matches_to_process

        src_pts = np.float32(
            [kp_template[m.queryIdx].pt for m in current_matches]
        ).reshape(-1, 1, 2)
        dst_pts = np.float32(
            [kp_scene[m.trainIdx].pt for m in current_matches]
        ).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if M is None or mask is None:
            break

        inlier_matches = [m for i, m in enumerate(current_matches) if mask.ravel()[i]]
        logger.debug(
            f" -> Found {len(inlier_matches)} inlier matches for this detection."
        )

        if len(inlier_matches) < MIN_MATCH_COUNT:
            break

        detected_count += 1
        logger.debug(f"Detected object #{detected_count}")

        # --- 7b. Visualize the Inlier Matches for THIS Specific Object ---
        # Draw only the matches that were used (the inliers) for this detection
        if visualize is True:
            inlier_match_img = cv2.drawMatches(
                target_image,
                kp_template,
                source_image,
                kp_scene,
                inlier_matches,
                None,
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )

            # Add text to the visualization
            # cv2.putText(
            #     inlier_match_img,
            #     f"Inlier Matches for Object #{detected_count}",
            #     (10, 30),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     1,
            #     (0, 0, 255),
            #     2,
            # )

            # Show and save the inlier-specific visualization
            inlier_filename = os.path.join(
                output_dir, f"orb_inlier_matches_obj_{detected_count}_{time}.webp"
            )
            cv2.imwrite(
                inlier_filename, inlier_match_img, [cv2.IMWRITE_WEBP_QUALITY, 50]
            )

        # --- Draw Bounding Box on the main scene image ---
        h, w = target_image.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
            -1, 1, 2
        )
        dst = cv2.perspectiveTransform(pts, M)
        if visualize is True:
            scene_with_boxes = cv2.polylines(
                scene_with_boxes, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA
            )

        # * Disable for single object detection only
        break
        # --- Mark used keypoints and remove them from the list for the next iteration ---
        # inlier_indices = {m.trainIdx for m in inlier_matches}
        # matches_to_process = [
        #     m for m in matches_to_process if m.trainIdx not in inlier_indices
        # ]

    # * Disable for single object detection only
    # if detected_count > 0:
    #     logger.debug(f"Total objects detected: {detected_count}")
    # else:
    #     logger.warning(f"Total objects detected: {detected_count}")

    # --- 8. Display and Save the Final Image ---
    if visualize is True:
        output_filename = os.path.join(
            output_dir, f"orb_multiple_detections_final_{time}.webp"
        )
        cv2.imwrite(output_filename, scene_with_boxes, [cv2.IMWRITE_WEBP_QUALITY, 50])

    # return keypoints of the last detected object as an example
    if detected_count > 0:
        return np.int32(dst), len(inlier_matches)
    else:
        return None, None


def dl_template_matching(
    extractor_model,
    matcher_model,
    scene_image: np.ndarray,
    template_image: np.ndarray,
    device: tuple[torch.device, bool] = (torch.device("cuda:0"), True),
    visualize: bool = False,
    **kwargs,
) -> np.ndarray:
    """
    Performs deep-learning based feature matching to find multiple objects of the target image within the source image. Partially adapted for multiple targets.
    Args:
        extractor_model: The TensorRT feature extractor model.
        matcher_model: The Pytorch feature matcher model.
        scene_image (np.ndarray): The grayscale image in which to search for the target.
        template_image (np.ndarray): The grayscale template image to search for.
        device (tuple[torch.device, bool]): The device to run the models on and whether to use non-blocking transfers.
        visualize (bool): Whether to save intermediate visualization images.
    Returns:
        np.ndarray: The oriented bounding box (OBB) coordinates of detected objects in the source image.
    """
    # Unpack kwargs for logging
    kwargs = kwargs["kwargs"]
    MIN_OK_MATCH_COUNT = 200  # ? Config based number of pins

    # --- 1. Convert images to torch tensors and move to GPU ---
    scene_image_proc, scene_scale = image_preprocess_cv2(scene_image)

    template_image_proc, template_scale = image_preprocess_cv2(template_image)

    if visualize is True:
        output_dir = "main_debug/template_matching"
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Visualization images will be saved to: {output_dir}")
        now = datetime.now()
        time = now.strftime("%Y-%m-%d-%H:%M:%S.%f")[:-5]

    # # --- 2. Find Keypoints and Descriptors for the Scene/Template ---
    extractor_model.infer_async(
        {
            extractor_model.inputs[1].name: scene_image_proc,
            extractor_model.inputs[0].name: template_image_proc,
        }
    )
    output_results = extractor_model.get_async_results()
    normalized_keypoints01, descriptors01 = (
        output_results["normalized_keypoints01"],
        output_results["descriptors01"],
    )

    image0_dict = {
        "keypoints": torch.tensor(np.expand_dims(normalized_keypoints01[0], axis=0)).to(
            device[0], non_blocking=device[1]
        ),
        "descriptors": torch.tensor(np.expand_dims(descriptors01[0], axis=0)).to(
            device[0], non_blocking=device[1]
        ),
        "image_size": [scene_image.shape[1], scene_image.shape[0]],
    }
    image1_dict = {
        "keypoints": torch.tensor(np.expand_dims(normalized_keypoints01[1], axis=0)).to(
            device[0]
        ),
        "descriptors": torch.tensor(np.expand_dims(descriptors01[1], axis=0)).to(
            device[0]
        ),
        "image_size": [template_image.shape[1], template_image.shape[0]],
    }

    # --- 4. Match Descriptors using a LightGlue Matcher ---
    matches01 = matcher_model({"image0": image0_dict, "image1": image1_dict})

    matches = matches01["matches"][0]  # indices with shape (K,2)
    kpts_template = image0_dict["keypoints"][0][
        matches[..., 0]
    ]  # coordinates in image #0, shape (K,2)
    kpts_scene = image1_dict["keypoints"][0][
        matches[..., 1]
    ]  # coordinates in image #1, shape (K,2)

    # Rescale keypoints to original image size
    kpts_template = (
        scale_4_points(kpts_template, (template_scale[0], template_scale[1]))
        .cpu()
        .numpy()
    )
    kpts_scene = (
        scale_4_points(kpts_scene, (scene_scale[0], scene_scale[1])).cpu().numpy()
    )

    # --- 6. Visualize All Good Matches Before Detection Loop ---
    # This image shows every potential match that the algorithm will consider.
    # It can be crowded but gives a good overview.
    if visualize is True:
        axes = viz2d.plot_images([template_image, scene_image])
        viz2d.plot_matches(kpts_template, kpts_scene, color="lime", lw=0.2)
        viz2d.add_text(0, f"Stop after {matches01['stop']} layers", fs=25)
        viz2d.save_plot(os.path.join(output_dir, f"dl_all_good_matches_{time}.webp"))
        plt.close()

    if len(kpts_template) > MIN_OK_MATCH_COUNT:
        # --- 7. Find and Draw Bounding Box ---
        M, mask = cv2.findHomography(
            kpts_template, kpts_scene, cv2.USAC_MAGSAC, 0.25
        )  # robust fitting

        # --- Draw Bounding Box on the main scene image ---
        h, w = template_image.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
            -1, 1, 2
        )
        dst = cv2.perspectiveTransform(pts, M)

        # --- 7. Display and Save the Final Image with bbox---
        if visualize is True:
            scene_with_boxes = cv2.polylines(
                scene_image, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA
            )

            output_filename = os.path.join(
                output_dir,
                f"dl_bbox_{kwargs['defect_type']}_u{kwargs['unique']}_r{kwargs['row']}_c{kwargs['col']}.bmp",
            )
            cv2.imwrite(output_filename, scene_with_boxes)
            # [cv2.IMWRITE_WEBP_QUALITY, 100]
    else:
        dst = None

    # return keypoints of the last detected object as an example
    if isinstance(dst, np.ndarray):
        return np.int32(dst), len(matches)
    else:
        return None, len(matches)


def trt_template_matching(
    extractor_matcher_model,
    scene_image: np.ndarray,
    template_image: np.ndarray,
    device: tuple[torch.device, bool] = (torch.device("cuda:0"), True),
    visualize: bool = False,
    **kwargs,
) -> np.ndarray:
    """
    Performs deep-learning based feature matching to find multiple objects of the target image within the source image. Partially adapted for multiple targets.
    Args:
        extractor_matcher_model: The combined feature extractor and matcher model.
        scene_image (np.ndarray): The grayscale image in which to search for the target.
        template_image (np.ndarray): The grayscale template image to search for.
        device (tuple[torch.device, bool]): The device to run the models on and whether to use non-blocking transfers.
        visualize (bool): Whether to save intermediate visualization images.
    Returns:
        np.ndarray: The oriented bounding box (OBB) coordinates of detected objects in the source image.
    """
    # Unpack kwargs for logging
    kwargs = kwargs["kwargs"]
    MIN_OK_MATCH_COUNT = 200  # ? Config based number of pins

    # --- 1. Convert images to torch tensors and move to GPU ---
    scene_image_tensor, scene_scale = image_preprocess(scene_image)
    scene_image_tensor = scene_image_tensor.unsqueeze(0)
    # scene_image_tensor = scene_image_tensor.to(device[0], non_blocking=device[1])

    template_image_tensor, template_scale = image_preprocess(template_image)
    template_image_tensor = template_image_tensor.unsqueeze(0)
    # template_image_tensor = template_image_tensor.to(device[0], non_blocking=device[1])

    # scene_template_concat = torch.cat(
    #     [scene_image_tensor, template_image_tensor], dim=0
    # ).numpy()

    # if visualize is True:
    output_dir = "main_debug/template_matching"
    os.makedirs(output_dir, exist_ok=True)
    logger.debug(f"Visualization images will be saved to: {output_dir}")
    now = datetime.now()
    time = now.strftime("%Y-%m-%d-%H:%M:%S.%f")[:-5]

    # extractor_matcher_model.check_input(0, scene_template_concat)

    # # --- 2. Find features for the Template ---
    # features_template = extractor_model.extract(template_image_tensor)

    # if features_template is None:
    #     raise ValueError("Could not compute features for the template image.")

    # # --- 3. Find Keypoints and Descriptors for the Scene ---
    # features_scene = extractor_model.extract(scene_image_tensor)

    # # --- 4. Match Descriptors using a LightGlue Matcher ---

    # matches01 = matcher_model({"image0": features_template, "image1": features_scene})
    extractor_matcher_model.infer_async(
        {
            extractor_matcher_model.inputs[1].name: scene_image_tensor.numpy(),
            extractor_matcher_model.inputs[0].name: template_image_tensor.numpy(),
        }
    )

    output_results = extractor_matcher_model.get_async_results()
    kpts0_kpts1, matches0 = (
        output_results["keypoints"],
        output_results["matches"],
    )
    logger.debug(
        f"kpts0_kpts1 shape: {kpts0_kpts1.shape}, matches0 shape: {matches0.shape}"
    )
    print(kpts0_kpts1.shape, matches0.shape)
    # Keypoints output shape: (2, 2000, 2)
    # Matches output shape: (2000, 3)
    # Mscores output shape: (N,)

    features_scene = {"keypoints": kpts0_kpts1[0]}
    print(f"features_scene keypoints shape: {features_scene['keypoints'].shape}")
    features_template = {"keypoints": kpts0_kpts1[1]}
    logger.debug(
        f"features_template keypoints shape: {features_template['keypoints'].shape}, features_scene keypoints shape: {features_scene['keypoints'].shape}"
    )

    # Sum number of -1 in matches0 to get number of keypoints in image 0
    num_kpts0 = np.sum(matches0 != -1)
    logger.debug(f"Number of keypoints in image 0: {num_kpts0}")
    # Get real matches != -1
    matches01 = {"matches": matches0[matches0[:, 0] != -1, :3]}
    logger.debug(f"Number of matches found: {len(matches01['matches'])}")

    # Sum number of 0 in mscores0 to get real matches in image 0
    # num_real_matches0 = np.sum(mscores0 > 0)
    # logger.debug(f"Number of real matches in image 0: {num_real_matches0}")

    # features_template, features_scene, matches01 = [
    #     rbd(x) for x in [features_template, features_scene, matches01]
    # ]  # remove batch dimension
    matches = matches01["matches"]  # indices with shape (K,2)
    kpts_template = features_template["keypoints"][
        matches[..., 1]
    ]  # coordinates in image #0, shape (K,2)
    kpts_scene = features_scene["keypoints"][
        matches[..., 0]
    ]  # coordinates in image #1, shape (K,2)

    # if device[0].type == "cuda":
    #     kpts_template = kpts_template.cpu().numpy()
    #     kpts_scene = kpts_scene.cpu().numpy()
    # else:
    #     kpts_template = kpts_template.numpy()
    #     kpts_scene = kpts_scene.numpy()

    # Rescale keypoints to original image size
    kpts_template = scale_4_points(
        kpts_template, (template_scale[0], template_scale[1])
    )
    logger.debug(kpts_template.shape)
    kpts_scene = scale_4_points(kpts_scene, (scene_scale[0], scene_scale[1]))
    logger.debug(kpts_scene.shape)

    # --- 6. Visualize All Good Matches Before Detection Loop ---
    # This image shows every potential match that the algorithm will consider.
    # It can be crowded but gives a good overview.
    # if visualize is True:
    axes = viz2d.plot_images([template_image, scene_image])
    viz2d.plot_matches(kpts_template, kpts_scene, color="lime", lw=0.2)
    # viz2d.add_text(0, f"Stop after {matches01['stop']} layers", fs=25)
    viz2d.save_plot(os.path.join(output_dir, f"dl_all_good_matches_{time}.webp"))
    plt.close()

    if len(kpts_template) > MIN_OK_MATCH_COUNT:
        # --- 7. Find and Draw Bounding Box ---
        M, mask = cv2.findHomography(
            kpts_template, kpts_scene, cv2.USAC_MAGSAC, 0.25
        )  # robust fitting

        # --- Draw Bounding Box on the main scene image ---
        h, w = template_image.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
            -1, 1, 2
        )
        dst = cv2.perspectiveTransform(pts, M)

        # --- 7. Display and Save the Final Image with bbox---
        # if visualize is True:
        scene_with_boxes = cv2.polylines(
            scene_image, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA
        )

        output_filename = os.path.join(
            output_dir,
            f"dl_bbox_{kwargs['defect_type']}_u{kwargs['unique']}_r{kwargs['row']}_c{kwargs['col']}.bmp",
        )
        cv2.imwrite(output_filename, scene_with_boxes)
    # [cv2.IMWRITE_WEBP_QUALITY, 100]
    else:
        dst = None

    # return keypoints of the last detected object as an example
    if isinstance(dst, np.ndarray):
        return np.int32(dst), len(matches)
    else:
        return None, len(matches)

    # TODO: MAINTAIN ASPECT RATIO DURING RESIZING


# def dl_template_matching(
#     extractor_model,
#     matcher_model,
#     scene_image: np.ndarray,
#     template_image: np.ndarray,
#     device: tuple[torch.device, bool] = (torch.device("cuda:0"), True),
#     visualize: bool = False,
#     **kwargs,
# ) -> np.ndarray:
#     """
#     Performs deep-learning based feature matching to find multiple objects of the target image within the source image. Partially adapted for multiple targets.
#     Args:
#         extractor_model: The feature extractor model.
#         matcher_model: The feature matcher model.
#         scene_image (np.ndarray): The grayscale image in which to search for the target.
#         template_image (np.ndarray): The grayscale template image to search for.
#         device (tuple[torch.device, bool]): The device to run the models on and whether to use non-blocking transfers.
#         visualize (bool): Whether to save intermediate visualization images.
#     Returns:
#         np.ndarray: The oriented bounding box (OBB) coordinates of detected objects in the source image.
#     """
#     # Unpack kwargs for logging
#     kwargs = kwargs["kwargs"]
#     MIN_OK_MATCH_COUNT = 200  # ? Config based number of pins

#     # --- 1. Convert images to torch tensors and move to GPU ---
#     scene_image_tensor, scene_scale = image_preprocess(scene_image)
#     scene_image_tensor = scene_image_tensor.to(device[0], non_blocking=device[1])

#     template_image_tensor, template_scale = image_preprocess(template_image)
#     template_image_tensor = template_image_tensor.to(device[0], non_blocking=device[1])

#     if visualize is True:
#         output_dir = "main_debug/template_matching"
#         os.makedirs(output_dir, exist_ok=True)
#         logger.debug(f"Visualization images will be saved to: {output_dir}")
#         now = datetime.now()
#         time = now.strftime("%Y-%m-%d-%H:%M:%S.%f")[:-5]

#     # --- 2. Find features for the Template ---
#     features_template = extractor_model.extract(template_image_tensor)

#     if features_template is None:
#         raise ValueError("Could not compute features for the template image.")

#     # --- 3. Find Keypoints and Descriptors for the Scene ---
#     features_scene = extractor_model.extract(scene_image_tensor)

#     # --- 4. Match Descriptors using a LightGlue Matcher ---

#     matches01 = matcher_model({"image0": features_template, "image1": features_scene})

#     features_template, features_scene, matches01 = [
#         rbd(x) for x in [features_template, features_scene, matches01]
#     ]  # remove batch dimension
#     matches = matches01["matches"]  # indices with shape (K,2)
#     kpts_template = features_template["keypoints"][
#         matches[..., 0]
#     ]  # coordinates in image #0, shape (K,2)
#     kpts_scene = features_scene["keypoints"][
#         matches[..., 1]
#     ]  # coordinates in image #1, shape (K,2)

#     if device[0].type == "cuda":
#         kpts_template = kpts_template.cpu().numpy()
#         kpts_scene = kpts_scene.cpu().numpy()
#     else:
#         kpts_template = kpts_template.numpy()
#         kpts_scene = kpts_scene.numpy()

#     # --- 6. Visualize All Good Matches Before Detection Loop ---
#     # This image shows every potential match that the algorithm will consider.
#     # It can be crowded but gives a good overview.
#     # if visualize is True:
#     #     axes = viz2d.plot_images([template_image_tensor, scene_image_tensor])
#     #     viz2d.plot_matches(kpts_template, kpts_scene, color="lime", lw=0.2)
#     #     viz2d.add_text(0, f"Stop after {matches01['stop']} layers", fs=25)
#     #     viz2d.save_plot(os.path.join(output_dir, f"dl_all_good_matches_{time}.webp"))
#     #     plt.close()

#     # Rescale keypoints to original image size
#     kpts_template = scale_4_points(
#         kpts_template, (template_scale[0], template_scale[1])
#     )
#     kpts_scene = scale_4_points(kpts_scene, (scene_scale[0], scene_scale[1]))

#     if len(kpts_template) > MIN_OK_MATCH_COUNT:
#         # --- 7. Find and Draw Bounding Box ---
#         M, mask = cv2.findHomography(
#             kpts_template, kpts_scene, cv2.USAC_MAGSAC, 0.25
#         )  # robust fitting

#         # --- Draw Bounding Box on the main scene image ---
#         h, w = template_image.shape
#         pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
#             -1, 1, 2
#         )
#         dst = cv2.perspectiveTransform(pts, M)

#         # --- 7. Display and Save the Final Image with bbox---
#         if visualize is True:
#             scene_with_boxes = cv2.polylines(
#                 scene_image, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA
#             )

#             output_filename = os.path.join(
#                 output_dir,
#                 f"dl_bbox_{kwargs['defect_type']}_u{kwargs['unique']}_r{kwargs['row']}_c{kwargs['col']}.bmp",
#             )
#             cv2.imwrite(output_filename, scene_with_boxes)
#             # [cv2.IMWRITE_WEBP_QUALITY, 100]
#     else:
#         dst = None

#     # return keypoints of the last detected object as an example
#     if isinstance(dst, np.ndarray):
#         return np.int32(dst), len(matches)
#     else:
#         return None, len(matches)
