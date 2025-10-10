# MathyKit

MathyKit is a lightweight Python framework for building and using AI models, with a focus on Meta/Facebook models. It provides a simple and efficient way to use state-of-the-art AI models without the need for API keys or local model installations.

## Features

- Easy-to-use interface for AI model integration
- Support for Meta/Facebook models
- Pure Python implementation
- No API keys required
- Lightweight and efficient

## Installation

```bash
pip install mathykit
```

## Quick Start

```python
from mathkit import Model
from mathkit.models import MetaOPT

# Load a pre-trained model
model = MetaOPT.from_pretrained("meta-opt-1.3b")

# Generate text
output = model.generate("What is artificial intelligence?")
print(output)
```

## Documentation

For detailed documentation and examples, visit our [documentation page](https://mathkit.readthedocs.io).

## License

This project is licensed under the MIT License - see the LICENSE file for details.