"""
BLACK VEIL V5 - PyTorch Utilities
Common PyTorch helpers for model management
"""
import torch
import torch.nn as nn
import random
import numpy as np
import os
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path


def get_device() -> torch.device:
    """
    Get the optimal device for PyTorch operations.

    Returns:
        torch.device: Optimal device
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch, "mps") and torch.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_seed(seed: int = 42) -> None:
    """
    Set random seed for reproducibility.

    Args:
        seed: Random seed
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    metrics: Dict[str, float],
    path: str,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
) -> None:
    """
    Save training checkpoint.

    Args:
        model: PyTorch model
        optimizer: Optimizer
        epoch: Current epoch
        metrics: Training metrics
        path: Save path
        scheduler: Optional learning rate scheduler
    """
    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "metrics": metrics,
    }
    if scheduler:
        checkpoint["scheduler_state_dict"] = scheduler.state_dict()

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    torch.save(checkpoint, path)


def load_checkpoint(
    model: nn.Module,
    path: str,
    optimizer: Optional[torch.optim.Optimizer] = None,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """
    Load training checkpoint.

    Args:
        model: PyTorch model
        path: Checkpoint path
        optimizer: Optional optimizer to load state
        device: Device to load to

    Returns:
        Dict[str, Any]: Checkpoint data
    """
    if device is None:
        device = get_device()

    checkpoint = torch.load(path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])

    if optimizer and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    return checkpoint


def count_parameters(model: nn.Module) -> int:
    """
    Count trainable parameters in a model.

    Args:
        model: PyTorch model

    Returns:
        int: Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_model_size(model: nn.Module) -> float:
    """
    Get model size in MB.

    Args:
        model: PyTorch model

    Returns:
        float: Model size in MB
    """
    param_size = sum(p.numel() * p.element_size() for p in model.parameters())
    buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
    total_size = (param_size + buffer_size) / (1024 * 1024)
    return round(total_size, 2)


def create_optimizer(
    model: nn.Module,
    optimizer_type: str = "adam",
    learning_rate: float = 0.001,
    weight_decay: float = 1e-5,
    **kwargs
) -> torch.optim.Optimizer:
    """
    Create optimizer for model training.

    Args:
        model: PyTorch model
        optimizer_type: Optimizer type
        learning_rate: Learning rate
        weight_decay: Weight decay
        **kwargs: Additional optimizer arguments

    Returns:
        torch.optim.Optimizer: Created optimizer

    Raises:
        ValueError: If optimizer type is not supported
    """
    optimizer_map = {
        "adam": torch.optim.Adam,
        "adamw": torch.optim.AdamW,
        "sgd": torch.optim.SGD,
        "adamax": torch.optim.Adamax,
        "rmsprop": torch.optim.RMSprop,
    }

    if optimizer_type not in optimizer_map:
        raise ValueError(f"Unsupported optimizer: {optimizer_type}")

    optimizer_class = optimizer_map[optimizer_type]
    return optimizer_class(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
        **kwargs
    )


def create_scheduler(
    optimizer: torch.optim.Optimizer,
    scheduler_type: str = "cosine",
    **kwargs
) -> torch.optim.lr_scheduler._LRScheduler:
    """
    Create learning rate scheduler.

    Args:
        optimizer: Optimizer
        scheduler_type: Scheduler type
        **kwargs: Additional scheduler arguments

    Returns:
        torch.optim.lr_scheduler._LRScheduler: Created scheduler

    Raises:
        ValueError: If scheduler type is not supported
    """
    scheduler_map = {
        "cosine": torch.optim.lr_scheduler.CosineAnnealingLR,
        "step": torch.optim.lr_scheduler.StepLR,
        "multistep": torch.optim.lr_scheduler.MultiStepLR,
        "exponential": torch.optim.lr_scheduler.ExponentialLR,
        "reduce_on_plateau": torch.optim.lr_scheduler.ReduceLROnPlateau,
        "one_cycle": torch.optim.lr_scheduler.OneCycleLR,
    }

    if scheduler_type not in scheduler_map:
        raise ValueError(f"Unsupported scheduler: {scheduler_type}")

    scheduler_class = scheduler_map[scheduler_type]
    return scheduler_class(optimizer, **kwargs)


def to_numpy(tensor: torch.Tensor) -> np.ndarray:
    """
    Convert PyTorch tensor to numpy array.

    Args:
        tensor: PyTorch tensor

    Returns:
        np.ndarray: Numpy array
    """
    return tensor.detach().cpu().numpy()


def to_tensor(
    array: np.ndarray,
    device: Optional[torch.device] = None,
    dtype: Optional[torch.dtype] = None
) -> torch.Tensor:
    """
    Convert numpy array to PyTorch tensor.

    Args:
        array: Numpy array
        device: Target device
        dtype: Target data type

    Returns:
        torch.Tensor: PyTorch tensor
    """
    if device is None:
        device = get_device()

    tensor = torch.from_numpy(array)
    if dtype:
        tensor = tensor.to(dtype)
    return tensor.to(device)


def init_weights(model: nn.Module, init_type: str = "xavier") -> None:
    """
    Initialize model weights.

    Args:
        model: PyTorch model
        init_type: Initialization type
    """
    def _init_weights(m: nn.Module) -> None:
        if isinstance(m, (nn.Linear, nn.Conv1d, nn.Conv2d)):
            if init_type == "xavier":
                nn.init.xavier_uniform_(m.weight)
            elif init_type == "kaiming":
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
            elif init_type == "normal":
                nn.init.normal_(m.weight, mean=0, std=0.01)
            elif init_type == "orthogonal":
                nn.init.orthogonal_(m.weight)

            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

        elif isinstance(m, (nn.BatchNorm1d, nn.BatchNorm2d)):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)

        elif isinstance(m, nn.LSTM):
            for name, param in m.named_parameters():
                if "weight_ih" in name:
                    nn.init.xavier_uniform_(param)
                elif "weight_hh" in name:
                    nn.init.orthogonal_(param)
                elif "bias" in name:
                    nn.init.constant_(param, 0)

    model.apply(_init_weights)
