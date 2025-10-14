# Exposure Fusion

## Mertens Fusion
This script implements the OpenCV C++ Mertens exposure fusion algorithm for
GRAYSCALE images using PyTorch for GPU acceleration.

It includes two versions of the algorithm:
1. MertensFusionGrayscale: Uses a 5x5 Gaussian kernel for better quality.
2. MertensFusionGrayscaleApprox: Uses a 3x3 Gaussian kernel for faster performance.

Both models are designed to be exportable to ONNX and TensorRT for efficient
inference on NVIDIA GPUs.

The models take a burst of grayscale images `[N, 1, H, W] (N=number of images)` as input and 
produce a single fused image as `[1, 1, H, W] (float32 [0-1])` output.
