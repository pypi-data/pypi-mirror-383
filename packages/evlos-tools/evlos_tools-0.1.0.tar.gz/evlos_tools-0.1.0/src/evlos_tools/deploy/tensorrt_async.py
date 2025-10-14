import tensorrt as trt
import numpy as np
import pycuda.driver as cuda
import os
import time
import warnings
import torch


# --- bfloat16 Conversion Helpers ---
def float32_to_bfloat16_numpy(data: np.ndarray) -> np.ndarray:
    """Converts a float32 numpy array to a bfloat16 numpy array (as uint16)."""
    int_data = data.view(np.uint32)
    return (int_data >> 16).astype(np.uint16)


def bfloat16_to_float32_numpy(data: np.ndarray) -> np.ndarray:
    """Converts a bfloat16 numpy array (as uint16) to a float32 numpy array."""
    int_data = data.astype(np.uint32) << 16
    return int_data.view(np.float32)


class TensorRTInferAsync:
    """
    Manages asynchronous inference using set_tensor_address and execute_async_v3.
    """

    class EngineIO:
        """Helper class to manage engine IO details."""

        def __init__(self, host_mem, device_mem, name, shape, np_dtype, trt_dtype):
            self.host, self.device, self.name, self.shape = (
                host_mem,
                device_mem,
                name,
                shape,
            )
            self.np_dtype, self.trt_dtype = np_dtype, trt_dtype
            self.converted_host_buffer = None

    def __init__(self, engine_path: str):
        cuda.init()
        self.cuda_driver_context = cuda.Device(0).make_context()
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.engine = self._load_engine(engine_path)
        assert self.engine, "Failed to load the TensorRT engine."
        self.context = self.engine.create_execution_context()
        assert self.context, "Failed to create execution context."
        self.inputs, self.outputs, self.np_dtype = self._allocate_buffers()
        self._set_tensor_addresses()
        self.stream = cuda.Stream()

    def _load_engine(self, engine_path: str):
        if not os.path.exists(engine_path):
            raise FileNotFoundError(f"Engine file not found: {engine_path}")
        with open(engine_path, "rb") as f, trt.Runtime(self.logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())

    def _allocate_buffers(self):
        """
        Allocates host and device buffers.
        """
        inputs, outputs = [], []
        for i in range(self.engine.num_io_tensors):
            name = self.engine.get_tensor_name(i)
            shape = self.engine.get_tensor_shape(name)
            trt_dtype = self.engine.get_tensor_dtype(name)
            try:
                np_dtype = trt.nptype(trt_dtype)
            except Exception as e:
                warnings.warn(
                    f"Unsupported TRT data type {trt_dtype} for tensor '{name}': {e} Defaulting to uint16."
                )
                if trt_dtype == trt.DataType.BF16:
                    np_dtype = np.uint16
            print(
                f"Allocating buffer for tensor '{name}' with TRT type {trt_dtype} and NumPy type {np_dtype}"
            )
            volume = trt.volume(shape)
            size = volume * np.dtype(np_dtype).itemsize
            host_mem = cuda.pagelocked_empty(volume, np_dtype)
            device_mem = cuda.mem_alloc(size)

            io = self.EngineIO(host_mem, device_mem, name, shape, np_dtype, trt_dtype)
            (
                inputs
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT
                else outputs
            ).append(io)
        return inputs, outputs, np_dtype

    def _set_tensor_addresses(self):
        """
        Sets the device memory addresses for all I/O tensors in the context.
        This is a prerequisite for using execute_async_v3.
        """
        for io_buffer in self.inputs + self.outputs:
            self.context.set_tensor_address(io_buffer.name, io_buffer.device)

    def infer_async(self, input_data: dict):
        self.cuda_driver_context.push()
        # 1. Perform conversions and copy inputs H->D asynchronously
        for inp in self.inputs:
            data = input_data[inp.name]
            if inp.trt_dtype == trt.DataType.BF16:
                if data.dtype != np.float32:
                    data = data.astype(np.float32)
                inp.converted_host_buffer = float32_to_bfloat16_numpy(data)
                np.copyto(inp.host, inp.converted_host_buffer.ravel())
            else:
                np.copyto(inp.host, data.astype(inp.np_dtype).ravel())

            cuda.memcpy_htod_async(inp.device, inp.host, self.stream)

        # 2. Run inference. execute_async_v3 doesn't need the bindings list.
        self.context.execute_async_v3(stream_handle=self.stream.handle)

        # 3. Copy outputs D->H asynchronously
        for out in self.outputs:
            cuda.memcpy_dtoh_async(out.host, out.device, self.stream)

    def get_async_results(self):
        self.stream.synchronize()
        results = {}
        for i, out in enumerate(self.outputs):
            host_buffer = out.host.reshape(out.shape)
            if out.trt_dtype == trt.DataType.BF16:
                results[out.name] = bfloat16_to_float32_numpy(host_buffer)
            else:
                results[out.name] = host_buffer
        self.cuda_driver_context.pop()
        return results

    def check_input(self, input_index: int, input_data: torch.Tensor):
        """
        Health check for input data shape and dtype.

        Args:
            input_index (int): Index of the input tensor to check.
            input_data (torch.Tensor): Input data tensor.

        Raises:
            ValueError: If there is a mismatch in shape or dtype.
        """
        name = self.engine.get_tensor_name(input_index)
        shape = self.engine.get_tensor_shape(name)

        if shape != input_data.shape:
            raise ValueError(
                f"Input shape mismatch for '{name}': expected {shape}, got {input_data.shape}"
            )
        if self.np_dtype == np.uint16 and input_data.dtype != np.float32:
            raise ValueError(
                f"Input dtype mismatch for '{name}': expected float32 for BF16 input, got {input_data.dtype}"
            )
        elif input_data.dtype != self.np_dtype and self.np_dtype != np.uint16:
            raise ValueError(
                f"Input dtype mismatch for '{name}': expected {self.np_dtype}, got {input_data.dtype}"
            )

    def destroy(self):
        self.cuda_driver_context.pop()


