# astroSR - Astronomical Super-Resolution with Drizzle

[![CI](https://github.com/dot-gabriel-ferrer/astroSR/actions/workflows/ci.yml/badge.svg)](https://github.com/dot-gabriel-ferrer/astroSR/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/dot-gabriel-ferrer/astroSR/branch/main/graph/badge.svg)](https://codecov.io/gh/dot-gabriel-ferrer/astroSR)

## Description

This package implements the **Drizzle** algorithm (Fruchter & Hook 2002) to combine multiple dithered astronomical images and create super-resolution images with precise photometry conservation.

### Key Features

✨ **Professional Drizzle Algorithm**
- Faithful implementation of Fruchter & Hook (2002)
- Exact flux conservation for precise photometry
- Pixel-to-pixel mapping with overlap area calculation

🔬 **Real Resolution Improvement**
- Increases spatial resolution (reduces arcsec/pix)
- Leverages dithering to resolve sub-pixel details
- Configurable improvement factor (typically 2-3×)

📊 **Flexible Weighting**
- Custom weights per image (exposure time, quality, etc.)
- Multiple kernel types (square, gaussian, tophat)
- Noise correlation control via `pixfrac` parameter

📐 **Complete WCS Support**
- Input WCS header handling
- Precise geometric transformations
- Output image WCS generation

### Resolution Gain with Drizzle

The achievable spatial resolution using drizzle depends on:
- The number of input images per field.
- The dithering pattern (relative sub-pixel shifts between images).
- The alignment quality and the PSF.

**Theoretical estimate:**
- If images are well-aligned and dithers are optimal, the pixel scale can be reduced by up to a factor of √N, where N is the number of independent, well-dithered images.
- In practice, the gain is usually between 1.5× and 2× (i.e., you can halve the pixel scale) with at least 4–9 images and good dithering.

**Practical summary:**
- 2 images: modest improvement (~1.4×)
- 4 images: clear improvement (~2×)
- 9 images: optimal improvement (~3×)
- More images: marginal additional gain, limited by PSF and alignment.

## Installation

```bash
# Clone the repository
git clone https://github.com/dot-gabriel-ferrer/astroSR.git
cd astroSR

# Install
pip install .

# Or for development
pip install -e .
```

### Dependencies

- Python ≥ 3.9
- NumPy
- Astropy
- SciPy
- Matplotlib (for visualization)

## Quick Usage

### Command Line

```bash
# Basic example: combine 4 images with 2× improvement factor
python scripts/run_drizzle.py \
    -i img1.fits img2.fits img3.fits img4.fits \
    -o combined_highres.fits \
    --scale-factor 2.0 \
    --pixfrac 0.8
```

```bash
# With custom weights
python scripts/run_drizzle.py \
    -i short.fits long.fits \
    -o weighted_output.fits \
    --weights 1.0 3.0 \
    --scale-factor 2.0
```

### As Python Module

```python
from astrosr import drizzle_super_resolution

# Basic example
drizzle_super_resolution(
    input_files=['img1.fits', 'img2.fits', 'img3.fits'],
    output_file='superres.fits',
    scale_factor=2.0,
    pixfrac=0.8
)

# With advanced parameters
drizzle_super_resolution(
    input_files=['obs1.fits', 'obs2.fits', 'obs3.fits', 'obs4.fits'],
    output_file='output.fits',
    pixel_scale=0.5,        # arcsec/pix
    scale_factor=2.0,
    pixfrac=0.8,
    weights=[1.0, 1.0, 1.2, 0.8],
    kernel='square',
    save_weight_map=True,
    preserve_flux=True
)
```

## Documentation

- **[Usage Guide](docs/usage.md)**: Detailed examples and use cases
- **[Drizzle Algorithm](docs/algorithm.md)**: Mathematical foundations and references
- **[API Reference](docs/api.md)**: Complete function documentation (coming soon)

## Main Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scale_factor` | 2.0 | Resolution improvement factor (1.5-3.0 typical) |
| `pixfrac` | 0.8 | Drizzle pixel fraction (0.6-1.0 recommended) |
| `kernel` | 'square' | Kernel type: square, gaussian, tophat |
| `weights` | None | Per-image weights (e.g., exposure time) |
| `pixel_scale` | auto | Output pixel scale (arcsec/pix) |

See `docs/usage.md` for detailed descriptions.

## Use Cases

### 1. Dithered Observations

Combine multiple exposures of the same field with small displacements:

```bash
python scripts/run_drizzle.py -i dithered_*.fits -o superres.fits --scale-factor 2.0
```

### 2. Overlapping Mosaics

Join partially overlapping images into a high-resolution mosaic:

```bash
python scripts/run_drizzle.py -i tile_*.fits -o mosaic.fits --scale-factor 1.5
```

### 3. Quality Weighting

Assign weights based on exposure time or seeing:

```python
drizzle_super_resolution(
    input_files=['good_seeing.fits', 'medium_seeing.fits', 'poor_seeing.fits'],
    output_file='quality_weighted.fits',
    weights=[3.0, 2.0, 1.0],
    scale_factor=2.0
)
```

## Project Structure

```
astrosr/
├── src/astrosr/              # Main code
│   ├── __init__.py
│   └── drizzle_super_resolution.py
├── tests/                    # Unit tests
│   └── test_drizzle_super_resolution.py
├── scripts/                  # CLI scripts
│   └── run_drizzle.py
├── docs/                     # Documentation
│   ├── usage.md             # Usage guide
│   └── algorithm.md         # Mathematical foundations
├── examples/                 # Examples (coming soon)
├── pyproject.toml           # Package configuration
└── README.md                # This file
```

## Scientific References

1. **Fruchter, A. S., & Hook, R. N. (2002)**. "Drizzle: A Method for the Linear Reconstruction of Undersampled Images". *Publications of the Astronomical Society of the Pacific*, 114(792), 144-152. [DOI: 10.1086/338393](https://doi.org/10.1086/338393)

2. **Gonzaga, S., et al. (2012)**. "The DrizzlePac Handbook". Space Telescope Science Institute.

3. **Koekemoer, A. M., et al. (2003)**. "HST Dither Handbook". Space Telescope Science Institute.

## Validation

The algorithm has been validated for:

- ✓ Flux conservation (<1% error)
- ✓ Effective resolution improvement
- ✓ Correct NaN pixel handling
- ✓ Precise geometric transformations

See `tests/` for test cases.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Contact

- Issues: [GitHub Issues](https://github.com/dot-gabriel-ferrer/astroSR/issues)
- Email: gabriel.ferrer@example.com

## Acknowledgments

- Original algorithm: Andrew Fruchter and Richard Hook (STScI)
- Inspiration: DrizzlePac package from Space Telescope Science Institute
- Astropy community

---

**Note**: This is a research package. For critical applications, consider using the official DrizzlePac from STScI.
