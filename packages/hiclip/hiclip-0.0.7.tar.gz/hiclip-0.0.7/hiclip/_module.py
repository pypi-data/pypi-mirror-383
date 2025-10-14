from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np
import torch
from scvi import REGISTRY_KEYS, settings
from scvi.module.base import BaseModuleClass, LossOutput, auto_move_data
from torch import nn

from ._constants import LOSS_KEYS
from ._utils import _logger, tensor2mat
from .Torchelie.torchelie.loss import PerceptualLoss


class DoubleConv(nn.Module):
    def __init__(
        self, in_ch: int, out_ch: int, kernel_size: int = 3, padding_size: int = 1
    ):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size, padding=padding_size),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size, padding=padding_size),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, input):
        return self.conv(input)


class DownConv(nn.Module):
    def __init__(
        self, in_ch: int, out_ch: int, kernel_size: int = 3, padding_size: int = 1
    ):
        super(DownConv, self).__init__()
        self.conv = nn.Sequential(
            nn.MaxPool2d(2), DoubleConv(in_ch, out_ch, kernel_size, padding_size)
        )

    def forward(self, input):
        return self.conv(input)


class UpConv(nn.Module):
    def __init__(
        self, in_ch: int, out_ch: int, kernel_size: int = 3, padding_size: int = 1
    ):
        super(UpConv, self).__init__()
        self.up = nn.ConvTranspose2d(in_ch, out_ch, 2, stride=2)
        self.conv = DoubleConv(in_ch, out_ch, kernel_size, padding_size)

    def forward(self, input1, input2):
        return self.conv(torch.cat([self.up(input1), input2], dim=1))


class HiClipModule(BaseModuleClass):
    def __init__(
        self,
        main_loc: str,
        sub_loc: str,
        target_loc: str,
        main_channel: List = [1, 64, 128, 256, 128, 64],
        sub_channel: List = [1, 16, 32, 64],
        out_channel: List = [128, 64, 1],
        main_conv: List = [
            (3, 1),
            ((5, 1), (2, 0)),
            ((1, 5), (0, 2)),
            ((5, 1), (2, 0)),
            ((1, 5), (0, 2)),
        ],
        sub_conv: List = [(1, 0), (1, 0), (1, 0)],
        out_conv: List = [(3, 1), (1, 0)],
        seed: int = 0,
    ):
        super().__init__()

        assert len(main_channel) == len(main_conv) + 1
        assert len(sub_channel) == len(sub_conv) + 1
        assert len(out_channel) == len(out_conv) + 1

        assert len(main_channel) % 2 == 0
        assert main_channel[-1] + sub_channel[-1] == out_channel[0]

        torch.manual_seed(seed)
        np.random.seed(seed)
        settings.seed = seed

        self.main_loc, self.sub_loc, self.target_loc = main_loc, sub_loc, target_loc

        self.main_depths = int((len(main_conv) - 1) / 2)
        self.main_modules = [
            DoubleConv(
                main_channel[0], main_channel[1], main_conv[0][0], main_conv[0][1]
            )
        ]
        for i in range(self.main_depths):
            _i = 1 + i
            self.main_modules.append(
                DownConv(
                    main_channel[_i],
                    main_channel[_i + 1],
                    main_conv[_i][0],
                    main_conv[_i][1],
                )
            )
        for i in range(self.main_depths):
            _i = 1 + self.main_depths + i
            self.main_modules.append(
                UpConv(
                    main_channel[_i],
                    main_channel[_i + 1],
                    main_conv[_i][0],
                    main_conv[_i][1],
                )
            )
        self.main_modules = nn.ModuleList(self.main_modules)
        self.sub_modules = nn.ModuleList(
            [
                DoubleConv(
                    sub_channel[i], sub_channel[i + 1], sub_conv[i][0], sub_conv[i][1]
                )
                for i in range(len(sub_conv))
            ]
        )
        self.out_modules = nn.ModuleList(
            [
                DoubleConv(
                    out_channel[i], out_channel[i + 1], out_conv[i][0], out_conv[i][1]
                )
                for i in range(len(out_conv))
            ]
        )

        self.L1_loss = nn.L1Loss(reduction="mean")
        self.perceptual_loss_layers = [
            "conv1_1",
            "relu1_1",
            "conv1_2",
            "relu1_2",
            "maxpool1",
            "conv2_1",
            "relu2_1",
            "conv2_2",
            "relu2_2",
            "maxpool2",
            "conv3_1",
            "relu3_1",
            "conv3_2",
            "relu3_2",
            "conv3_3",
            "relu3_3",
            "conv3_4",
            "relu3_4",
            "maxpool3",  # noqa: E131
            "conv4_1",
            "relu4_1",
            "conv4_2",
            "relu4_2",
            "conv4_3",
            "relu4_3",
            "conv4_4",
            "relu4_4",
            "maxpool4",  # noqa: E131
            "conv5_1",
            "relu5_1",
            "conv5_2",
            "relu5_2",
            "conv5_3",
            "relu5_3",
            "conv5_4",
            "relu5_4",  # 'maxpool5'
        ]

    def _get_inference_input(self, tensors: Dict[Any, Any], **kwargs):
        main = tensors[self.main_loc]  # [batch_size, interactions]
        sub = tensors[self.sub_loc]  # [batch_size, interactions]
        # sample_indices = tensors[REGISTRY_KEYS.INDICES_KEY].long().ravel()

        main = torch.unsqueeze(tensor2mat(main), 1)
        sub = torch.unsqueeze(tensor2mat(sub), 1)

        input_dict = {
            "main": main,
            "sub": sub,
        }
        return input_dict

    @auto_move_data
    def inference(
        self,
        main: torch.Tensor,
        sub: torch.Tensor,
    ):
        # main = self.main_modules[0](main)
        mains = []
        for i in range(self.main_depths):
            main = self.main_modules[i](main)
            mains.append(main)
        main = self.main_modules[self.main_depths](main)
        for i in range(self.main_depths):
            main = self.main_modules[1 + self.main_depths + i](main, mains[-i - 1])

        for module in self.sub_modules:
            sub = module(sub)

        out = torch.cat([main, sub], dim=1)
        for module in self.out_modules:
            out = module(out)

        out = nn.ReLU()(out)
        return out

    @auto_move_data
    def loss(
        self,
        tensors: Dict[str, torch.Tensor],
        inference_output: torch.Tensor,
    ) -> Dict[str, float]:
        losses = dict()
        target = tensors[self.target_loc]
        target = torch.unsqueeze(tensor2mat(target), 1)

        target_is_0, target_is_not_0 = target == 0, target != 0

        losses[LOSS_KEYS.L1] = self.L1_loss(
            inference_output[target_is_not_0], target[target_is_not_0]
        )

        _output, _target = inference_output.clone().detach(), target.clone().detach()
        _output[target_is_0], _target[target_is_0] = 0, 0
        losses[LOSS_KEYS.PERCEPTUAL] = PerceptualLoss(
            self.perceptual_loss_layers,
            rescale=True,
        ).to(inference_output.device)(_output, _target)

        return losses

    @auto_move_data
    def forward(
        self,
        tensors,
        compute_loss=True,
    ) -> Union[tuple[torch.Tensor], tuple[torch.Tensor, LossOutput]]:
        inference_inputs = self._get_inference_input(tensors)
        inference_output = self.inference(**inference_inputs)

        if compute_loss:
            losses = self.loss(tensors, inference_output)
            return inference_output, losses
        else:
            return inference_output
