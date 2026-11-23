"""PyTorch implementations of the two paper baselines."""

import torch
from torch import nn
from torch.nn import functional as F


def conv_pair(inputs, outputs, *, kernel=3, batch_norm=False):
    layers = []
    for channels in (inputs, outputs):
        layers.append(nn.Conv2d(channels, outputs, kernel, padding=kernel // 2,
                                bias=not batch_norm))
        if batch_norm:
            layers.append(nn.BatchNorm2d(outputs))
        layers.append(nn.ReLU(inplace=True))
    return nn.Sequential(*layers)


class SqueezeExcite(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.weights = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Conv2d(channels, channels // 16, 1),
            nn.ReLU(inplace=True), nn.Conv2d(channels // 16, channels, 1),
            nn.Sigmoid(),
        )

    def forward(self, features):
        return features * self.weights(features)


class OFCN(nn.Module):
    """Bianchi et al., Figure 3, with one SAR input and one output logit."""

    def __init__(self):
        super().__init__()
        widths = [32, 64, 128, 256, 512]
        self.encoder = nn.ModuleList(
            conv_pair(a, b, batch_norm=True) for a, b in zip([1, *widths], widths)
        )
        self.down = nn.ModuleList(
            nn.Sequential(nn.MaxPool2d(2), SqueezeExcite(width), nn.Dropout(0.1))
            for width in widths[:-1]
        )
        self.decoder = nn.ModuleList()
        for incoming, skip in zip(reversed(widths[1:]), reversed(widths[:-1])):
            last = skip == widths[0]
            self.decoder.append(nn.Sequential(
                nn.Dropout(0.1),
                nn.Conv2d(incoming + skip, skip, 3, padding=1, bias=False),
                nn.BatchNorm2d(skip), nn.ReLU(inplace=True),
                nn.Conv2d(skip, 1 if last else skip, 3, padding=1, bias=False),
                nn.BatchNorm2d(1 if last else skip),
                nn.Identity() if last else nn.ReLU(inplace=True),
            ))

    def forward(self, image):
        skips = []
        for encode, down in zip(self.encoder[:-1], self.down):
            image = encode(image)
            skips.append(image)
            image = down(image)
        image = self.encoder[-1](image)
        for decode, skip in zip(self.decoder, reversed(skips)):
            image = F.interpolate(image, size=skip.shape[-2:], mode='bilinear',
                                  align_corners=False)
            image = decode(torch.cat((image, skip), dim=1))
        return image


class ShabanGate(nn.Module):
    """Two convolutions per block, following the published Conv/ReLU layer counts."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            conv_pair(3, 32, kernel=11), nn.MaxPool2d(2),
            conv_pair(32, 64, kernel=9), nn.MaxPool2d(2),
            conv_pair(64, 128, kernel=7), nn.MaxPool2d(2),
        )
        widths = [128 * 8 * 8, 128, 64, 32, 16]
        classifier = [nn.Flatten()]
        for inputs, outputs in zip(widths, widths[1:]):
            classifier.extend([nn.Linear(inputs, outputs), nn.ReLU(inplace=True)])
        self.classifier = nn.Sequential(*classifier, nn.Linear(widths[-1], 2))

    def forward(self, image):
        return self.classifier(self.features(image))


class ShabanUNet(nn.Module):
    """Five downsampling stages with 64x64 outputs, narrowed for local training."""

    def __init__(self, base=16):
        super().__init__()
        widths = [base * 2**stage for stage in range(6)]
        self.encoder = nn.ModuleList(
            conv_pair(a, b) for a, b in zip([3, *widths], widths)
        )
        self.up = nn.ModuleList()
        self.decoder = nn.ModuleList()
        for incoming, skip in zip(reversed(widths[1:]), reversed(widths[:-1])):
            self.up.append(nn.ConvTranspose2d(incoming, skip, 2, stride=2))
            self.decoder.append(conv_pair(2 * skip, skip))
        self.output = nn.Conv2d(base, 1, 1)

    def forward(self, image):
        skips = []
        for encode in self.encoder[:-1]:
            image = encode(image)
            skips.append(image)
            image = F.max_pool2d(image, 2)
        image = self.encoder[-1](image)
        for up, decode, skip in zip(self.up, self.decoder, reversed(skips)):
            image = decode(torch.cat((up(image), skip), dim=1))
        return self.output(image)


def generalized_dice(logits, mask):
    """Inverse-squared class-volume weights over a minibatch."""
    oil = logits.sigmoid()
    prediction = torch.cat((1 - oil, oil), dim=1)
    target = torch.cat((1 - mask, mask), dim=1)
    dims = (0, 2, 3)
    weights = target.sum(dim=dims).clamp_min(1).reciprocal().square()
    overlap = (prediction * target).sum(dim=dims)
    total = (prediction + target).sum(dim=dims)
    return 1 - 2 * (weights * overlap).sum() / (weights * total).sum().clamp_min(1e-8)
