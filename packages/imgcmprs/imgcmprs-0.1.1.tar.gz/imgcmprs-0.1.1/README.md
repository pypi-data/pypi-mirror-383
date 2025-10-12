# img

A fast, easy-to-use Python CLI tool for compressing JPEG and PNG images with both lossless and lossy modes.

---

## Features
- Compresses images individually or in bulk (folders)
- Supports JPEG and PNG
- **Lossless mode** (`-l`): Optimizes files without visible quality loss
- **Lossy mode** (`-q`): Reduce file size by lowering image quality
- Recursive directory support
- Custom output folder
- Prompts to delete originals after compression
- Skips replacement if compressed file is larger
- Cross-platform, requires Python 3.7+

---

## Installation

1. Install Python 3.7+
2. Clone this repo and install:
   ```bash
   pip install -e .
   # Or for user-local install:
   pip install --user .
   ```

---

## Usage

### Compress a single image (lossy, 60% quality):

```bash
img -i myphoto.jpg -q 60
```

### Compress a folder (lossless, best for PNG):

```bash
img -i images/ -o optimized/ -l -r
```

### Options (Single-letter flags)
| Flag | Meaning                        | Example                   |
|------|--------------------------------|---------------------------|
| -i   | Input file or folder (required)| `-i mypic.jpg`            |
| -o   | Output file or folder (optional)| `-o compressed/`         |
| -q   | JPEG quality (default 60; ignored in lossless mode)| `-q 80` |
| -l   | Use lossless compression       | `-l`                      |
| -r   | Recursively process folders    | `-r`                      |

- All flags are **single-letter** for speed and ease: `-i`, `-o`, `-q`, `-l`, `-r`.
- After compressing, you will be **prompted to delete the original files**.
- If the compressed file is larger, the original is kept and a warning is printed.

---

## Requirements
- Python 3.7+
- Pillow (`pip install Pillow`)

---

## Notes
- Lossless for PNG is truly lossless; for JPEG, uses `quality=100` with optimizations (minor effect but no further visual loss).
- Output defaults to `_compressed` directory if not specified for folders.
- Re-run with `-l` to optimize previously compressed images further (if possible).

---

## Publishing to PyPI

1. **Ensure you have an account on [PyPI](https://pypi.org/).**
2. **Install required tools:**
    ```bash
    pip install build twine
    ```
3. **Build your package:**
    ```bash
    python -m build
    ```
    This creates a `dist/` folder with your distributable files (tar.gz and .whl).
4. **Upload to PyPI:**
    ```bash
    python -m twine upload dist/*
    ```
5. **Enter your PyPI credentials when prompted.**

---

## License
MIT
