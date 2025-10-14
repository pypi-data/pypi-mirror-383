from enum import Enum


class LOSS_KEYS(str, Enum):
    """Module loss keys."""

    L1 = "l1_loss"
    PERCEPTUAL = "perceptual_loss"
