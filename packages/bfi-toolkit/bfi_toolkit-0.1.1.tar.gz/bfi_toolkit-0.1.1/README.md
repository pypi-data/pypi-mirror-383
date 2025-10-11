# 🌊 BFI-Toolkit

[![TestPyPI](https://img.shields.io/badge/TestPyPI-bfi--toolkit-blue)](https://test.pypi.org/project/bfi-toolkit/)
[![PyPI](https://img.shields.io/pypi/v/bfi-toolkit.svg)](https://pypi.org/project/bfi-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.1029%2F2024WR039479-blue)](https://doi.org/10.1029/2024WR039479)

A lightweight and flexible Python package for estimating **Baseflow** and **Baseflow Index (BFI)** from streamflow time series.

This toolkit provides a simple, efficient way to:
- Separate baseflow using forward/backward recession analysis
- Compute optimized decay parameters (*k*)
- Calculate **BFI** — a key hydrologic metric for understanding watershed storage and runoff behavior.

---

## 📄 Associated Research

This toolkit was developed as part of the work presented in:

> **Farmani, M. A.**, Tavakoly, A., Behrangi, A., Qiu, Y., Gupta, A., Jawad, M., Yousefi Sohi, H., Zhang, X., Geheran, M., Niu, G.-Y. (2025).  
> *Improving Streamflow Predictions in the Arid Southwestern United States Through Understanding of Baseflow Generation Mechanisms.*  
> *Water Resources Research.* [https://doi.org/10.1029/2024WR039479](https://doi.org/10.1029/2024WR039479)

© Author(s) 2025. This work is distributed under the Creative Commons Attribution 4.0 License.

---

## 📦 Installation

### From PyPI (when released)
```bash
pip install bfi-toolkit
```

### From source (development version)
```bash
git clone https://github.com/mfarmani95/BFI-Toolkit.git
cd BFI-Toolkit
pip install -e .
```

This installs the package in **editable mode**, so any code edits are reflected immediately without reinstalling.

---

## ⚡️ Quick Start

```python
import numpy as np
from bfi_toolkit import compute_bfi

# Example: simple synthetic streamflow data
streamflow = np.array([5, 5, 5, 6, 7, 6, 5.8, 5.6, 5.4, 5.2, 5, 4.9, 4.8])

result = compute_bfi(streamflow, day_after_peak=5, start_date="2020-01-01")

print("Optimized k:", result["k"])
print("BFI:", result["bfi"])
print("Baseflow head:\n", result["baseflow"].head())
```

✅ **Supported input types:**
- Python `list`
- `numpy.ndarray`
- `pandas.DataFrame` (must contain column `QQ`)
- `torch.Tensor` *(optional, if PyTorch installed)*

---

## 🧪 Development Setup

### Option 1: with pip
```bash
git clone https://github.com/mfarmani95/BFI-Toolkit.git 
cd BFI-Toolkit
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements-dev.txt
```

### Option 2: with Conda (recommended)
```bash
git clone https://github.com/mfarmani95/BFI-Toolkit.git 
cd BFI-Toolkit
conda env create -f environment.yml
conda activate bfi-toolkit
```

Then:
```bash
make dev     # install dev dependencies
make test    # run tests
```

---

## 🧰 Useful Makefile Commands

| Command             | Description                                |
|----------------------|---------------------------------------------|
| `make install`       | Install package in editable mode           |
| `make dev`           | Install dev dependencies                   |
| `make test`          | Run test suite with pytest                 |
| `make format`        | Auto-format code with Black                |
| `make lint`          | Run static checks with Ruff                |
| `make build`         | Build distribution package                |
| `make upload-test`   | Upload to TestPyPI                         |
| `make upload`        | Upload to PyPI                             |

---

## 🧠 Contributing

We welcome contributions from the community 🙌  

1. **Fork** the repository  
2. Create a **feature branch**  
3. Commit your changes with clear messages  
4. Add or update tests if needed  
5. Submit a **Pull Request**

Before submitting:
```bash
make format
make lint
make test
```

---

## 🧭 Features

- ✅ Supports multiple input formats (NumPy, Pandas, PyTorch, lists)  
- 📉 Flexible dry period filtering with `day_after_peak`  
- ⚙️ Optimized decay constant estimation (*k*)  
- 💧 Baseflow separation using forward/backward recession  
- 📊 Automatic BFI calculation  
- 🧰 Clean modular structure (core, utils, optimization, baseflow)  
- 🧪 Fully testable with `pytest`

---

## 📝 Citation

If you use this toolkit in your research or operational projects, please cite:

> Farmani, M. A. (2025). *BFI-Toolkit: A lightweight Python package for estimating baseflow and Baseflow Index (BFI)*.  
> GitHub: [https://github.com/<your-username>/BFI-Toolkit](https://github.com/<your-username>/BFI-Toolkit)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).  
You’re free to use, modify, and distribute it — just give credit where it’s due.

---

## 🚀 Roadmap

- [ ] Add uncertainty quantification for k estimates  
- [ ] Add multi-resolution time series support (weekly, monthly)  
- [ ] Add visualization module (hydrograph plotting)  
- [ ] Add unit conversion utilities for different discharge formats  
- [ ] Publish as official PyPI package

---

## 💧 Acknowledgements

Developed as part of ongoing hydrologic research by  
**Mohammad Ali Farmani** — University of Arizona.  

Inspired by the need for transparent, flexible, and efficient baseflow separation tools for hydrologic modeling and water resources applications.