if __name__ == "__main__":
    time_start = time.perf_counter()
    # ENGINE_FILE = "deployment/resources/checkpoints/mertens_fusion_approx_grayscale_f32_lvl10_15k_trt9.trt"
    ENGINE_FILE = (
        "/home/evlos/evlos/LightGlue-ONNX/weights/disk_lightglue_pipeline_1.trt"
    )

    if not os.path.exists(ENGINE_FILE):
        print(f"Error: Engine file not found at '{ENGINE_FILE}'.")
    else:
        trt_infer = TensorRTInferAsync(ENGINE_FILE)
        input_name = trt_infer.inputs[0].name
        input_shape = trt_infer.inputs[0].shape
        input_trt_dtype = trt_infer.inputs[0].trt_dtype
        print(
            f"Model expects input '{input_name}' with shape: {input_shape}, TRT type: {input_trt_dtype}"
        )
        print("\nRunning ASYNC inference...")
        dummy_input = np.random.rand(*input_shape)
        for i in range(10):
            dummy_input = dummy_input.astype(np.float32)
            try:
                output_results = trt_infer.get_async_results()
            except:
                output_results = trt_infer.get_async_results()
            input_feed = {input_name: dummy_input}
            trt_infer.infer_async(input_feed)
        trt_infer.destroy()
        print("\n--- Async Inference Results ---")
        for name, array in output_results.items():
            print(f"Output Name: {name}, Shape: {array.shape}, Dtype: {array.dtype}")
            if name == "matches":
                print(f"Sample matches data (first 10 elements): {array.ravel()[:10]}")

    time_end = time.perf_counter()
    print(f"\nTime taken: {(time_end - time_start) / 100} seconds")
