# Usage of astroSR

## Introduction

**astroSR** implements the Drizzle algorithm (Fruchter & Hook 2002) for astronomical super-resolution. This method combines multiple displaced (dithered) images to create higher resolution images while preserving photometry.

## Installation

```bash
pip install .
```

Or for development:
```bash
pip install -e .
```

## Basic Usage

### From command line

#### Simple example: combine 4 images

```bash
python scripts/run_drizzle.py \
    -i img1.fits img2.fits img3.fits img4.fits \
    -o combined_highres.fits \
    --scale-factor 2.0
```

#### With custom parameters

```bash
python scripts/run_drizzle.py \
    -i image*.fits \
    -o output_superres.fits \
    --pixel-scale 0.5 \
    --pixfrac 0.8 \
    --kernel square \
    --scale-factor 2.0
```

#### With weights based on exposure time

```bash
# If you have a short exposure (100s) and a long exposure (300s)
python scripts/run_drizzle.py \
    -i short_exposure.fits long_exposure.fits \
    -o weighted_output.fits \
    --weights 1.0 3.0 \
    --scale-factor 2.0
```

### Main Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-i, --inputs` | list | - | **Required**. Input FITS files |
| `-o, --output` | str | - | **Required**. Output FITS file |
| `--scale-factor` | float | 2.0 | Resolution improvement factor (typically 1.5-3.0) |
| `--pixel-scale` | float | auto | Output pixel scale in arcsec/pix |
| `--pixfrac` | float | 0.8 | Drizzle pixel fraction (0 < pixfrac ≤ 1.0) |
| `--kernel` | str | square | Kernel type: square, gaussian, tophat |
| `--weights` | list | None | Weights for each image |

### Advanced Options

```bash
# See all options
python scripts/run_drizzle.py --help
```

### As Python module

```python
from astrosr import drizzle_super_resolution

# Basic example
drizzle_super_resolution(
    input_files=['img1.fits', 'img2.fits', 'img3.fits'],
    output_file='combined.fits',
    scale_factor=2.0,
    pixfrac=0.8
)

# With advanced parameters
drizzle_super_resolution(
    input_files=['obs1.fits', 'obs2.fits', 'obs3.fits', 'obs4.fits'],
    output_file='superres.fits',
    pixel_scale=0.5,  # arcsec/pix
    scale_factor=2.0,
    pixfrac=0.8,
    weights=[1.0, 1.0, 1.2, 0.8],  # Weight by quality
    kernel='square',
    save_weight_map=True,
    preserve_flux=True
)
```

## Understanding the Parameters

### scale_factor (Scale Factor)

The `scale_factor` determines how much resolution increases:

- **scale_factor = 2.0**: Output pixels are 2× smaller (2× better resolution)
- **scale_factor = 3.0**: Output pixels are 3× smaller (3× better resolution)

**Recommendations:**
- For typical dithering (displacements ~0.5-1 pixel): use 2.0
- For aggressive dithering (displacements ~0.25 pixel): can use 3.0
- Do not exceed 4.0 unless you have very fine dithering

### pixfrac (Pixel Fraction)

The `pixfrac` controls the size of the "drop" (reduced pixel):

- **pixfrac = 1.0**: Drop the full size of the pixel
  - ✓ Maximum signal-to-noise (S/N)
  - ✗ Higher correlation between output pixels
  
- **pixfrac = 0.8**: Drop at 80% of pixel size (recommended)
  - ✓ Good balance between S/N and correlation
  - ✓ Lower noise correlation
  
- **pixfrac < 0.6**: Small drop
  - ✓ Minimum correlation
  - ✗ Lower S/N per pixel
  - ✓ Better effective resolution

**Recommendations:**
- For images with good S/N: 0.6-0.8
- For noisy images: 0.8-1.0
- Default: 0.8 (good general compromise)

### kernel (Kernel Type)

The `kernel` defines the shape of the "drop":

- **square**: Square pixel (faster, standard)
- **gaussian**: Gaussian profile (additional smoothing)
- **tophat**: Circular profile

**Recommendations:**
- Use `square` for most cases (faster)
- Use `gaussian` if you want additional smoothing
- Use `tophat` for circular PSF

### weights (Weights)

The `weights` allow weighting each image:

```python
# Example: weight by exposure time
drizzle_super_resolution(
    input_files=['t100s.fits', 't300s.fits', 't500s.fits'],
    output_file='weighted.fits',
    weights=[1.0, 3.0, 5.0],  # Proportional to time
    scale_factor=2.0
)
```

**Use cases:**
- Different exposure time
- Variable image quality (seeing, transparency)
- Prioritize certain observations

## Practical Examples

### Example 1: Dithered Observations

If you have 9 images of the same field with small displacements:

```bash
python scripts/run_drizzle.py \
    -i obs_[0-8].fits \
    -o superres_field.fits \
    --scale-factor 2.0 \
    --pixfrac 0.8
```

**Expected result:**
- 2× improved resolution
- Flux conserved
- Generated files:
  - `superres_field.fits`: High resolution image
  - `superres_field_weight.fits`: Coverage map

### Example 2: Combining Multiple Exposures

```bash
# 3 short exposures + 1 long exposure
python scripts/run_drizzle.py \
    -i short1.fits short2.fits short3.fits long.fits \
    -o combined.fits \
    --weights 1 1 1 5 \
    --scale-factor 2.0 \
    --pixfrac 0.8
```

