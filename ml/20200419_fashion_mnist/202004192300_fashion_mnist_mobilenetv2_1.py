#!/usr/bin/env python
# coding: utf-8

import os

import torch
from pytorch_lightning.callbacks import ModelCheckpoint
from torch import nn
from torch.nn import functional as F
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST, FashionMNIST

from argparse import ArgumentParser

import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning import Trainer
from collections import OrderedDict
from torch import optim
import numpy as np
from dataclasses import dataclass
from torchvision.models import MobileNetV2
from torchvision.models.mobilenet import InvertedResidual, _make_divisible, ConvBNReLU
from torchvision.models.resnet import Bottleneck, BasicBlock, conv1x1


def reduce_mean_dicts(list_dicts, key):
    if not list_dicts:
        return 0.

    s = sum([d[key] for d in list_dicts], 0.)
    return s / len(list_dicts)


@dataclass
class Params:
    batch_size_train: int
    batch_size_val: int
    path_data: str
    learning_rate: float


# from pytorch
class MobileNetV2(nn.Module):
    def __init__(self,
                 num_classes=1000,
                 width_mult=1.0,
                 inverted_residual_setting=None,
                 round_nearest=8,
                 block=None):
        """
        MobileNet V2 main class

        Args:
            num_classes (int): Number of classes
            width_mult (float): Width multiplier - adjusts number of channels in each layer by this amount
            inverted_residual_setting: Network structure
            round_nearest (int): Round the number of channels in each layer to be a multiple of this number
            Set to 1 to turn off rounding
            block: Module specifying inverted residual building block for mobilenet

        """
        super(MobileNetV2, self).__init__()

        if block is None:
            block = InvertedResidual
        input_channel = 32
        last_channel = 1280

        if inverted_residual_setting is None:
            inverted_residual_setting = [
                # t, c, n, s
                [1, 16, 1, 1],
                [6, 24, 2, 2],
                [6, 32, 3, 2],
                [6, 64, 4, 2],
                [6, 96, 3, 1],
                [6, 160, 3, 2],
                [6, 320, 1, 1],
            ]

        # only check the first element, assuming user knows t,c,n,s are required
        if len(inverted_residual_setting) == 0 or len(inverted_residual_setting[0]) != 4:
            raise ValueError("inverted_residual_setting should be non-empty "
                             "or a 4-element list, got {}".format(inverted_residual_setting))

        # building first layer
        input_channel = _make_divisible(input_channel * width_mult, round_nearest)
        self.last_channel = _make_divisible(last_channel * max(1.0, width_mult), round_nearest)
        features = [ConvBNReLU(1, input_channel, stride=2)]
        # building inverted residual blocks
        for t, c, n, s in inverted_residual_setting:
            output_channel = _make_divisible(c * width_mult, round_nearest)
            for i in range(n):
                stride = s if i == 0 else 1
                features.append(block(input_channel, output_channel, stride, expand_ratio=t))
                input_channel = output_channel
        # building last several layers
        features.append(ConvBNReLU(input_channel, self.last_channel, kernel_size=1))
        # make it nn.Sequential
        self.features = nn.Sequential(*features)

        # building classifier
        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(self.last_channel, num_classes),
        )

        # weight initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)

    def _forward_impl(self, x):
        # This exists since TorchScript doesn't support inheritance, so the superclass method
        # (this one) needs to have a name other than `forward` that can be accessed in a subclass
        x = self.features(x)
        x = x.mean([2, 3])
        x = self.classifier(x)
        return x

    def forward(self, x):
        return self._forward_impl(x)


