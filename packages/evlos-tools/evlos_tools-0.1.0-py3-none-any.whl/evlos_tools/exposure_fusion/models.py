"""
This script implements the OpenCV C++ Mertens exposure fusion algorithm for
GRAYSCALE images using PyTorch for GPU acceleration.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class MertensFusionGrayscaleApprox(nn.Module):
    """
    Implements the Mertens exposure fusion algorithm, optimized for PyTorch
    and ready for ONNX/TensorRT export. This version is specialized for
    GRAYSCALE images and uses a 3x3 Gaussian approximation kernel.

    Args:
        w_cont (float): Weight for the contrast metric. Defaults to 1.0.
        w_exp (float): Weight for the well-exposedness metric. Defaults to 1.0.
        n_levels (int): Number of levels in the Gaussian/Laplacian pyramids. Defaults to 5.
        sigma_exp (float): Standard deviation for the well-exposedness Gaussian curve. Defaults to 0.2.
    """

    def __init__(
        self,
        w_cont: float = 1.0,
        w_exp: float = 1.0,
        n_levels: int = 5,
        sigma_exp: float = 0.2,
    ):
        super().__init__()
        self.w_cont = w_cont
        self.w_exp = w_exp
        self.n_levels = n_levels
        self.sigma_exp = sigma_exp

        # Create a 3x3 binomial kernel for Gaussian approximation
        kernel = torch.tensor(
            [
                [1, 2, 1],
                [2, 4, 2],
                [1, 2, 1],
            ],
            dtype=torch.float32,
        )
        kernel = kernel / kernel.sum()  # Normalize by 16
        self.register_buffer("gaussian_kernel", kernel.view(1, 1, 3, 3))

        # Create a 3x3 Laplacian kernel and register it as a buffer
        laplacian_kernel = torch.tensor(
            [[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=torch.float32
        )
        self.register_buffer("laplacian_kernel", laplacian_kernel.view(1, 1, 3, 3))

    def forward(self, burst: torch.Tensor) -> torch.Tensor:
        """
        Performs exposure fusion on a burst of grayscale images.

        Args:
            burst (torch.Tensor): Input tensor of shape [N, 1, H, W].

        Returns:
            torch.Tensor: The [0-1] float32 fused image as a tensor of shape [1, 1, H, W].
        """

        contrast = self._compute_contrast(burst)
        exposedness = self._compute_well_exposedness(burst)

        weights = (contrast.pow(self.w_cont) * exposedness.pow(self.w_exp)) + 1e-12
        weights_sum = torch.sum(weights, dim=0, keepdim=True)
        weights = weights / weights_sum

        img_laplacian_pyramid = self._compute_laplacian_pyramid(burst, self.n_levels)
        weight_gaussian_pyramid = self._compute_gaussian_pyramid(weights, self.n_levels)

        fused_laplacian_pyramid = self._merge_laplacian_pyramid(
            img_laplacian_pyramid, weight_gaussian_pyramid
        )
        fused_image = self._collapse_pyramid(fused_laplacian_pyramid)

        return torch.clamp(fused_image, 0, 1).squeeze()

    def _compute_contrast(self, grayscale_burst: torch.Tensor) -> torch.Tensor:
        """Computes contrast using a Laplacian filter."""
        padded_gray = F.pad(grayscale_burst, (1, 1, 1, 1), mode="replicate")
        contrast = torch.abs(F.conv2d(padded_gray, self.laplacian_kernel))
        return contrast

    def _compute_well_exposedness(self, grayscale_burst: torch.Tensor) -> torch.Tensor:
        """Computes the well-exposedness metric using a Gaussian curve."""
        gauss_curve = torch.exp(
            -((grayscale_burst - 0.5) ** 2) / (2 * self.sigma_exp**2)
        )
        return gauss_curve

    def _compute_gaussian_pyramid(self, tensor: torch.Tensor, n_levels: int) -> list:
        """Builds a Gaussian pyramid for a grayscale tensor."""
        pyramid = [tensor]
        current = tensor
        for _ in range(n_levels - 1):
            padded = F.pad(current, (1, 1, 1, 1), mode="replicate")
            downsampled = F.conv2d(padded, self.gaussian_kernel, stride=2)
            pyramid.append(downsampled)
            current = downsampled
        return pyramid

    def _expand_stage(self, tensor: torch.Tensor, target_shape: tuple) -> torch.Tensor:
        """Upsamples a pyramid level using transposed convolution (pyrUp)."""
        n, c, h, w = tensor.shape
        target_h, target_w = target_shape

        kernel = self.gaussian_kernel * 4

        output_padding_h = target_h - (h * 2 - 1)
        output_padding_w = target_w - (w * 2 - 1)

        # REVISION: The padding argument is now 1 to match the 3x3 kernel.
        return F.conv_transpose2d(
            tensor,
            kernel,
            stride=2,
            padding=1,
            output_padding=(output_padding_h, output_padding_w),
        )

    def _compute_laplacian_pyramid(self, tensor: torch.Tensor, n_levels: int) -> list:
        """Builds a Laplacian pyramid."""
        gaussian_pyramid = self._compute_gaussian_pyramid(tensor, n_levels)
        laplacian_pyramid = []
        for i in range(n_levels - 1):
            fine_level = gaussian_pyramid[i]
            coarse_level = gaussian_pyramid[i + 1]
            _, _, th, tw = fine_level.shape
            upsampled = self._expand_stage(coarse_level, (th, tw))
            laplacian_pyramid.append(fine_level - upsampled)
        laplacian_pyramid.append(gaussian_pyramid[-1])
        return laplacian_pyramid

    def _merge_laplacian_pyramid(self, img_pyr: list, weight_pyr: list) -> list:
        """Blends Laplacian pyramids using Gaussian weights."""
        merged_pyramid = []
        for img_level, weight_level in zip(img_pyr, weight_pyr):
            fused_level = (weight_level * img_level).sum(dim=0, keepdim=True)
            merged_pyramid.append(fused_level)
        return merged_pyramid

    def _collapse_pyramid(self, laplacian_pyramid: list) -> torch.Tensor:
        """Reconstructs the image from a Laplacian pyramid."""
        current_level = laplacian_pyramid[-1]
        for i in range(len(laplacian_pyramid) - 2, -1, -1):
            laplacian_level = laplacian_pyramid[i]
            _, _, th, tw = laplacian_level.shape
            upsampled = self._expand_stage(current_level, (th, tw))
            current_level = upsampled + laplacian_level
        return current_level


"""
This script implements the OpenCV C++ Mertens exposure fusion algorithm for
GRAYSCALE images using PyTorch for GPU acceleration.
"""


class MertensFusionGrayscale(nn.Module):
    """
    Implements the Mertens exposure fusion algorithm, optimized for PyTorch
    and ready for ONNX/TensorRT export. This version is specialized for
    GRAYSCALE images and uses a 5x5 Gaussian kernel.

    Args:
        w_cont (float): Weight for the contrast metric. Defaults to 1.0.
        w_exp (float): Weight for the well-exposedness metric. Defaults to 1.0.
        n_levels (int): Number of levels in the Gaussian/Laplacian pyramids. Defaults to 5.
        sigma_exp (float): Standard deviation for the well-exposedness Gaussian curve. Defaults to 0.2.
    """

    def __init__(
        self,
        w_cont: float = 1.0,
        w_exp: float = 1.0,
        n_levels: int = 5,
        sigma_exp: float = 0.2,
    ):
        super().__init__()
        self.w_cont = w_cont
        self.w_exp = w_exp
        self.n_levels = n_levels
        self.sigma_exp = sigma_exp

        # Create a 5x5 Gaussian kernel and register it as a buffer
        kernel = torch.tensor(
            [
                [1, 4, 7, 4, 1],
                [4, 16, 26, 16, 4],
                [7, 26, 41, 26, 7],
                [4, 16, 26, 16, 4],
                [1, 4, 7, 4, 1],
            ],
            dtype=torch.float32,
        )
        kernel = kernel / kernel.sum()
        self.register_buffer("gaussian_kernel", kernel.view(1, 1, 5, 5))

        # Create a 3x3 Laplacian kernel and register it as a buffer
        laplacian_kernel = torch.tensor(
            [[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=torch.float32
        )
        self.register_buffer("laplacian_kernel", laplacian_kernel.view(1, 1, 3, 3))

    def forward(self, burst: torch.Tensor) -> torch.Tensor:
        """
        Performs exposure fusion on a burst of grayscale images.

        Args:
            burst (torch.Tensor): Input tensor of shape [N, 1, H, W].

        Returns:
            torch.Tensor: The fused image as a tensor of shape [1, 1, H, W].
        """

        contrast = self._compute_contrast(burst)
        exposedness = self._compute_well_exposedness(burst)

        weights = (contrast.pow(self.w_cont) * exposedness.pow(self.w_exp)) + 1e-12
        weights_sum = torch.sum(weights, dim=0, keepdim=True)
        weights = weights / weights_sum

        img_laplacian_pyramid = self._compute_laplacian_pyramid(burst, self.n_levels)
        weight_gaussian_pyramid = self._compute_gaussian_pyramid(weights, self.n_levels)

        fused_laplacian_pyramid = self._merge_laplacian_pyramid(
            img_laplacian_pyramid, weight_gaussian_pyramid
        )
        fused_image = self._collapse_pyramid(fused_laplacian_pyramid)

        return torch.clamp(fused_image, 0, 1)

    def _compute_contrast(self, grayscale_burst: torch.Tensor) -> torch.Tensor:
        """Computes contrast using a Laplacian filter."""
        padded_gray = F.pad(grayscale_burst, (1, 1, 1, 1), mode="replicate")
        contrast = torch.abs(F.conv2d(padded_gray, self.laplacian_kernel))
        return contrast

    def _compute_well_exposedness(self, grayscale_burst: torch.Tensor) -> torch.Tensor:
        """Computes the well-exposedness metric using a Gaussian curve."""
        gauss_curve = torch.exp(
            -((grayscale_burst - 0.5) ** 2) / (2 * self.sigma_exp**2)
        )
        return gauss_curve

    def _compute_gaussian_pyramid(self, tensor: torch.Tensor, n_levels: int) -> list:
        """Builds a Gaussian pyramid for a grayscale tensor."""
        pyramid = [tensor]
        current = tensor
        for _ in range(n_levels - 1):
            padded = F.pad(current, (2, 2, 2, 2), mode="replicate")
            downsampled = F.conv2d(padded, self.gaussian_kernel, stride=2)
            pyramid.append(downsampled)
            current = downsampled
        return pyramid

    def _expand_stage(self, tensor: torch.Tensor, target_shape: tuple) -> torch.Tensor:
        """Upsamples a pyramid level using transposed convolution (pyrUp)."""
        n, c, h, w = tensor.shape
        target_h, target_w = target_shape

        kernel = self.gaussian_kernel * 4

        output_padding_h = target_h - (h * 2 - 1)
        output_padding_w = target_w - (w * 2 - 1)

        # REVISION: The padding argument is now 2 to match the 5x5 kernel.
        return F.conv_transpose2d(
            tensor,
            kernel,
            stride=2,
            padding=2,
            output_padding=(output_padding_h, output_padding_w),
        )

    def _compute_laplacian_pyramid(self, tensor: torch.Tensor, n_levels: int) -> list:
        """Builds a Laplacian pyramid."""
        gaussian_pyramid = self._compute_gaussian_pyramid(tensor, n_levels)
        laplacian_pyramid = []
        for i in range(n_levels - 1):
            fine_level = gaussian_pyramid[i]
            coarse_level = gaussian_pyramid[i + 1]
            _, _, th, tw = fine_level.shape
            upsampled = self._expand_stage(coarse_level, (th, tw))
            laplacian_pyramid.append(fine_level - upsampled)
        laplacian_pyramid.append(gaussian_pyramid[-1])
        return laplacian_pyramid

    def _merge_laplacian_pyramid(self, img_pyr: list, weight_pyr: list) -> list:
        """Blends Laplacian pyramids using Gaussian weights."""
        merged_pyramid = []
        for img_level, weight_level in zip(img_pyr, weight_pyr):
            fused_level = (weight_level * img_level).sum(dim=0, keepdim=True)
            merged_pyramid.append(fused_level)
        return merged_pyramid

    def _collapse_pyramid(self, laplacian_pyramid: list) -> torch.Tensor:
        """Reconstructs the image from a Laplacian pyramid."""
        current_level = laplacian_pyramid[-1]
        for i in range(len(laplacian_pyramid) - 2, -1, -1):
            laplacian_level = laplacian_pyramid[i]
            _, _, th, tw = laplacian_level.shape
            upsampled = self._expand_stage(current_level, (th, tw))
            current_level = upsampled + laplacian_level
        return current_level
