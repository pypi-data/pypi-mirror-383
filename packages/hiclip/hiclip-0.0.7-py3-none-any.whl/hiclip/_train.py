from typing import Dict, List, Union

import numpy as np
import torch
from scvi.train import TrainingPlan
from torch.optim.lr_scheduler import CosineAnnealingLR, StepLR

from ._constants import LOSS_KEYS
from ._module import HiClipModule
from ._utils import hiclip_metric


class HiClipTrainingPlan(TrainingPlan):
    """Training plan for the hiclip model."""

    def __init__(
        self,
        module: HiClipModule,
        n_epochs_warmup: Union[int, None] = None,
        checkpoint_freq: int = 20,
        lr=1e-4,
        weight_decay=1e-4,
        step_size_lr: int = 4,
        cosine_scheduler: bool = False,
        scheduler_max_epochs: int = 1000,
        scheduler_final_lr: float = 1e-5,
    ):
        super().__init__(
            module=module,
            lr=lr,
            weight_decay=weight_decay,
            n_epochs_kl_warmup=None,
            reduce_lr_on_plateau=False,
            lr_factor=None,
            lr_patience=None,
            lr_threshold=None,
            lr_scheduler_metric=None,
            lr_min=None,
        )

        self.n_epochs_warmup = n_epochs_warmup if n_epochs_warmup is not None else 0

        self.checkpoint_freq = checkpoint_freq

        self.scheduler = CosineAnnealingLR if cosine_scheduler else StepLR
        self.scheduler_params = (
            {"T_max": scheduler_max_epochs, "eta_min": scheduler_final_lr}
            if cosine_scheduler
            else {"step_size": step_size_lr}
        )

        self.step_size_lr = step_size_lr

        self.automatic_optimization = False
        self.iter_count = 0
        self.training_step_outputs = []
        self.validation_step_outputs = []
        self._epoch_keys = []

        self.epoch_keys = [
            "hiclip_metric",
            LOSS_KEYS.L1,
            LOSS_KEYS.PERCEPTUAL,
        ]

        self.epoch_history = {"mode": [], "epoch": []}
        for key in self.epoch_keys:
            self.epoch_history[key] = []

    def configure_optimizers(self):
        """Set up optimizers."""
        optimizers = []
        schedulers = []

        optimizers.append(
            torch.optim.Adam(
                [
                    {
                        "params": list(
                            filter(
                                lambda p: p.requires_grad,
                                self.module.parameters(),
                            )
                        ),
                        "lr": self.lr,
                        "weight_decay": self.weight_decay,
                        # betas=(0.5, 0.999),
                    }
                ]
            )
        )

        if self.step_size_lr is not None:
            for optimizer in optimizers:
                schedulers.append(self.scheduler(optimizer, **self.scheduler_params))
            return optimizers, schedulers
        else:
            return optimizers

    @property
    def epoch_keys(self):
        """Epoch keys getter."""
        return self._epoch_keys

    @epoch_keys.setter
    def epoch_keys(self, epoch_keys: List):
        self._epoch_keys.extend(epoch_keys)

    def training_step(self, batch):
        """Training step."""
        optimizers = self.optimizers()
        if not isinstance(optimizers, list):
            optimizers = [optimizers]
        # model update
        for optimizer in optimizers:
            optimizer.zero_grad()

        _, losses = self.module.forward(batch)

        self.manual_backward(losses[LOSS_KEYS.L1])
        self.manual_backward(losses[LOSS_KEYS.PERCEPTUAL])
        for optimizer in optimizers:
            optimizer.step()

        results = {
            LOSS_KEYS.L1: losses[LOSS_KEYS.L1].item(),
            LOSS_KEYS.PERCEPTUAL: losses[LOSS_KEYS.PERCEPTUAL].item(),
        }

        self.iter_count += 1

        for key in self.epoch_keys:
            if key not in results:
                results.update({key: 0.0})

        self.training_step_outputs.append(results)
        return results

    def on_train_epoch_end(self):
        """Training epoch end."""
        outputs = self.training_step_outputs
        self.epoch_history["epoch"].append(self.current_epoch)
        self.epoch_history["mode"].append("train")

        for key in self.epoch_keys:
            self.epoch_history[key].append(np.mean([output[key] for output in outputs]))
            self.log(key, self.epoch_history[key][-1], prog_bar=True)

        if self.current_epoch > 1 and self.current_epoch % self.step_size_lr == 0:
            schedulers = self.lr_schedulers()
            if not isinstance(schedulers, list):
                schedulers = [schedulers]
            for scheduler in schedulers:
                scheduler.step()

        self.training_step_outputs.clear()

    def validation_step(self, batch, batch_idx):
        """Validation step."""
        _, losses = self(batch)

        results = {}
        for key in losses:
            results.update({key: losses[key].item()})

        results.update(
            {
                "hiclip_metric": hiclip_metric(
                    results[LOSS_KEYS.L1], results[LOSS_KEYS.PERCEPTUAL]
                )
            }
        )

        self.validation_step_outputs.append(results)
        return results

    def on_validation_epoch_end(self):
        """Validation step end."""
        outputs = self.validation_step_outputs
        self.epoch_history["epoch"].append(self.current_epoch)
        self.epoch_history["mode"].append("valid")
        for key in self.epoch_keys:
            self.epoch_history[key].append(np.mean([output[key] for output in outputs]))
            self.log(f"val_{key}", self.epoch_history[key][-1], prog_bar=True)

        self.validation_step_outputs.clear()

    def test_step(self, batch, batch_idx):
        """Test step."""
        return self.validation_step(batch, batch_idx)

    def test_epoch_end(self, outputs):
        """Test step end."""
        self.epoch_history["epoch"].append(self.current_epoch)
        self.epoch_history["mode"].append("test")
        for key in self.epoch_keys:
            self.epoch_history[key].append(np.mean([output[key] for output in outputs]))
            self.log(f"test_{key}", self.epoch_history[key][-1], prog_bar=True)
