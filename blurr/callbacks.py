# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_callbacks.ipynb (unless otherwise specified).

__all__ = ['GradientCheckpointing']

# Cell
import importlib, sys, torch
from typing import Any, Callable, Dict, List, Optional, Union, Type

from fastcore.all import *
from fastai.callback.all import *
from fastai.imports import *
from fastai.learner import *
from fastai.torch_core import *
from transformers import PreTrainedModel

# Internal Cell
class CheckpointingNotSupported(Exception):
    def __init__(self, msg="Model does not support gradient checkpointing."):
        super().__init__(msg)

# Cell
class GradientCheckpointing(Callback):
    """A fastai callback to enable gradient checkpointing for compatible HuggingFace models."""

    def before_fit(self):
        """Enable gradient checkpointing on before_fit event."""

        # Check that huggingface model supports gradient checkpointing
        if not self.model.hf_model.supports_gradient_checkpointing:
            raise CheckpointingNotSupported()

        if self.model.hf_model.is_gradient_checkpointing == False:
            self.model.hf_model.gradient_checkpointing_enable()

    def after_fit(self):
        """Disable gradient checkpointing on after_fit event."""
        if self.model.hf_model.is_gradient_checkpointing:
            self.model.hf_model.gradient_checkpointing_disable()

    @staticmethod
    def supported(model: PreTrainedModel):
        """Tests whether a HuggingFace `PreTrainedModel` supports gradient checkpointing."""
        return model.supports_gradient_checkpointing