import numpy as np
import torch
import torch.nn.functional as F
from scipy.ndimage import center_of_mass, gaussian_filter, shift
from scipy.stats import norm
from tqdm.auto import tqdm

from quantem.core.utils.imaging_utils import cross_correlation_shift

# --- Projection Operator Utils ---


def rot_ZXZ(mags, z1, x, z3, device, mode="bilinear"):
    if not isinstance(x, torch.Tensor) or not isinstance(z1, torch.Tensor):
        z1 = torch.tensor(z1, dtype=torch.float32, device=device)
        x = torch.tensor(x, dtype=torch.float32, device=device)
        z3 = torch.tensor(z3, dtype=torch.float32, device=device)
    curr_mags = mags

    curr_mags = differentiable_rotz_vectorized(curr_mags, z1, mode)
    curr_mags = differentiable_rotx_vectorized(curr_mags, x, mode)

    curr_mags = differentiable_rotz_vectorized(curr_mags, z3, mode)

    return curr_mags


def differentiable_rotz_vectorized(mags, theta, mode="bilinear"):
    _, dimz, dimy, dimx = mags.shape

    if theta.dim() == 0:
        theta = theta.unsqueeze(0)

    theta_rad = torch.deg2rad(theta)

    cos_t, sin_t = torch.cos(theta_rad), torch.sin(theta_rad)
    affine_matrix = torch.stack(
        [cos_t, -sin_t, torch.zeros_like(theta), sin_t, cos_t, torch.zeros_like(theta)], dim=-1
    ).view(-1, 2, 3)

    mags = mags.permute(1, 0, 2, 3)

    def transform_slice(mag_slice):
        grid = F.affine_grid(affine_matrix, mag_slice.unsqueeze(0).shape, align_corners=False)
        return F.grid_sample(mag_slice.unsqueeze(0), grid, mode=mode, align_corners=False).squeeze(
            0
        )

    rotated_mags = torch.vmap(transform_slice)(mags)
    return rotated_mags.permute(1, 0, 2, 3)


def differentiable_rotx_vectorized(mags, theta, mode="bilinear"):
    _, dimz, dimy, dimx = mags.shape

    if theta.dim() == 0:
        theta = theta.unsqueeze(0)

    theta_rad = torch.deg2rad(theta)

    cos_t, sin_t = torch.cos(theta_rad), torch.sin(theta_rad)
    affine_matrix = torch.stack(
        [cos_t, -sin_t, torch.zeros_like(theta), sin_t, cos_t, torch.zeros_like(theta)], dim=-1
    ).view(-1, 2, 3)

    mags = mags.permute(3, 0, 1, 2)

    def transform_slice(mag_slice):
        grid = F.affine_grid(affine_matrix, mag_slice.unsqueeze(0).shape, align_corners=False)
        return F.grid_sample(mag_slice.unsqueeze(0), grid, mode=mode, align_corners=False).squeeze(
            0
        )

    rotated_mags = torch.vmap(transform_slice)(mags)
    return rotated_mags.permute(1, 2, 3, 0)


def differentiable_shift_2d(image, shift_x, shift_y, sampling_rate):
    """
    Shifts a 2D image using grid_sample in a differentiable manner.

    Args:
        image: Tensor of shape [H, W]
        shift_x: Scalar tensor (dx) for shift in x-direction (in physical units)
        shift_y: Scalar tensor (dy) for shift in y-direction (in physical units)
        sampling_rate: Scalar value (physical units per pixel) to correctly normalize shifts

    Returns:
        Shifted image of shape [H, W]
    """
    H, W = image.shape

    # Convert physical shift to pixel shift
    shift_x_pixel = shift_x
    shift_y_pixel = shift_y

    # Normalize shift for grid_sample (assuming align_corners=True)
    normalized_shift_x = shift_x_pixel * 2 / (W - 1)
    normalized_shift_y = shift_y_pixel * 2 / (H - 1)

    # Create normalized grid
    grid_y, grid_x = torch.meshgrid(
        torch.linspace(-1, 1, H, device=image.device),
        torch.linspace(-1, 1, W, device=image.device),
        indexing="ij",
    )

    grid = torch.stack((grid_x, grid_y), dim=-1).unsqueeze(0)  # [1, H, W, 2]

    # Apply shift (ensure it's differentiable)
    grid[:, :, :, 0] -= normalized_shift_x
    grid[:, :, :, 1] -= normalized_shift_y

    # Add batch and channel dimensions
    image = image.unsqueeze(0).unsqueeze(0)  # [1, 1, H, W]

    # Sample using grid_sample (fully differentiable)
    shifted_image = F.grid_sample(
        image, grid, mode="bicubic", padding_mode="zeros", align_corners=True
    )

    return shifted_image.squeeze(0).squeeze(0)  # Back to [H, W]


# --- TV loss ---


def get_TV_loss(tensor, factor=1e-3):
    tv_d = torch.pow(tensor[:, :, 1:, :, :] - tensor[:, :, :-1, :, :], 2).sum()
    tv_h = torch.pow(tensor[:, :, :, 1:, :] - tensor[:, :, :, :-1, :], 2).sum()
    tv_w = torch.pow(tensor[:, :, :, :, 1:] - tensor[:, :, :, :, :-1], 2).sum()
    tv_loss = tv_d + tv_h + tv_w

    return tv_loss * factor / (torch.prod(torch.tensor(tensor.shape)))


# --- Gaussian filters ---


def gaussian_kernel_1d(sigma: float, num_sigmas: float = 3.0) -> torch.Tensor:
    radius = np.ceil(num_sigmas * sigma)
    support = torch.arange(-radius, radius + 1, dtype=torch.float)
    kernel = torch.distributions.Normal(loc=0, scale=sigma).log_prob(support).exp_()
    # Ensure kernel weights sum to 1, so that image brightness is not altered
    return kernel.mul_(1 / kernel.sum())


