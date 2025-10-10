"""Core functionality for MathyKit."""

from abc import ABC, abstractmethod
import torch
import numpy as np

class Model(ABC):
    """Base class for all models in MathyKit."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = None
        self._tokenizer = None

    @abstractmethod
    def forward(self, inputs):
        """Forward pass through the model."""
        pass

    @abstractmethod
    def generate(self, prompt, max_length=100, **kwargs):
        """Generate output from the model."""
        pass

    @classmethod
    @abstractmethod
    def from_pretrained(cls, model_name, **kwargs):
        """Load a pre-trained model."""
        pass

    def to(self, device):
        """Move model to specified device."""
        self.device = device
        if self._model is not None:
            self._model.to(device)
        return self

    def eval(self):
        """Set model to evaluation mode."""
        if self._model is not None:
            self._model.eval()
        return self