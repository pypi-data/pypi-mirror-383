import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
import gc
import cv2
import math
from loguru import logger
from imutils import contours

_connectors_partitioning_output_dir = "output_main/connector_partitioning"

#! Mapping is determined based on defects location (VERIFY)
_parts_partition_map = {
    "Contact 1": "Contact",
    "Contact 2": "Contact",
    "Contact 3": "Contact",
    "Contact 4": "Contact",
    "Contact 5": "Contact",
    "Contact 6": "Contact",
    "Contact 7": "Contact",
    "Contact 8": "Contact",
    "Contact 9": "Contact",
    "Contact 10": "Contact",
    "Contact 11": "Contact",
    "Contact BC": "Contact",
    "Contact C": "Contact",
    "Housing BC": "Housing",
    "Housing BL": "Housing",
    "Housing BR": "Housing",
    "Housing C": "Housing C",
    "Housing C1": "Housing C",
    "Housing C2": "Housing C",
    "Housing L": "Housing",
    "Housing R": "Housing",
    "Pin B1": "Pin",
    "Pin B2": "Pin",
    "Pin B3": "Pin",
    "Pin B4": "Pin",
    "Pin B5": "Pin",
    "Pin B6": "Pin",
    "Pin B7": "Pin",
    "Pin B8": "Pin",
    "Pin B9": "Pin",
    "Pin B10": "Pin",
    "Pin B11": "Pin",
    "Pin B12": "Pin",
    "Pin E1": "Pin E",
    "Pin E10": "Pin E",
    "Pin E11": "Pin E",
    "Pin E12": "Pin E",
    "Pin E2": "Pin E",
    "Pin E3": "Pin E",
    "Pin E4": "Pin E",
    "Pin E5": "Pin E",
    "Pin E6": "Pin E",
    "Pin E7": "Pin E",
    "Pin E8": "Pin E",
    "Pin E9": "Pin E",
    "Pin EC": "Pin E",
    "Pin T1": "Pin",
    "Pin T10": "Pin",
    "Pin T11": "Pin",
    "Pin T12": "Pin",
    "Pin T2": "Pin",
    "Pin T3": "Pin",
    "Pin T4": "Pin",
    "Pin T5": "Pin",
    "Pin T6": "Pin",
    "Pin T7": "Pin",
    "Pin T8": "Pin",
    "Pin T9": "Pin",
    "Shell L": "Shell",
    "Shell R": "Shell",
}

sku_number_of_square_partitions = {
    "CA 20p": 5,
    # "CA 60"
}


def sort_contours(
    cnts: list[list[np.ndarray]], grid_size: tuple[int, int] = (25, 2)
) -> list[list[np.ndarray]]:
    """
    Sort contours into a grid layout (rows and columns).
    Args:
        cnts (list of list of np.ndarray): List of contours to be sorted.
        grid_size (tuple of int): Number of columns and rows in the grid.
    Returns:
        list of list of np.ndarray: Sorted contours in a grid layout.
    """
    (cnts, _) = contours.sort_contours(cnts, method="top-to-bottom")

    tray_rows = []
    row = []
    for i, c in enumerate(cnts, 1):
        row.append(c)
        if i % grid_size[1] == 0:
            (cnt, _) = contours.sort_contours(row, method="left-to-right")
            tray_rows.append(cnt)
            row = []
    return tray_rows


def obb_to_orbb(obb: np.ndarray) -> np.ndarray:
    """
    Convert oriented bounding box (OBB) to oriented rectangle bounding box (ORBB).
    Args:
        obb (np.ndarray): The OBB coordinates of shape (4, 2).
    Returns:
        np.ndarray: The ORBB coordinates of shape (4, 2).
    """
    if obb.shape != (4, 2):
        raise ValueError(f"Expected obb shape (4, 2), but got {obb.shape}")
    rect = cv2.minAreaRect(obb)
    box = cv2.boxPoints(rect)
    box = box.astype(int)
    return box


def bbox_to_xywhn(
    bbox: np.ndarray, image_shape: tuple[int, int]
) -> tuple[float, float, float, float]:
    """
    Convert bounding box (bbox) to normalized (x, y, w, h) format.
    Args:
        bbox (np.ndarray): The bbox coordinates of shape (4, 2).
        image_shape (tuple of int): The shape of the image as (height, width).
    Returns:
        tuple of float: The normalized (x_center, y_center, width, height) values.
    """
    if bbox.shape != (4, 2):
        raise ValueError(f"Expected bbox shape (4, 2), but got {bbox.shape}")
    height, width = image_shape
    x_coords = bbox[:, 0]
    y_coords = bbox[:, 1]
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    box_width = x_max - x_min
    box_height = y_max - y_min
    x_center = x_min + box_width / 2
    y_center = y_min + box_height / 2
    return (
        x_center / width,
        y_center / height,
        box_width / width,
        box_height / height,
    )


