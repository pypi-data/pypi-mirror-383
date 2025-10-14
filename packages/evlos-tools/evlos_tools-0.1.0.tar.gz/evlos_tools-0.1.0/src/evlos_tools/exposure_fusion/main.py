import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import os
import numpy as np
import yaml
import torch
import tensorrt as trt
import onnxruntime as ort
from loguru import logger

from exposure_fusion.models import MertensFusionGrayscale, MertensFusionGrayscaleApprox
from exposure_fusion.utils import deinterleave_image, preprocess
from deploy.export import build_onnx, build_engine
from deploy.tensorrt_async import TensorRTInferAsync

with open("src/exposure_fusion/configs/exposure_fusion.yaml", "r") as f:
    config = yaml.safe_load(f)

if __name__ == "__main__":
    # --- Parameters ---
    EXPOSURE_TIMES = config["model"]["exposure_times"]

    # --- Pytorch Model Initialization ---
    model = MertensFusionGrayscale(
        w_cont=config["model"]["contrast_weight"],
        w_exp=config["model"]["exposure_weight"],
        n_levels=config["model"]["n_levels"],
        sigma_exp=config["model"]["exposure_sigma"],
    ).eval()

    # ---Directory Setup---
    INTERLEAVED_IMAGE_PATH = "src/exposure_fusion/data/00_input_interleaved.bmp"

    # --- Generate and Process Data ---
    logger.info("Deinterleaving data (UINT8)...")
    interleaved_image = cv2.imread(
        INTERLEAVED_IMAGE_PATH,
        cv2.IMREAD_UNCHANGED,
    )
    exposures = deinterleave_image(interleaved_image, len(EXPOSURE_TIMES))
    logger.debug(
        f"Shapes of deinterleaved exposures: {[img.shape for img in exposures]}"
    )

    # --- Pytorch Inference ---
    burst_images = preprocess(exposures)
    logger.debug(
        f"Input shape for PyTorch: {burst_images.shape}, dtype: {burst_images.dtype}"
    )
    with torch.no_grad():
        fused_image = model(torch.from_numpy(burst_images))

    # --- Build ONNX IR---
    onnx_model_path = build_onnx(model, config)

    # --- ONNX Inference ---
    available_providers = ort.get_available_providers()
    logger.info(f"Available ONNX Runtime providers: {available_providers}")
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if "CUDAExecutionProvider" in available_providers
        else ["CPUExecutionProvider"]
    )
    ort_session = ort.InferenceSession(onnx_model_path, providers=providers)
    ort_inputs = {ort_session.get_inputs()[0].name: burst_images}
    ort_outputs = ort_session.run(None, ort_inputs)
    fused_image_onnx = ort_outputs[0]
    logger.info(
        f"Output 'fused_image' from ONNX has shape: {fused_image_onnx.shape}, dtype: {fused_image_onnx.dtype}"
    )
    del ort_session  # Free cuda lock for TensorRT check

    # --- Build TensorRT Engine ---
    LOGGER = trt.Logger(trt.Logger.INFO)

    tensorrt_model_path = build_engine(onnx_model_path, config, LOGGER)

    # --- TensorRT Inference ---
    trt_infer = TensorRTInferAsync(tensorrt_model_path)
    input_name = trt_infer.inputs[0].name
    input_shape = trt_infer.inputs[0].shape
    input_trt_dtype = trt_infer.inputs[0].trt_dtype
    burst_images = preprocess(exposures)
    logger.info(
        f"Model expects input '{input_name}' with shape: {input_shape}, TRT type: {input_trt_dtype}"
    )

    trt_infer.check_input(0, burst_images)
    input_feed = {input_name: burst_images}
    trt_infer.infer_async(input_feed)
    output_results = trt_infer.get_async_results()

    # --- Postprocess ---
    fused_image = output_results["fused_image"]
    logger.info(
        f"Output 'fused_image' from TensorRT has shape: {fused_image.shape}, dtype: {fused_image.dtype}"
    )
    fused_image_8bit = (fused_image * 255.0).astype(np.uint8)  # For visualization

    # --- Inference finished and closing ---
    trt_infer.destroy()