class MObileNetV2_1(pl.LightningModule):

    def __init__(self, hparams: Params):
        super().__init__()

        self.hparams = hparams
        self.model = MobileNetV2(num_classes=10,
                                 inverted_residual_setting=[
                                     # t, c, n, s
                                     [1, 16, 1, 1],
                                     [6, 24, 2, 2],
                                     [6, 32, 3, 2],
                                     [6, 64, 4, 2],
                                     [6, 96, 3, 1],
                                     # [6, 160, 3, 2],
                                     # [6, 320, 1, 1],
                                 ]
                                 )
        self.loss = F.cross_entropy
        self.train_dataset = None
        self.val_dataset = None
        
        self.tfms_common = [
            transforms.ToTensor(),
            transforms.Normalize((0.285,), (.3523,))
        ]
        self.tfms_train = [
            transforms.RandomRotation(7., fill=(0,)),
            transforms.RandomCrop(28, padding=3),
        ]
        

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.forward(x)
         
        loss_val = self.loss(y_hat, y, )

        
        tqdm_dict = {'train_loss': loss_val,
                    }
        
        # if batch_idx % 100 == 0:
        #     tqdm_dict['lr'] = np.array(self.trainer.lr_schedulers[0]['scheduler'].get_lr())
            
        return OrderedDict({
            'loss': loss_val,
            'log': tqdm_dict
        })

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.forward(x)

        loss_val = self.loss(y_hat, y, )

        # acc
        labels_hat = torch.argmax(y_hat, dim=1)
        val_acc = torch.sum(y == labels_hat).item() / (len(y) * 1.0)
        val_acc = torch.tensor(val_acc)

        if self.on_gpu:
            val_acc = val_acc.cuda(loss_val.device.index)

        output = OrderedDict({
            'val_loss': loss_val,
            'val_acc': val_acc,
        })

        return output

    def validation_epoch_end(self, outputs):
        loss_mean = reduce_mean_dicts(outputs, 'val_loss')
        acc_mean = reduce_mean_dicts(outputs, 'val_acc')
        tqdm_dict = {
            'val_loss': loss_mean,
            'val_acc': acc_mean
        }
        result = {'progress_bar': tqdm_dict, 'log': tqdm_dict, 'val_loss': loss_mean}
        return result

    def prepare_data(self):

        mnist_train = FashionMNIST(self.hparams.path_data, train=True, download=True,
                                   transform=transforms.Compose(self.tfms_train + self.tfms_common)
                                  )
        mnist_test = FashionMNIST(self.hparams.path_data, train=False, download=True,
                                  transform=transforms.Compose(self.tfms_common)
                                  )

        #         mnist_train, mnist_val = random_split(mnist_train, [55000, 5000])

        self.train_dataset = mnist_train
        self.val_dataset = mnist_test

    def train_dataloader(self):
        if self.train_dataset is None:
            self.prepare_data()
        return DataLoader(self.train_dataset, batch_size=self.hparams.batch_size_train, num_workers=12, shuffle=True)

    def val_dataloader(self):
        if self.val_dataset is None:
            self.prepare_data()
        return DataLoader(self.val_dataset, batch_size=self.hparams.batch_size_val, num_workers=8)

    def test_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.hparams.batch_size_val, num_workers=0)

    def configure_optimizers(self):
        """
        Return whatever optimizers and learning rate schedulers you want here.
        At least one optimizer is required.
        """
        optimizer = optim.SGD(self.parameters(), lr=self.hparams.learning_rate, momentum=0.9)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min')
        # optimizer = optim.Adam(self.parameters(), lr=self.hparams.learning_rate)
        # scheduler = optim.lr_scheduler.OneCycleLR(optimizer, max_lr=self.hparams.learning_rate,
        #                                           steps_per_epoch=1,
        #                                           epochs=self.trainer.max_epochs
        #                                           )
        return [optimizer], [scheduler]

    @staticmethod
    def add_model_specific_args(parent_parser):  # pragma: no-cover
        parser = ArgumentParser(parents=[parent_parser])

        parser.add_argument('--learning_rate', default=0.01, type=float)
        parser.add_argument('--batch_size_train', default=64, type=int)
        parser.add_argument('--batch_size_val', default=32, type=int)
        parser.add_argument('--path_data', default="./data", type=str)

        # training params (opt)
        parser.add_argument('--epochs', default=20, type=int)
        return parser

    def test_step(self, batch, batch_idx):
        """
        Lightning calls this during testing, similar to `validation_step`,
        with the data from the test dataloader passed in as `batch`.
        """
        output = self.validation_step(batch, batch_idx)
        # Rename output keys
        output['test_loss'] = output.pop('val_loss')
        output['test_acc'] = output.pop('val_acc')
        return output

    def test_epoch_end(self, outputs):
        loss_mean = reduce_mean_dicts(outputs, 'test_loss')
        acc_mean = reduce_mean_dicts(outputs, 'test_acc')
        tqdm_dict = {
            'test_loss': loss_mean,
            'test_acc': acc_mean
        }
        result = {'progress_bar': tqdm_dict, 'log': tqdm_dict, 'test_loss': loss_mean}
        return result


def main(hparams):
    model = MObileNetV2_1(hparams)
    name = type(model).__name__
    logger = TensorBoardLogger("lightning_logs", name=name)

    checkpoint_callback = ModelCheckpoint(
        filepath=os.path.join('models', name, name+'_{epoch:02d}-{val_acc:.4f}-{val_loss:.4f}'),
        save_top_k=2,
        verbose=True,
        monitor='val_acc',
        mode='max',
        prefix=''
    )

    trainer = pl.Trainer(
        max_epochs=hparams.epochs,
        gpus=hparams.gpus,
        logger=logger,
        checkpoint_callback=checkpoint_callback,
        # precision=16 if hparams.use_16bit else 32,
        progress_bar_refresh_rate=50,
    )

    trainer.fit(model)

    trainer.test(model)


if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.realpath(__file__))
    parent_parser = ArgumentParser(add_help=False)

    # gpu args
    parent_parser.add_argument(
        '--gpus',
        type=int,
        default=1,
        help='how many gpus'
    )

    parser = MObileNetV2_1.add_model_specific_args(parent_parser)
    hyperparams = parser.parse_args()
    main(hyperparams)
