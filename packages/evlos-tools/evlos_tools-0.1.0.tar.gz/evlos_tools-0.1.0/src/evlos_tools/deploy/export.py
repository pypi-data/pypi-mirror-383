import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import tensorrt as trt
import onnx
import numpy as np


def _dtype_convert(str_dtype: str):
    """
    Converts a string representation of a data type to the corresponding PyTorch and TensorRT data types.
    Args:
        str_dtype (str): The string representation of the data type (e.g., "float32", "int64").
    Returns:
        tuple: A tuple containing the PyTorch dtype and TensorRT dtype.
    Raises:
        ValueError: If the provided string does not correspond to a supported data type.
    """
    dtype_mappings = {
        "float32": (torch.float32, trt.float32),
        "float16": (torch.float16, trt.float16),
        "int32": (torch.int32, trt.int32),
        # "int64": (torch.int64, trt.int32),  # Note: TensorRT does not support int64
        "uint8": (torch.uint8, trt.uint8),
        "int8": (torch.int8, trt.int8),
        "bool": (torch.bool, trt.bool),
    }

    if str_dtype not in dtype_mappings:
        raise ValueError(f"Unsupported data type: {str_dtype}")

    return dtype_mappings[str_dtype]


def build_onnx(model: nn.Module, deploy_dict: dict):
    """
    Exports the given PyTorch model to ONNX format.
    Args:
        model (nn.Module): The PyTorch model to export.
        burst_input (torch.Tensor): A sample input tensor for the model.
    Returns:
        str: The path to the saved ONNX model.
    Raises:
        ValueError: If input names, shapes, or dtypes are missing in deploy_dict.
    """
    input_tensors = []
    for input_name in deploy_dict["model"]["input_names"]:
        if input_name not in deploy_dict["model"]["input_shapes"]:
            raise ValueError(f"Missing shape for input: {input_name}")
        if input_name not in deploy_dict["model"]["input_dtypes"]:
            raise ValueError(f"Missing dtype for input: {input_name}")
        input_tensor = torch.randn(deploy_dict["model"]["input_shapes"][input_name]).to(
            _dtype_convert(deploy_dict["model"]["input_dtypes"][input_name])[0]
        )
        input_tensors.append(input_tensor)

    if not os.path.exists(deploy_dict["deploy"]["onnx"]["onnx_save_dir"]):
        os.makedirs(deploy_dict["deploy"]["onnx"]["onnx_save_dir"])
        print(
            f"Created ONNX model directory: {deploy_dict['deploy']['onnx']['onnx_save_dir']}"
        )

    onnx_path = f"{deploy_dict['deploy']['onnx']['onnx_save_dir']}/{deploy_dict['model']['type']}_ov{deploy_dict['deploy']['onnx']['opset_version']}.onnx"

    model.eval()
    torch.onnx.export(
        model,
        input_tensors if len(input_tensors) > 1 else input_tensors[0],
        onnx_path,
        input_names=deploy_dict["model"]["input_names"],
        output_names=deploy_dict["model"]["output_names"],
        opset_version=deploy_dict["deploy"]["onnx"]["opset_version"],
        do_constant_folding=True,
        # dynamic_axes={
        #     'burst_input': {0: 'num_images', 2: 'height', 3: 'width'},
        #     'fused_output': {2: 'height', 3: 'width'}
        # }
    )

    return onnx_path


# def set_profile_shapes(profile, network, cfg):
#     for name, rng in cfg.items():
#         print("Setting profile for:", name, rng)
#         # t = network.get_input(0)  # placeholder
#         # Find tensor by name
#         for i in range(network.num_inputs):
#             if network.get_input(i).name == name:
#                 t = network.get_input(i)
#                 print(t.name, t.shape, t.is_shape_tensor)
#                 break
#         # Is it a shape input?
#         if t.is_shape_tensor or name in ["images", "keypoints"]:
#             print(f"Setting shape input for: {t.name}")
#             # For shape inputs, values are 1D shapes (e.g., (1,), (2048,))
#             profile.set_shape_input(
#                 t.name,
#                 np.array(rng["min"], dtype=np.int32),
#                 np.array(rng["opt"], dtype=np.int32),
#                 np.array(rng["max"], dtype=np.int32),
#             )
#         else:
#             profile.set_shape(t.name, rng["min"], rng["opt"], rng["max"])


