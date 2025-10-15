# Drizzle Algorithm for Astronomical Super-Resolution

## Introduction

The **Drizzle** algorithm (from English "drop size," abbreviated "drizzle") was originally developed for processing Hubble Space Telescope (HST) images by Fruchter and Hook (2002). This method allows combining multiple displaced (dithered) images to create a higher resolution image while preserving photometry and minimizing noise correlation between pixels.

## Scientific References

1. **Fruchter, A. S., & Hook, R. N. (2002)**. "Drizzle: A Method for the Linear Reconstruction of Undersampled Images". *Publications of the Astronomical Society of the Pacific*, 114(792), 144-152. [DOI: 10.1086/338393](https://doi.org/10.1086/338393)

2. **Gonzaga, S., et al. (2012)**. "The DrizzlePac Handbook". Space Telescope Science Institute.

3. **Koekemoer, A. M., et al. (2003)**. "HST Dither Handbook". Space Telescope Science Institute.

## Mathematical Foundations

### 1. Undersampling Problem

In astronomy, images are often undersampled when the physical pixel is larger than the telescope's PSF (Point Spread Function). The Nyquist criterion requires at least 2 pixels per PSF FWHM for adequate sampling.

### 2. Drizzle Principle

The drizzle algorithm reconstructs a high-resolution image by mapping each input pixel to the output grid considering:

- **Geometric transformation**: Precise alignment between images
- **Drop size (pixfrac)**: Fraction of the input pixel area that "drips" to the output pixel
- **Flux conservation**: Total flux is conserved through area weighting

### 3. Mathematical Formulation

For each output pixel `O(x_out, y_out)`:

```
O(x_out, y_out) = Σ_i Σ_j [I_i(x_in, y_in) × W_i × A_overlap(x_in, y_in, x_out, y_out)] / Σ_i Σ_j [W_i × A_overlap]
```

Where:
- `I_i(x_in, y_in)`: Input pixel value in image i
- `W_i`: Weight of image i (based on exposure time, quality, etc.)
- `A_overlap`: Overlap area between the input "drop" and the output pixel
- `i`: Image index
- `j`: Pixel index within the image

### 4. Overlap Area Calculation

The overlap area is calculated considering:

1. **Geometric transformation**: Coordinate mapping (x_in, y_in) → (x_out, y_out)
2. **Drop size**: Input pixel scaled by `pixfrac`
3. **Polygon intersection**: Area where the drop intersects the output pixel

```
A_overlap = Area_intersection(Drop_input × pixfrac, Pixel_output)
```

### 5. Key Parameters

#### pixfrac (Pixel Fraction)
- **Range**: 0 < pixfrac ≤ 1.0
- **Typical value**: 0.8-1.0
- **Effect**:
  - `pixfrac = 1.0`: Maximum signal conservation, higher pixel correlation
  - `pixfrac < 1.0`: Lower noise correlation, but lower S/N per pixel
  
#### pixel_scale (Pixel Scale)
- **Definition**: Output pixel size in arcsec/pixel
- **Resolution relationship**: `pixel_scale_out < pixel_scale_in` → Super-resolution
- **Typical value**: 0.5 × pixel_scale_in (factor 2 improvement)

#### Weights
Weights can be based on:
- Exposure time
- Image quality (seeing, transparency)
- Distance to detector edge
- Bad pixel mask

## Implemented Algorithm

### Process Steps

1. **Image Reading**
   - Load FITS images with data and headers
   - Extract WCS (World Coordinate System) information
   - Identify and apply bad pixel masks

2. **Image Alignment**
   - Use WCS information for coordinate transformation
   - If no WCS: image registration based on sources
   - Calculate transformation matrix for each image

3. **Output Grid Definition**
   - Determine common FOV of all images
   - Set output pixel_scale
   - Create output arrays: image and total weight

4. **Drizzling**
   For each input image:
   ```python
   for input_image in images:
       for pixel in input_image:
           # Transform coordinates
           x_out, y_out = transform(x_in, y_in, wcs)
           
           # Calculate drop (pixel reduced by pixfrac)
           drop_size = pixel_size * pixfrac
           
           # Find output pixels that intersect the drop
           affected_pixels = find_overlap(x_out, y_out, drop_size)
           
           # Distribute flux proportionally
           for out_pix in affected_pixels:
               overlap_area = calculate_overlap(drop, out_pix)
               contribution = pixel_value * weight * overlap_area
               output[out_pix] += contribution
               weight_map[out_pix] += weight * overlap_area
   ```

5. **Normalization**
   ```python
   # Divide by weight map to preserve photometry
   final_image = output / weight_map
   ```

6. **Result Writing**
   - Create FITS header with updated WCS
   - Include process metadata
   - Save output image and weight map

## Advantages of the Drizzle Method

1. **Flux Conservation**: Photometry is preserved exactly
2. **Resolution Improvement**: Exploits dithering to resolve sub-pixel details
3. **Flexibility**: Allows arbitrary geometric correction
4. **Correlation Control**: The pixfrac parameter allows balancing between S/N and resolution
5. **Bad Pixel Treatment**: Masks propagate correctly

## Limitations and Considerations

1. **Requires Dithering**: Images must be displaced (typically > 0.5 pixel)
2. **WCS Information**: Necessary for precise transformations
3. **Computational Cost**: Proportional to N_images × N_pixels_in × overlap_factor
4. **Correlated Noise**: With pixfrac = 1.0, output pixels are not independent

## Algorithm Validation

To verify correct implementation:

1. **Flux Conservation**:
   ```python
   assert np.isclose(np.sum(input_images), np.sum(output_image))
   ```

2. **Resolution Improvement**:
   - Measure FWHM of point sources
   - FWHM_output < FWHM_input

3. **Test with Synthetic Images**:
   - Create images with known point sources
   - Apply sub-pixel displacements
   - Verify position recovery

## Use in Astrophysical Context

This algorithm is especially useful for:

- **Dithered observations**: Multiple exposures with small displacements
- **Mosaics**: Combine partially overlapping images
- **Distortion correction**: Rectify optical distortions of the instrument
- **Precision astrometry**: Improve positional accuracy of sources
- **Aperture photometry**: Better resolution allows smaller apertures, less contamination

## Additional References

- Casertano, S., et al. (2000). "The Photometric Performance and Calibration of WFPC2". PASP, 112, 1486.
- Anderson, J., & King, I. R. (2006). "PSFs, Photometry, and Astronomy for the ACS/WFC". STScI Instrument Science Report ACS 2006-01.