def gaussian_filter_2d(
    img: torch.Tensor, sigma: float, kernel_1d: torch.Tensor
) -> torch.Tensor:  # Add kernel_1d as an argument
    # kernel_1d = gaussian_kernel_1d(sigma)  # Create 1D Gaussian kernel - Moved outside function
    padding = len(kernel_1d) // 2  # Ensure that image size does not change
    img = img.unsqueeze(0).unsqueeze_(0)  # Make copy, make 4D for ``conv2d()``
    # Convolve along columns and rows
    img = torch.nn.functional.conv2d(img, weight=kernel_1d.view(1, 1, -1, 1), padding=(padding, 0))
    img = torch.nn.functional.conv2d(img, weight=kernel_1d.view(1, 1, 1, -1), padding=(0, padding))
    return img.squeeze_(0).squeeze_(0)  # Make 2D again


def gaussian_filter_2d_stack(stack: torch.Tensor, kernel_1d: torch.Tensor) -> torch.Tensor:
    """
    Apply 2D Gaussian blur to each slice stack[:, i, :] in a vectorized way.

    Args:
        stack (torch.Tensor): Tensor of shape (H, N, W) where N is num_sinograms
        kernel_1d (torch.Tensor): 1D Gaussian kernel

    Returns:
        torch.Tensor: Blurred stack of same shape (H, N, W)
    """
    H, N, W = stack.shape
    padding = len(kernel_1d) // 2

    # Reshape to (N, 1, H, W) for conv2d
    stack_reshaped = stack.permute(1, 0, 2).unsqueeze(1)  # (N, 1, H, W)

    # Apply separable conv2d: vertical then horizontal
    out = torch.nn.functional.conv2d(
        stack_reshaped, kernel_1d.view(1, 1, -1, 1), padding=(padding, 0)
    )
    out = torch.nn.functional.conv2d(out, kernel_1d.view(1, 1, 1, -1), padding=(0, padding))

    # Restore shape to (H, N, W)
    return out.squeeze(1).permute(1, 0, 2)


# Circular mask


def torch_phase_cross_correlation(im1, im2):
    f1 = torch.fft.fft2(im1)
    f2 = torch.fft.fft2(im2)
    cc = torch.fft.ifft2(f1 * torch.conj(f2))
    cc_abs = torch.abs(cc)

    max_idx = torch.argmax(cc_abs)
    shifts = torch.tensor(np.unravel_index(max_idx.item(), im1.shape), device=im1.device).float()

    for i, dim in enumerate(im1.shape):
        if shifts[i] > dim // 2:
            shifts[i] -= dim

    # return shifts.flip(0)  # (dx, dy)
    return shifts


# --- Tilt Series Processing Utility Functions ---


def fourier_cropping(img, crop_size):
    """
    Crop the img in Fourier space to the specified size.
    """
    center = np.array(img.shape) // 2

    fft_img = np.fft.fftshift(np.fft.fft2(img))

    cropped_fft = fft_img[
        center[0] - crop_size[0] // 2 : center[0] + crop_size[0] // 2,
        center[1] - crop_size[1] // 2 : center[1] + crop_size[1] // 2,
    ]
    cropped_img = np.fft.ifft2(np.fft.ifftshift(cropped_fft)).real
    return cropped_img


def estimate_background(
    img,
    num_iterations=10,
    cutoff=3,
    smoothing_sigma=1.0,
):
    """
    Estimate the background of the image using a Gaussian filter.
    """
    if smoothing_sigma > 0:
        img = gaussian_filter(img, sigma=smoothing_sigma)
    pixel_vals = img.ravel()

    for i in range(num_iterations):
        mu, std = norm.fit(pixel_vals)

        # Set cutoff threshold (e.g., 3 standard deviations)
        lower = mu - cutoff * std
        upper = mu + cutoff * std

        # Mask pixel values within ±3σ
        pixel_vals = pixel_vals[(pixel_vals >= lower) & (pixel_vals <= upper)]

    return mu


def cross_correlation_align_stack(ref_img, stack):
    """
    Aligns a stack of images to a reference image using cross-correlation.

    This function assumes the stack does not contain the reference image itself.

    Stack shape should be (N, H, W) where N is the number of images.
    """

    new_images = []
    pred_shifts = []

    prev_img = ref_img
    for img in tqdm(stack):
        shift_pred = cross_correlation_shift(prev_img, img)
        shifted_image = shift(img, shift=shift_pred, mode="constant", cval=0.0)

        pred_shifts.append(shift_pred)
        new_images.append(shifted_image)

        prev_img = shifted_image

    return new_images, pred_shifts


def centering_com_alignment(image_stack):
    """
    Aligns the image stack to the center of mass of the whole image_stack to the
    image center. This is useful for aligning the tilt series to the invariant line.
    """

    aligned_stack = np.zeros_like(image_stack)
    h, w = image_stack.shape[1:]
    image_center = np.array([h // 2, w // 2])

    com_reference = np.array(center_of_mass(image_stack.mean(axis=0)))

    for i, img in enumerate(image_stack):
        com_img = np.array(center_of_mass(img))
        shift_vec = com_reference - com_img
        aligned_stack[i] = shift(img, shift=shift_vec, mode="constant", cval=0.0)

    final_shift = image_center - com_reference
    for i in range(aligned_stack.shape[0]):
        aligned_stack[i] = shift(aligned_stack[i], shift=final_shift, mode="constant", cval=0.0)

    return aligned_stack