def build_engine(
    onnx_model_path: str,
    config: dict,
    logger,
):
    """
    Builds a TensorRT engine from an ONNX model and saves it to a file.
    Args:
        onnx_model_path (str): Path to the ONNX model file.
        config (dict): Configuration dictionary containing paths and settings.
        logger: TensorRT logger instance.
    Returns:
        str: Path to the saved TensorRT engine file.
    Raises:
        RuntimeError: If the ONNX model cannot be parsed.
    """
    compile_mode = config["deploy"]["trt"]["compile_mode"]
    serialized_engine_path = os.path.join(
        config["deploy"]["trt"]["trt_save_dir"],
        f"{config['model']['type']}_ov{config['deploy']['onnx']['opset_version']}_{compile_mode}.engine",
    )

    if not os.path.exists(config["deploy"]["trt"]["trt_save_dir"]):
        os.makedirs(config["deploy"]["trt"]["trt_save_dir"])
        print(
            f"Created TensorRT model directory: {config['deploy']['trt']['trt_save_dir']}"
        )

    if compile_mode == "quick_compile":
        builder_optimization_level = 0
        tiling_optimization_level = trt.TilingOptimizationLevel.NONE
    elif compile_mode == "quick_inference":
        builder_optimization_level = 5
        tiling_optimization_level = trt.TilingOptimizationLevel.FULL
    else:
        raise ValueError(f"Unknown compile_mode: {compile_mode}")

    with (
        trt.Builder(logger) as builder,
        builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        ) as network,
        trt.OnnxParser(network, logger) as parser,
        builder.create_builder_config() as config,
    ):
        # Set cache
        cache = config.create_timing_cache(b"")
        config.set_timing_cache(cache, ignore_mismatch=False)
        # builder.max_batch_size = 1  # ignored with explicit batch; harmless
        # config.set_memory_pool_limit(
        #     trt.MemoryPoolType.WORKSPACE, 2 << 30
        # )  # 2GB workspace; tune as needed
        config.builder_optimization_level = builder_optimization_level
        config.profiling_verbosity = trt.ProfilingVerbosity.DETAILED
        config.tiling_optimization_level = tiling_optimization_level

        with open(onnx_model_path, "rb") as f:
            if not parser.parse(f.read()):
                for i in range(parser.num_errors):
                    print(parser.get_error(i))
                raise RuntimeError("Failed to parse ONNX")
        inputs = [network.get_input(i) for i in range(network.num_inputs)]
        outputs = [network.get_output(i) for i in range(network.num_outputs)]
        for input in inputs:
            print(f"Model {input.name} shape: {input.shape} {input.dtype}")
        for output in outputs:
            print(f"Model {output.name} shape: {output.shape} {output.dtype}")

        # Create optimization profiles
        # prof0 = builder.create_optimization_profile()
        # # set_profile_shapes(prof0, network, P0)
        # for name, rng in P0.items():
        #     # if name in ["images", "keypoints", "matches", "mscores"]:
        #     #     print(f"Setting shape input for: {name}")
        #     #     prof0.set_shape(
        #     #         name,
        #     #         np.array(rng["min"], dtype=np.int32),
        #     #         np.array(rng["opt"], dtype=np.int32),
        #     #         np.array(rng["max"], dtype=np.int32),
        #     #     )
        #     # else:
        #     print(f"Setting profile for: {name} {rng}")
        #     prof0.set_shape(name, rng["min"], rng["opt"], rng["max"])
        # config.add_optimization_profile(prof0)

        # prof1 = builder.create_optimization_profile()
        # set_profile_shapes(prof1, network, P1)
        # config.add_optimization_profile(prof1)

        # config.set_flag(trt.BuilderFlag.FP16)
        config.set_flag(trt.BuilderFlag.BF16)
        config.set_flag(trt.BuilderFlag.TF32)

        strip_weights = False
        if strip_weights:
            config.set_flag(trt.BuilderFlag.STRIP_PLAN)

        # To remove strip plan from config
        # config.flags &= ~(1 << int(trt.BuilderFlag.STRIP_PLAN))

        engine_bytes = builder.build_serialized_network(network, config)
        assert engine_bytes, "Engine build failed."
        with open(serialized_engine_path, "wb") as f:
            f.write(engine_bytes)
        print("Wrote:", serialized_engine_path)
    return serialized_engine_path


if __name__ == "__main__":
    ONNX_MODEL = "deployment/resources/checkpoints/mertens_fusion_approx_grayscale_f32_lvl10_15k_sanitize.onnx"

    # fusion_model = MertensFusionGrayscaleApprox(n_levels=10)
    # print("MertensFusionGrayscale model instantiated.")

    # dummy_burst = torch.randn(4, 1, 15_000, 4096, dtype=torch.float32)
    # build_onnx(fusion_model, dummy_burst, ONNX_FILE_PATH)

    SERIALIZED_ENGINE = "deployment/resources/checkpoints/mertens_fusion_approx_grayscale_f32_lvl10_15k_sanitize_trt13.trt"

    # ONNX_MODEL = (
    #     "/home/evlos/evlos/aliked-tensorrt/converted_model/aliked-n16rot-top1k-tum_sanitize.onnx"
    # )
    # SERIALIZED_ENGINE = (
    #     "/home/evlos/evlos/aliked-tensorrt/converted_model/aliked-n16rot-top1k-tum_sanitize.trt"
    # )
    LOGGER = trt.Logger(trt.Logger.INFO)

    # ---- Define your ranges ----
    # P0 = {
    #     # "images": {
    #     #     "min": (2, 3, 384, 1024),
    #     #     "opt": (2, 3, 384, 1024),
    #     #     "max": (2, 3, 384, 1024),
    #     # },
    #     # "keypoints": {"min": (2, 2048, 2), "opt": (2, 2048, 2), "max": (2, 2048, 2)},
    #     "matches": {"min": (1, 3), "opt": (384, 3), "max": (1024, 3)},
    #     "mscores": {"min": (1,), "opt": (384,), "max": (1024,)},
    # }

    build_engine()