### Example 3: Mosaic with Overlap

```bash
python scripts/run_drizzle.py \
    -i field_NW.fits field_NE.fits field_SW.fits field_SE.fits \
    -o mosaic.fits \
    --scale-factor 1.5 \
    --pixfrac 1.0
```

## Result Verification

### 1. Inspect Output Image

```python
from astropy.io import fits
import matplotlib.pyplot as plt

# Load image
data = fits.getdata('superres_field.fits')
header = fits.getheader('superres_field.fits')

print(f"Shape: {data.shape}")
print(f"Scale factor: {header['SCALE']}")
print(f"Pixel scale: {header['PIXSCALE']} arcsec/pix")

# Visualize
plt.imshow(data, origin='lower', vmin=np.percentile(data, 1), 
           vmax=np.percentile(data, 99))
plt.colorbar(label='Flux')
plt.title('Super-Resolved Image')
plt.show()
```

### 2. Verify Flux Conservation

```python
import numpy as np
from astropy.io import fits

# Load images
inputs = [fits.getdata(f'img{i}.fits') for i in range(1, 5)]
output = fits.getdata('combined.fits')

# Calculate fluxes
input_flux = np.sum([np.nansum(img) for img in inputs])
output_flux = np.nansum(output)

print(f"Total input flux: {input_flux:.6e}")
print(f"Total output flux: {output_flux:.6e}")
print(f"Ratio: {output_flux/input_flux:.6f}")
# Should be very close to 1.0 (±1%)
```

### 3. Measure Resolution Improvement

```python
from photutils.detection import DAOStarFinder
from photutils.centroids import centroid_sources

# Detect point sources
daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
sources = daofind(data - background)

# Measure FWHM of sources
# (requires gaussian fitting to each source)
# FWHM should be ~scale_factor× smaller
```

## Troubleshooting

### Problem: "No output pixel has coverage"

**Cause:** Images are not aligned or have no overlap.

**Solution:**
- Verify that FITS headers have correct WCS information
- Use alignment tools (e.g., astroalign, astrometry.net)
- Verify that images cover the same sky region

### Problem: Poor flux conservation (>5% error)

**Cause:** Inadequate parameters or NaN/infinite pixels in input.

**Solution:**
```python
# Clean data before drizzle
data = fits.getdata('input.fits')
data[~np.isfinite(data)] = 0  # Replace NaN/inf
fits.writeto('input_clean.fits', overwrite=True)
```

### Problem: Output image is very noisy

**Cause:** pixfrac too small or scale_factor too large.

**Solution:**
- Increase pixfrac to 0.8-1.0
- Reduce scale_factor to 2.0 or less
- Verify that there is sufficient dithering in the images

## References

1. **Fruchter, A. S., & Hook, R. N. (2002)**. "Drizzle: A Method for the Linear Reconstruction of Undersampled Images". *PASP*, 114(792), 144-152. [DOI: 10.1086/338393](https://doi.org/10.1086/338393)

2. **Gonzaga, S., et al. (2012)**. "The DrizzlePac Handbook". Space Telescope Science Institute.

3. Algorithm documentation: `docs/algorithm.md`

## Support

For more information, consult:
- Algorithm documentation: `docs/algorithm.md`
- Examples: `examples/`
- Issues: Project GitHub Issues
```

### 3. Medir Mejora de Resolución

```python
from photutils.detection import DAOStarFinder
from photutils.centroids import centroid_sources

# Detectar fuentes puntuales
daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
sources = daofind(data - background)

# Medir FWHM de fuentes
# (requiere ajuste gaussiano a cada fuente)
# La FWHM debería ser ~scale_factor× más pequeña
```

## Troubleshooting

### Problema: "Ningún píxel de salida tiene cobertura"

**Causa:** Las imágenes no están alineadas o no tienen solapamiento.

**Solución:**
- Verificar que los headers FITS tienen información WCS correcta
- Usar herramientas de alineación (e.g., astroalign, astrometry.net)
- Verificar que las imágenes cubren la misma región del cielo

### Problema: La conservación de flujo es pobre (>5% error)

**Causa:** Parámetros inadecuados o píxeles NaN/infinitos en entrada.

**Solución:**
```python
# Limpiar datos antes de drizzle
data = fits.getdata('input.fits')
data[~np.isfinite(data)] = 0  # Reemplazar NaN/inf
fits.writeto('input_clean.fits', data, overwrite=True)
```

### Problema: La imagen de salida es muy ruidosa

**Causa:** pixfrac muy pequeño o scale_factor muy grande.

**Solución:**
- Aumentar pixfrac a 0.8-1.0
- Reducir scale_factor a 2.0 o menos
- Verificar que hay suficiente dithering en las imágenes

## Referencias

1. **Fruchter, A. S., & Hook, R. N. (2002)**. "Drizzle: A Method for the Linear Reconstruction of Undersampled Images". *PASP*, 114(792), 144-152. [DOI: 10.1086/338393](https://doi.org/10.1086/338393)

2. **Gonzaga, S., et al. (2012)**. "The DrizzlePac Handbook". Space Telescope Science Institute.

3. Documentación del algoritmo: `docs/algorithm.md`

## Soporte

Para más información, consulte:
- Documentación del algoritmo: `docs/algorithm.md`
- Ejemplos: `examples/`
- Issues: GitHub Issues del proyecto
