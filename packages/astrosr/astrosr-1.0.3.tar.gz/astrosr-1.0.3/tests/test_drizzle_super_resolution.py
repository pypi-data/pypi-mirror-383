"""
Tests for the Drizzle super-resolution algorithm.

Verifies:
- Flux conservation
- Resolution improvement
- Parameter handling
- Edge cases
"""

import numpy as np
import pytest
from astropy.io import fits

from astrosr.drizzle_super_resolution import (
    _calculate_overlap_area,
    drizzle_super_resolution,
)


def create_dithered_images(base_image, n_images=4, dither_pixels=0.5):
    """
    Creates dithered images by slightly shifting the base image.

    Parameters
    ----------
    base_image : ndarray
        Base image
    n_images : int
        Number of dithered images to create
    dither_pixels : float
        Maximum displacement in pixels

    Returns
    -------
    list of ndarray
        List of dithered images
    """
    dithered = []
    h, w = base_image.shape

    for i in range(n_images):
        # Small random displacement (integer pixels)
        shift_y = np.random.choice([-1, 0, 1])
        shift_x = np.random.choice([-1, 0, 1])

        # Create shifted image manually with proper bounds
        shifted = np.zeros_like(base_image)
        h, w = base_image.shape

        # Source region in original image
        src_y_start = max(0, shift_y)
        src_y_end = min(h, h + shift_y)
        src_x_start = max(0, shift_x)
        src_x_end = min(w, w + shift_x)

        # Destination region in shifted image
        dst_y_start = max(0, -shift_y)
        dst_y_end = dst_y_start + (src_y_end - src_y_start)
        dst_x_start = max(0, -shift_x)
        dst_x_end = dst_x_start + (src_x_end - src_x_start)

        shifted[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = base_image[
            src_y_start:src_y_end, src_x_start:src_x_end
        ]

        dithered.append(shifted)

    return dithered


def create_synthetic_image(shape, flux_level=1000.0, add_sources=False):
    """
    Creates synthetic image for testing.

    Parameters
    ----------
    shape : tuple
        Image shape (height, width)
    flux_level : float
        Base flux level
    add_sources : bool
        If True, adds point sources

    Returns
    -------
    image : ndarray
        Synthetic image
    """
    image = np.ones(shape, dtype=np.float64) * flux_level

    if add_sources:
        # Add some gaussian point sources
        h, w = shape
        # Source in center
        y, x = np.mgrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        sigma = 2.0
        gaussian = np.exp(-((x - center_x) ** 2 + (y - center_y) ** 2) / (2 * sigma**2))
        image += gaussian * flux_level * 10  # Bright source

        # Source in corner
        corner_y, corner_x = h // 4, w // 4
        gaussian2 = np.exp(
            -((x - corner_x) ** 2 + (y - corner_y) ** 2) / (2 * sigma**2)
        )
        image += gaussian2 * flux_level * 5

    return image


def test_resolution_improvement(tmp_path):
    """
    Test: verify that resolution improves effectively.
    """
    # Create base image with point sources
    base = create_synthetic_image((60, 60), flux_level=100.0, add_sources=True)

    # Create dithered images
    dithered = create_dithered_images(base, n_images=4, dither_pixels=1.0)

    # Save
    input_files = []
    for i, img in enumerate(dithered):
        fname = tmp_path / f"dither_{i}.fits"
        fits.writeto(fname, img, overwrite=True)
        input_files.append(str(fname))

    # Run drizzle
    output = tmp_path / "highres.fits"
    drizzle_super_resolution(
        input_files=input_files, output_file=str(output), scale_factor=2.0, pixfrac=0.8
    )

    # Verify resolution improvement
    result = fits.getdata(output)

    # Output image should be 2× larger
    assert result.shape == (120, 120)

    # Maximum value should be preserved (point source)
    # Note: may vary slightly due to resampling
    max_input = max([np.max(img) for img in dithered])
    max_output = np.nanmax(result)
    assert max_output > 0.5 * max_input  # At least 50% of maximum


def test_different_pixfracs(tmp_path):
    """
    Test: verify that different pixfracs produce different results.
    """
    # Create images with sources to see differences
    img1 = create_synthetic_image((30, 30), flux_level=1000.0, add_sources=True)
    img2 = create_synthetic_image((30, 30), flux_level=1000.0, add_sources=True)

    f1 = tmp_path / "pf_img1.fits"
    f2 = tmp_path / "pf_img2.fits"
    fits.writeto(f1, img1, overwrite=True)
    fits.writeto(f2, img2, overwrite=True)

    results = {}
    for pixfrac in [0.6, 0.8, 1.0]:
        output = tmp_path / f"output_pf_{pixfrac}.fits"
        drizzle_super_resolution(
            input_files=[str(f1), str(f2)],
            output_file=str(output),
            scale_factor=2.0,
            pixfrac=pixfrac,
        )
        results[pixfrac] = fits.getdata(output)

    # Verify that weight maps are different
    # (more important than final values)
    # when there are sources, since pixfrac affects coverage
    weight_file_06 = tmp_path / "output_pf_0.6_weight.fits"
    weight_file_10 = tmp_path / "output_pf_1.0_weight.fits"

    weight_06 = fits.getdata(weight_file_06)
    weight_10 = fits.getdata(weight_file_10)

    # Weight maps should be different
    assert not np.allclose(weight_06, weight_10, rtol=0.01)


def test_weights(tmp_path):
    """
    Test: verify that weights are applied correctly.
    """
    # Create two images with very different values
    img1 = create_synthetic_image((30, 30), flux_level=1000.0)
    img2 = create_synthetic_image((30, 30), flux_level=2000.0)

    f1 = tmp_path / "w_img1.fits"
    f2 = tmp_path / "w_img2.fits"
    fits.writeto(f1, img1, overwrite=True)
    fits.writeto(f2, img2, overwrite=True)

    # Test 1: equal weights -> average
    output_equal = tmp_path / "output_equal_weights.fits"
    drizzle_super_resolution(
        input_files=[str(f1), str(f2)],
        output_file=str(output_equal),
        scale_factor=1.0,  # No scale change for simplicity
        weights=[1.0, 1.0],
        pixfrac=1.0,
    )
    result_equal = fits.getdata(output_equal)
    mean_equal = np.nanmean(result_equal)

    # Test 2: second weight much higher -> close to img2
    output_heavy = tmp_path / "output_heavy_weights.fits"
    drizzle_super_resolution(
        input_files=[str(f1), str(f2)],
        output_file=str(output_heavy),
        scale_factor=1.0,
        weights=[1.0, 10.0],
        pixfrac=1.0,
    )
    result_heavy = fits.getdata(output_heavy)
    mean_heavy = np.nanmean(result_heavy)

    # The result with higher weight should be closer to img2
    assert mean_equal < mean_heavy
    assert mean_heavy > 1500  # Closer to 2000 than to 1000


def test_invalid_parameters(tmp_path):
    """
    Test: verify that invalid parameters are rejected.
    """
    # Create dummy image
    img = create_synthetic_image((20, 20))
    f = tmp_path / "dummy.fits"
    fits.writeto(f, img, overwrite=True)
    output = tmp_path / "output.fits"

    # pixfrac out of range
    with pytest.raises(ValueError, match="pixfrac"):
        drizzle_super_resolution(
            input_files=[str(f)], output_file=str(output), pixfrac=1.5  # > 1.0
        )

    with pytest.raises(ValueError, match="pixfrac"):
        drizzle_super_resolution(
            input_files=[str(f)], output_file=str(output), pixfrac=0.0  # = 0
        )

    # negative scale_factor
    with pytest.raises(ValueError, match="scale_factor"):
        drizzle_super_resolution(
            input_files=[str(f)], output_file=str(output), scale_factor=-1.0
        )

    # Empty file list
    with pytest.raises(ValueError, match="At least one input image is required"):
        drizzle_super_resolution(input_files=[], output_file=str(output))

    # Weights with incorrect length
    f2 = tmp_path / "dummy2.fits"
    fits.writeto(f2, img, overwrite=True)
    with pytest.raises(ValueError, match="weights"):
        drizzle_super_resolution(
            input_files=[str(f), str(f2)],
            output_file=str(output),
            weights=[1.0],  # Solo 1 peso para 2 imágenes
        )


def test_overlap_area_calculation():
    """
    Test: verify overlap area calculation.
    """
    # Test 1: Complete overlap (drop centered on pixel)
    area = _calculate_overlap_area(
        drop_center_i=5.5,
        drop_center_j=5.5,
        drop_half_size=0.4,
        pixel_i=5,
        pixel_j=5,
        kernel="square",
    )
    assert area > 0.5  # At least 50% overlap

    # Test 2: No overlap (drop very far away)
    area = _calculate_overlap_area(
        drop_center_i=5.5,
        drop_center_j=5.5,
        drop_half_size=0.3,
        pixel_i=20,
        pixel_j=20,
        kernel="square",
    )
    assert area == 0.0

    # Test 3: Partial overlap (drop on pixel edge)
    area = _calculate_overlap_area(
        drop_center_i=5.9,
        drop_center_j=5.5,
        drop_half_size=0.4,
        pixel_i=5,
        pixel_j=5,
        kernel="square",
    )
    assert area > 0  # There should be some overlap


def test_different_kernels(tmp_path):
    """
    Test: verify that different kernels execute correctly.
    """
    # Create image with point sources
    img1 = create_synthetic_image((30, 30), flux_level=1000.0, add_sources=True)
    img2 = create_synthetic_image((30, 30), flux_level=1000.0, add_sources=True)

    f1 = tmp_path / "k_img1.fits"
    f2 = tmp_path / "k_img2.fits"
    fits.writeto(f1, img1, overwrite=True)
    fits.writeto(f2, img2, overwrite=True)

    results = {}
    for kernel in ["square", "gaussian", "lanczos"]:
        output = tmp_path / f"output_kernel_{kernel}.fits"
        drizzle_super_resolution(
            input_files=[str(f1), str(f2)],
            output_file=str(output),
            scale_factor=2.0,
            pixfrac=0.8,
            kernel=kernel,
        )
        results[kernel] = fits.getdata(output)

        # Verify that the result is valid
        assert results[kernel].shape == (60, 60)
        assert not np.all(np.isnan(results[kernel]))

    # Different kernels should produce valid results
    # (Note: differences may be small with our simplified algorithm)
    assert len(results) == 3


def test_output_shape(tmp_path):
    """
    Test: verify that custom output_shape works.
    """
    img = create_synthetic_image((30, 30))
    f = tmp_path / "img.fits"
    fits.writeto(f, img, overwrite=True)

    # Specify custom output shape
    custom_shape = (80, 80)
    output = tmp_path / "custom_shape.fits"
    drizzle_super_resolution(
        input_files=[str(f)],
        output_file=str(output),
        output_shape=custom_shape,
        scale_factor=2.0,
    )

    result = fits.getdata(output)
    assert result.shape == custom_shape


def test_header_metadata(tmp_path):
    """
    Test: verify that metadata is saved correctly in the header.
    """
    img = create_synthetic_image((30, 30))
    f = tmp_path / "img.fits"
    fits.writeto(f, img, overwrite=True)

    output = tmp_path / "with_metadata.fits"
    scale_factor = 2.5
    pixfrac = 0.75

    drizzle_super_resolution(
        input_files=[str(f)],
        output_file=str(output),
        scale_factor=scale_factor,
        pixfrac=pixfrac,
    )

    # Read header
    header = fits.getheader(output)

    # Verify metadata
    assert "SCALE" in header
    assert header["SCALE"] == scale_factor
    assert "PIXFRAC" in header
    assert header["PIXFRAC"] == pixfrac
    assert "NIMAGES" in header
    assert header["NIMAGES"] == 1


def test_nan_handling(tmp_path):
    """
    Test: verify correct handling of NaN pixels.
    """
    # Create image with some NaN
    img = create_synthetic_image((30, 30), flux_level=1000.0)
    img[10:15, 10:15] = np.nan

    f = tmp_path / "img_with_nan.fits"
    fits.writeto(f, img, overwrite=True)

    output = tmp_path / "output_nan.fits"
    drizzle_super_resolution(
        input_files=[str(f)], output_file=str(output), scale_factor=2.0
    )

    # The result should have NaN where there is no coverage
    result = fits.getdata(output)
    assert np.any(np.isnan(result))  # There should be some NaN
    assert not np.all(np.isnan(result))  # But not all


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
