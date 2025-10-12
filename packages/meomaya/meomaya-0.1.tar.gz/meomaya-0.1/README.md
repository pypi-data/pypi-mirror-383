# 🚀 Meomaya

[![Documentation](https://img.shields.io/badge/Docs-Site-blue?logo=github)](https://kashyapsinh-gohil.github.io/MeoMaya-Info/) 
[![PyPI version](https://badge.fury.io/py/Meomaya.svg)](https://badge.fury.io/py/Meomaya)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1G61wWs2pzCKJ2lyVkrtYVjIq_lBZPFrW?usp=sharing)

> 🔥 A modern, hardware-accelerated NLP framework designed for both research and production

MeoX is a powerful, pure-Python NLP framework that combines state-of-the-art language processing with hardware optimization. Built for researchers and developers who need both flexibility and performance.

## ✨ Key Features

- 🚄 **Hardware-Aware Execution**: Automatic optimization for CPU, CUDA, and MPS
- 🔧 **Modular Architecture**: Clean, extensible core with plug-and-play components
- 🎯 **Multiple Modalities**: Support for text, audio, image, and video processing
- 🤖 **Local Transformers**: Efficient offline processing with local model support
- 🌐 **REST API Ready**: Built-in FastAPI server for production deployment
- 📦 **Easy Integration**: Simple pip installation, minimal dependencies

## 🚀 Quick Install

```bash
pip install Meomaya
```


[![Documentation](https://img.shields.io/badge/Docs-Site-blue?logo=github)](https://kashyapsinh-gohil.github.io/MeoMaya-Info/) 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1G61wWs2pzCKJ2lyVkrtYVjIq_lBZPFrW?usp=sharing)


https://github.com/user-attachments/assets/df92d1db-3bd6-445e-a502-fb730513847d

## 🎯 Quick Start Guide

### Basic Usage

```python
from meomaya import Pipeline

# Create a pipeline for text processing
pipeline = Pipeline(mode="text")

# Process text with automatic hardware optimization
result = pipeline.process("Hello from MeoX! 👋")
print(result)
```

### 🌐 REST API Server

Launch the built-in API server for production use:

```bash
uvicorn meomaya.api.server:app --host 0.0.0.0 --port 8000
```

### 💻 Command Line Interface

Process text directly from the terminal:

```bash
python -m meomaya "Your text here" --mode text
```

### 🔒 Offline Mode

Enable strict offline mode for complete local processing:

```bash
export MEOMAYA_STRICT_OFFLINE=1
```

## 🛠 Advanced Features

- **Hardware Optimization**: Automatically detects and utilizes available hardware (CPU/CUDA/MPS)
- **Multimodal Support**: Process text, audio, images, and video through unified pipelines
- **Local Models**: Run transformer models completely offline
- **Extensible Architecture**: Easy to add custom processors and pipelines
- **Production Ready**: Built-in API server with FastAPI
- **Memory Efficient**: Smart resource management for large-scale processing

## 📚 Documentation

Visit our [comprehensive documentation](https://kashyapsinh-gohil.github.io/MeoMaya-Info/) for:
- Detailed API reference
- Advanced usage examples
- Best practices and optimization tips
- Hardware configuration guides
- Custom pipeline development

## 📦 Installation Options

### Basic Installation
```bash
pip install Meomaya
```

### With All Optional Dependencies
```bash
pip install "Meomaya[full]"
```

### Feature-specific Installation
```bash
# For ML features only
pip install "Meomaya[ml]"

# For Hugging Face integration
pip install "Meomaya[hf]"

# For API server
pip install "Meomaya[api]"
```

## 📜 License

This project is licensed under the Polyform Noncommercial License 1.0.0.
- ✅ Free for non-commercial use
- 🤝 Commercial licensing available
- 📧 Contact Kagohil000@gmail.com for commercial inquiries

---
<p align="center">
Made with ❤️ by <a href="https://github.com/KashyapSinh-Gohil">Kashyapsinh Gohil</a>
</p>