def xywhn_to_xyxy(
    xywhn: tuple[float, float, float, float], image_shape: tuple[int, int]
) -> tuple[int, int, int, int]:
    """
    Convert normalized (x, y, w, h) format to bounding box (bbox).
    Args:
        xywhn (tuple of float): The normalized (x_center, y_center, width, height) values.
        image_shape (tuple of int): The shape of the image as (height, width).
    Returns:
        tuple of int: The bbox coordinates as (x_min, y_min, x_max, y_max).
    Raises:
        ValueError: If the input values are not floats or if the length of xywhn is not 4.
    """
    if not all(isinstance(i, float) for i in xywhn):
        raise ValueError(f"Expected all xywhn elements to be float, but got {xywhn}")
    if len(xywhn) != 4:
        raise ValueError(f"Expected xywhn length 4, but got {len(xywhn)}")

    height, width = image_shape
    x_center = xywhn[0] * width
    y_center = xywhn[1] * height
    box_width = xywhn[2] * width
    box_height = xywhn[3] * height
    x_min = int(x_center - box_width / 2)
    y_min = int(y_center - box_height / 2)
    x_max = int(x_center + box_width / 2)
    y_max = int(y_center + box_height / 2)
    return (x_min, y_min, x_max, y_max)


def sort_bbox_corners_clockwise(bbox: np.ndarray) -> np.ndarray:
    """
    Sort the corners of a bounding box in clockwise order starting from the top-left corner.
    Args:
        bbox (np.ndarray): The bbox coordinates of shape (4, 2).
    Returns:
        np.ndarray: The sorted bbox coordinates of shape (4, 2).
    """
    if bbox.shape != (4, 2):
        raise ValueError(f"Expected bbox shape (4, 2), but got {bbox.shape}")

    # Calculate the center of the bounding box
    center = np.mean(bbox, axis=0)

    # Calculate the angle of each corner with respect to the center
    angles = np.arctan2(bbox[:, 1] - center[1], bbox[:, 0] - center[0])

    # Sort the corners based on the angles
    sorted_indices = np.argsort(angles)
    sorted_bbox = bbox[sorted_indices]

    # Ensure the top-left and top-right is longer than top-left to bottom-left
    if np.linalg.norm(sorted_bbox[0] - sorted_bbox[1]) < np.linalg.norm(
        sorted_bbox[0] - sorted_bbox[3]
    ):
        sorted_bbox = np.roll(sorted_bbox, 1, axis=0)

    return sorted_bbox


def crop_n_straighten(image: np.ndarray, orbb: np.ndarray) -> np.ndarray:
    """
    Crop and straighten the image using the ORBB coordinates.
    Args:
        image (np.ndarray): The original image.
        orbb (np.ndarray): The ORBB coordinates of shape (4, 2).
    Returns:
        np.ndarray: The cropped and straightened image.
    """
    if orbb.shape != (4, 2):
        raise ValueError(f"Expected orbb shape (4, 2), but got {orbb.shape}")
    orbb = sort_bbox_corners_clockwise(orbb)

    # Determine the width and height of the new image
    width_a = np.linalg.norm(orbb[0] - orbb[1])
    width_b = np.linalg.norm(orbb[2] - orbb[3])
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(orbb[0] - orbb[3])
    height_b = np.linalg.norm(orbb[1] - orbb[2])
    max_height = max(int(height_a), int(height_b))

    if max_width < max_height:
        raise ValueError(
            f"Expected max_width >= max_height, but got {max_width} < {max_height}"
        )

    # Define the destination points for the perspective transform
    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    # Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(orbb.astype("float32"), dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    return warped


def write_image(
    warped: np.ndarray,
    xywhn: tuple[float, float, float, float],
    partition_class: str,
    rc: tuple[int, int],
) -> None:
    """
    Crop and write the partitioning image to the corresponding directory.
    Args:
        warped (np.ndarray): The warped image of the pocket.
        xywhn (tuple[float, float, float, float]): The normalized (x, y, w, h) coordinates of the connector partition.
        partition_class (str): The partition class for naming the subdirectory.
        rc (tuple of int): The row and column indices of the pocket for naming the file.
    Raises:
        ValueError: If the partition_class is unknown or if the bbox shape is incorrect.
    """
    # Argument validation
    main_class = _parts_partition_map.get(partition_class, "Unknown")
    if main_class == "Unknown":
        raise ValueError(f"Unknown partition class: {partition_class}")
    if len(xywhn) != 4:
        raise ValueError(f"Expected xywhn shape (4,), but got {len(xywhn)}")

    # Folder validation
    if not os.path.exists(_connectors_partitioning_output_dir):
        os.makedirs(_connectors_partitioning_output_dir)
    partition_class_dir = os.path.join(_connectors_partitioning_output_dir, main_class)
    if not os.path.exists(partition_class_dir):
        os.makedirs(partition_class_dir)

    # Crop and save image
    x1, y1, x2, y2 = xywhn_to_xyxy(xywhn, warped.shape[:2])
    pocket = warped[y1:y2, x1:x2]
    part_image_path = os.path.join(
        partition_class_dir, f"{partition_class}_{rc[0]}_{rc[1]}.bmp"
    )
    cv2.imwrite(part_image_path, pocket)


