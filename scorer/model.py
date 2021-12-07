import torch.nn as nn
import torchvision.models as torch_models

"""
This is a custom model that uses a pretrained constructed and pretrained
resnet model provided by pytorch models library
"""
class PreTrainedResNet(nn.Module):
    def __init__(self, num_classes, feature_extracting):
        super(PreTrainedResNet, self).__init__()

        # load pre-trained ResNet Model
        self.resnet = torch_models.resnet18(pretrained=True)

        if feature_extracting:
            for param in self.resnet.parameters():
                param.requires_grad = False

        # replace the FC layer
        num_feats = self.resnet.fc.in_features
        self.input = nn.Conv2d(in_channels=1, out_channels=3, kernel_size=1)
        self.resnet.fc = nn.Linear(in_features=num_feats, out_features=2)

    def forward(self, x):
        x = self.input(x)
        return self.resnet(x)