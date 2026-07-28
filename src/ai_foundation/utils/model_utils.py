"""
BLACK VEIL V5 - Model Utilities
Helper functions for model management and manipulation
"""
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import torch
import torch.nn as nn
import json
from datetime import datetime


class ModelUtils:
    """Utility class for model management."""

    @staticmethod
    def get_model_size_mb(model: nn.Module) -> float:
        """
        Calculate model size in MB.

        Args:
            model: PyTorch model

        Returns:
            float: Model size in MB
        """
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        total_bytes = param_size + buffer_size
        return total_bytes / (1024 * 1024)

    @staticmethod
    def freeze_layers(model: nn.Module, freeze_ratio: float = 0.5) -> int:
        """
        Freeze a portion of model layers for transfer learning.

        Args:
            model: PyTorch model
            freeze_ratio: Ratio of layers to freeze

        Returns:
            int: Number of frozen parameters
        """
        layers = list(model.children())
        num_to_freeze = int(len(layers) * freeze_ratio)
        frozen_params = 0

        for layer in layers[:num_to_freeze]:
            for param in layer.parameters():
                param.requires_grad = False
                frozen_params += param.numel()

        return frozen_params

    @staticmethod
    def unfreeze_all(model: nn.Module) -> int:
        """
        Unfreeze all model parameters.

        Args:
            model: PyTorch model

        Returns:
            int: Number of unfrozen parameters
        """
        total = 0
        for param in model.parameters():
            param.requires_grad = True
            total += param.numel()
        return total

    @staticmethod
    def get_parameter_stats(model: nn.Module) -> Dict[str, float]:
        """
        Get parameter statistics.

        Args:
            model: PyTorch model

        Returns:
            Dict[str, float]: Parameter statistics
        """
        all_params = torch.cat([p.flatten() for p in model.parameters()])

        return {
            "total_params": model.numel() if hasattr(model, "numel") else 0,
            "mean": all_params.mean().item(),
            "std": all_params.std().item(),
            "min": all_params.min().item(),
            "max": all_params.max().item(),
            "zeros": (all_params == 0).sum().item(),
            "trainable": sum(
                p.numel() for p in model.parameters() if p.requires_grad
            ),
        }

    @staticmethod
    def gradient_norm(model: nn.Module) -> float:
        """
        Calculate total gradient norm for gradient clipping.

        Args:
            model: PyTorch model

        Returns:
            float: Total gradient norm
        """
        total_norm = 0.0
        for p in model.parameters():
            if p.grad is not None:
                param_norm = p.grad.detach().data.norm(2)
                total_norm += param_norm.item() ** 2
        return total_norm ** 0.5

    @staticmethod
    def save_model_summary(
        model: nn.Module,
        path: str,
        input_shape: tuple,
    ) -> None:
        """
        Save model architecture summary to JSON.

        Args:
            model: PyTorch model
            path: Output path
            input_shape: Expected input shape
        """
        summary = {
            "model_type": type(model).__name__,
            "input_shape": list(input_shape),
            "total_parameters": sum(p.numel() for p in model.parameters()),
            "trainable_parameters": sum(
                p.numel() for p in model.parameters() if p.requires_grad
            ),
            "non_trainable_parameters": sum(
                p.numel() for p in model.parameters() if not p.requires_grad
            ),
            "model_size_mb": round(
                ModelUtils.get_model_size_mb(model), 2
            ),
            "device": next(model.parameters()).device.type,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Add layer details
        layers = []
        for name, module in model.named_modules():
            if name:
                layers.append({
                    "name": name,
                    "type": type(module).__name__,
                    "parameters": sum(p.numel() for p in module.parameters()),
                })
        summary["layers"] = layers

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)

    @staticmethod
    def get_learning_rate(optimizer: torch.optim.Optimizer) -> float:
        """
        Get current learning rate from optimizer.

        Args:
            optimizer: PyTorch optimizer

        Returns:
            float: Current learning rate
        """
        for param_group in optimizer.param_groups:
            return param_group["lr"]
        return 0.0

    @staticmethod
    def set_learning_rate(optimizer: torch.optim.Optimizer, lr: float) -> None:
        """
        Set learning rate for all parameter groups.

        Args:
            optimizer: PyTorch optimizer
            lr: New learning rate
        """
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

    @staticmethod
    def create_model_copy(model: nn.Module, deepcopy: bool = True) -> nn.Module:
        """
        Create a copy of a model.

        Args:
            model: PyTorch model
            deepcopy: If True, copy weights as well

        Returns:
            nn.Module: Copied model
        """
        if deepcopy:
            import copy
            return copy.deepcopy(model)
        return model

    @staticmethod
    def average_models(models: List[nn.Module], weights: Optional[List[float]] = None) -> nn.Module:
        """
        Average the weights of multiple models (model averaging).

        Args:
            models: List of PyTorch models
            weights: Optional weights for weighted averaging

        Returns:
            nn.Module: Averaged model
        """
        if not models:
            raise ValueError("No models to average")

        if weights is None:
            weights = [1.0 / len(models)] * len(models)

        avg_model = models[0]
        avg_dict = avg_model.state_dict()

        for key in avg_dict:
            avg_dict[key] = avg_dict[key] * weights[0]
            for i in range(1, len(models)):
                avg_dict[key] += models[i].state_dict()[key] * weights[i]

        avg_model.load_state_dict(avg_dict)
        return avg_model

    @staticmethod
    def prune_model(
        model: nn.Module,
        prune_ratio: float = 0.3,
        method: str = "magnitude"
    ) -> int:
        """
        Prune model weights.

        Args:
            model: PyTorch model
            prune_ratio: Ratio of weights to prune
            method: Pruning method ('magnitude' or 'random')

        Returns:
            int: Number of pruned weights
        """
        total_pruned = 0
        for name, param in model.named_parameters():
            if "weight" in name and param.dim() > 1:
                if method == "magnitude":
                    threshold = torch.quantile(
                        param.abs().flatten(), prune_ratio
                    )
                    mask = param.abs() > threshold
                else:
                    mask = torch.rand_like(param) > prune_ratio

                param.data *= mask.float()
                total_pruned += (mask == 0).sum().item()

        return total_pruned


import os

