from __future__ import annotations

import torch
from torch.nn import Module
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader

from einops import pack, unpack

from accelerate import Accelerator

# ema - apparently greatly helped with results

from ema_pytorch import EMA

from tiny_recursive_model.trm import TinyRecursiveModel

# helpers

def range_from_one(n):
    return range(1, n + 1)

def is_empty(t):
    return t.numel() == 0

# trainer

def newtonschulz5(
    t,
    steps = 5,
    eps = 1e-7,
    coefs = (3.4445, -4.7750, 2.0315)
):
    if t.ndim <= 3:
        return t

    shape = t.shape
    should_transpose = shape[-2] > shape[-1]

    if should_transpose:
        t = t.transpose(-1, -2)

    t, packed_shape = pack([t], '* i j')
    t = t / t.norm(dim = (-1, -2), keepdim = True).clamp(min = eps)

    a, b, c = coefs

    for _ in range(steps):
        A = t @ t.transpose(-1, -2)
        B = b * A + c * A @ A
        t = a * t + B @ t

    t, = unpack(t, packed_shape, '* i j')

    if should_transpose:
        t = t.transpose(-1, -2)

    return t

class Trainer(Module):
    def __init__(
        self,
        model: TinyRecursiveModel | Module,
        dataset: Dataset,
        optim_klass = AdamW,
        learning_rate = 1e-4,
        weight_decay = 1.,
        batch_size = 16,
        epochs = 2,
        halt_prob_thres = 0.5,
        max_recurrent_steps = 12,
        ema_decay_rate = 0.999,
        switch_ema_every = 10000,           # switch ema https://arxiv.org/abs/2402.09240
        accelerate_kwargs: dict = dict(),
        cpu = False
    ):
        super().__init__()

        self.accelerator  = Accelerator(**accelerate_kwargs, cpu = cpu)

        self.batch_size = batch_size
        self.epochs = epochs

        self.dataset = dataset
        self.dataloader = dataloader = DataLoader(self.dataset, batch_size = self.batch_size, shuffle = True)

        self.optim = optim_klass(
            model.parameters(),
            lr = learning_rate,
            weight_decay = weight_decay
        )

        self.model = model

        # ema model

        self.ema_model = None

        if self.accelerator.is_main_process:
            self.ema_model = EMA(
                model,
                beta = ema_decay_rate,
                update_model_with_ema_every = switch_ema_every,
                forward_method_names = ('predict',)
            )

        # recurrent and act related variables

        self.halt_prob_thres = halt_prob_thres

        self.max_recurrent_steps = max_recurrent_steps

        # prepare maybe distributed

        self.model, self.optim, self.dataloader = self.accelerator.prepare(self.model, self.optim, self.dataloader)

    def forward(self):

        for epoch in range_from_one(self.epochs):

            for dataset_input, dataset_output in self.dataloader:

                outputs, latents = self.model.get_initial()

                for recurrent_step in range_from_one(self.max_recurrent_steps):

                    loss, (main_loss, halt_loss), outputs, latents, pred, halt = self.model(dataset_input, outputs, latents, labels = dataset_output)

                    self.accelerator.print(f'[{epoch} ({recurrent_step} / {self.max_recurrent_steps})] loss: {main_loss.mean().item():.3f} | halt loss: {halt_loss.mean().item():.3f}')

                    self.accelerator.backward(loss)

                    self.optim.step()
                    self.optim.zero_grad()

                    if self.accelerator.is_main_process:
                        self.ema_model.update()

                    # handle halting

                    halt_mask = halt >= self.halt_prob_thres

                    if not halt_mask.any():
                        continue

                    outputs = outputs[~halt_mask]
                    latents = latents[~halt_mask]
                    dataset_input = dataset_input[~halt_mask]
                    dataset_output = dataset_output[~halt_mask]

                    if is_empty(outputs):
                        break

        self.accelerator.print('complete')

        if self.accelerator.is_main_process:
            self.ema_model.copy_params_from_ema_to_model()