def get_pixel_overlap(image_shape: tuple[int, int], min_overlap_pix: int = 40) -> int:
    """
    Calculate the pixel overlap needed for partitioning based on image shape.
    Args:
        image_shape (tuple of int): The shape of the image as (height, width).
        min_overlap_pix (int): The minimum overlapping pixels for each square.
    Returns:
        int: The calculated pixel overlap.
    Raises:
        ValueError: If the image height is less than or equal to zero.
    """
    height, width = image_shape
    if height <= 0:
        raise ValueError(f"Expected image height > 0, but got {height}")

    num_squares = math.ceil(width / height)
    overlap_pix = int(((num_squares * height) - width) / (num_squares - 1))

    if overlap_pix < min_overlap_pix:
        num_squares = math.ceil(width / height) + 1
        return int(((num_squares * height) - width) / (num_squares - 1))

    return overlap_pix


def write_image_simple(
    warped: np.ndarray,
    overlap_pix: int = 40,
    sku: str = "Unknown",
    defect_type: str = "Unknown",
    unique: str = "0",
    rc: tuple[int, int] = (0, 0),
) -> None:
    """
    Crop the warped image into multiple overlapping squares and write to the corresponding directory. Square is Height x Height with overlap between column squares.
    Args:
        warped (np.ndarray): The warped image of the pocket.
        overlap_pix (int): The overlapping pixels for each square.
        sku (str): The SKU for naming the subdirectory.
        defect_type (str): The defect type for naming the file.
        rc (tuple of int): The row and column indices of the pocket for naming the file.
    Raises:
        ValueError: If the sku is unknown.
    """
    # Argument validation
    if sku == "Unknown":
        raise ValueError("SKU cannot be 'Unknown'")

    # Folder validation
    if not os.path.exists(_connectors_partitioning_output_dir):
        os.makedirs(_connectors_partitioning_output_dir)
    sku_dir = os.path.join(_connectors_partitioning_output_dir, sku)
    if not os.path.exists(sku_dir):
        os.makedirs(sku_dir)

    # Crop and save image
    height, width = warped.shape[:2]
    for start_x in range(0, width, height - overlap_pix):
        end_x = start_x + height
        if end_x > width:
            end_x = width
            start_x = max(0, end_x - height)
        square = warped[:, start_x:end_x]
        part_image_path = os.path.join(
            sku_dir,
            f"{defect_type}_u{unique}_r{rc[0]}_c{rc[1]}_s{start_x}_e{end_x}.bmp",
        )
        # cv2.imwrite(part_image_path, square)


def plot_connector_partitioning(
    image: np.ndarray,
    xywhn: tuple[float, float, float, float],
    partition_class: str,
) -> np.ndarray:
    """
    Plot the connector partitioning xywhn on the image.
    Args:
        image (np.ndarray): The original image.
        xywhn (tuple[float, float, float, float]): The normalized (x, y, w, h) coordinates of the connector partition.
        partition_class (str): The partition class for labeling the box.
    Returns:
        np.ndarray: The image with the plotted connector's partition.
    Raises:
        ValueError: If the partition_class is unknown or if the orbb shape is incorrect.
    """
    # Argument validation
    main_class = _parts_partition_map.get(partition_class, "Unknown")
    if main_class == "Unknown":
        raise ValueError(f"Unknown partition class: {partition_class}")

    height, width = image.shape[:2]
    x1, y1, x2, y2 = xywhn_to_xyxy(xywhn, (height, width))
    box = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])

    # Plot the rotated bbox on the image
    cv2.polylines(
        image,
        [box],
        isClosed=True,
        color=(255, 0, 0),
        thickness=2,
    )
    return image


def get_device(gpu_num: int = 0) -> tuple[torch.device, bool]:
    """
    Get the appropriate device (cuda, mps, cpu)

    Args:
        gpu_num (int): The GPU device number to use.

    Returns:
        tuple(torch.device, bool): The detected device and non_blocking flag.
    """

    if torch.cuda.is_available():
        device = torch.device(f"cuda:{gpu_num}")
        torch.backends.cudnn.benchmark = True  # Enable cudnn autotuner.
        torch.backends.cudnn.deterministic = False  # Disable deterministic mode.
        torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for matmul.
        torch.backends.cudnn.allow_tf32 = True  # Enable TF32 for convolution.
        torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = (
            True  # Enable FP16 reduced precision matmul.
        )
        torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = (
            True  # Enable BF16 reduced precision matmul.
        )
        torch.backends.cudnn.allow_fp16_reduced_precision_reduction = (
            True  # Enable FP16 reduced precision convolution.
        )
        return (device, True)
    elif torch.backends.mps.is_available():
        return (torch.device("mps"), False)
    else:
        return (torch.device("cpu"), False)


def clear_cache(gpu_type: str):
    """
    Clear cache based on the GPU type.

    Args:
        gpu_type (str): The type of GPU being used (e.g., "cuda", "mps").
    """
    if gpu_type == "mps":
        torch.mps.empty_cache()
    elif gpu_type == "cuda":
        torch.cuda.empty_cache()
        torch.compiler.reset()
    else:
        raise ValueError("Unsupported GPU type: {}".format(gpu_type))
    gc.collect()
