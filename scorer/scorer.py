# -*- coding: utf-8 -*-
"""Scorer.ipynb
"""
import numpy as np
import os
import cv2
import pprint

from torch.utils.data import TensorDataset, DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as nnf
import torch.optim as optim
from torchvision import transforms

from .model import PreTrainedResNet

# USE THESE PARAMS FOR FIXED RESNET
NUM_EPOCHS = 3
LEARNING_RATE = 0.001 
BATCH_SIZE = 8
RESNET_LAST_ONLY = False

# start the model
CLASSES = ["probable", "not-probable"]

'''
load chair dataset. Dimension refers to the target dimension of the output image, used to save up memory.
The images are originally 224x224.

There are opportunities to improve the dataset by performing image operations to augment the dataset and generating
more negative samples based on the given meshes.
'''
BASE_DIR = "./scorer/"
IM_SIZE = 64

train_transform = transforms.Compose([
    transforms.ToTensor()  
])

def load_train_data(dimension):
    imagesTop = []
    imagesSide = []
    imagesFront = []
    isPositive = False

    ls = 0

    for id, folder in enumerate([os.path.join(BASE_DIR, "positive/"), os.path.join(BASE_DIR, "negative/")]):
        isPositive = not isPositive

        length = len(os.listdir(folder)) // 3
        ls += length

        files = os.listdir(folder)
        files.sort()

        for filename in files:

            view = int(filename.split(".")[0])
            view = view % 3
            img = cv2.imread(folder+filename)
            if dimension < 224:
                img = cv2.resize(img, dsize=(dimension, dimension), interpolation=cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = np.nan_to_num(img)

            if img is not None:
                if view == 2:
                    imagesSide.append(1. - img / 255.)
                elif view == 0:
                    imagesTop.append(1. - img / 255.)
                else:
                    imagesFront.append(1. - img / 255.)

        if isPositive:
            y_vec_top = np.ones((length), dtype=np.int)
            y_vec_side = np.ones((length), dtype=np.int)
            y_vec_front = np.ones((length), dtype=np.int)
        else:
            y_vec_top = np.append(y_vec_top, np.zeros((length), dtype=np.int), axis=0 )
            y_vec_side = np.append(y_vec_side, np.zeros((length), dtype=np.int), axis=0 )
            y_vec_front = np.append(y_vec_front, np.zeros((length), dtype=np.int), axis=0 )

    imagesTop = np.array(imagesTop)
    imagesFront = np.array(imagesFront)
    imagesSide = np.array(imagesSide)

    #flatten the images
    # imagesTop = np.reshape(imagesTop, (ls, dimension * dimension))
    # imagesFront = np.reshape(imagesFront, (ls, dimension * dimension))
    # imagesSide = np.reshape(imagesSide, (ls, dimension * dimension))

    seed = 547
    np.random.seed(seed)
    np.random.shuffle(imagesTop)
    np.random.seed(seed)
    np.random.shuffle(imagesFront)
    np.random.seed(seed)
    np.random.shuffle(imagesSide)

    np.random.seed(seed)
    np.random.shuffle(y_vec_top)
    np.random.seed(seed)
    np.random.shuffle(y_vec_front)
    np.random.seed(seed)
    np.random.shuffle(y_vec_side)

    return imagesTop, imagesFront, imagesSide, y_vec_top, y_vec_front, y_vec_side

def load_train():
    # create the dataloaders for the model
    imagesTop, imagesFront, imagesSide, y_vec_top, y_vec_front, y_vec_side = load_train_data(IM_SIZE)
    y_vec_top   = [[_] for _ in y_vec_top]
    y_vec_front = [[_] for _ in y_vec_front]
    y_vec_side  = [[_] for _ in y_vec_side]

    top_dataset   = TensorDataset(torch.Tensor(imagesTop), torch.Tensor(y_vec_top))
    front_dataset = TensorDataset(torch.Tensor(imagesFront), torch.Tensor(y_vec_front))
    side_dataset  = TensorDataset(torch.Tensor(imagesSide), torch.Tensor(y_vec_side))

    tr_top_dataloader   = DataLoader(top_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    tr_front_dataloader = DataLoader(front_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    tr_side_dataloader  = DataLoader(side_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    tr_top_datasize   = len(top_dataset)
    tr_front_datasize = len(front_dataset)
    tr_side_datasize  = len(side_dataset)
    return tr_top_dataloader, tr_front_dataloader, tr_side_dataloader, tr_top_datasize, tr_front_datasize, tr_side_datasize

def train_model(model, optimizer, criterion, epoch, num_epochs, data_loader, data_size):
  model.train()
  epoch_loss = 0.0
  epoch_acc = 0.0

  for batch_idx, (images, labels) in enumerate(data_loader):
    #zero the parameter gradients
    optimizer.zero_grad()
    
    #move to GPU
    images, labels = images.cpu(), labels.cpu()
    images = torch.unsqueeze(images, 1)

    #forward
    outputs = model.forward(images)
    labels = labels.squeeze(1).long()
    loss = criterion(outputs, labels)
    preds = torch.sigmoid(outputs.data)
    _, preds = torch.max(outputs.data, 1)
    
    loss.backward()
    optimizer.step()
    epoch_loss += loss.item()
    epoch_acc += torch.sum(preds == labels).item()
    
  epoch_loss /= data_size
  epoch_acc /= data_size
  
  print('TRAINING Epoch %d/%d Loss %.4f Accuracy %.4f' % (epoch, num_epochs, epoch_loss, epoch_acc))

def init_models():
    models = [PreTrainedResNet(len(CLASSES), RESNET_LAST_ONLY) for _ in range(3)]
    models = [model.cpu() for model in models]
    return models

# save the model
def save_models(models):
    for i,view in enumerate(["top", "front", "side"]):
        torch.save(models[i].state_dict(), "./scorer/models/{}/model".format(view))

def load_models(models):
    for i,view in enumerate(["top", "front", "side"]):
        models[i].load_state_dict(torch.load("./scorer/models/{}/model.zip".format(view), map_location=torch.device("cpu")))

def load_eval_data(dimension):
    imagesTop = []
    imagesSide = []
    imagesFront = []

    ls = 0
    folder = os.path.join(BASE_DIR, "evaluate-chairs/") 

    length = len(os.listdir(folder)) // 3
    ls += length

    files = os.listdir(folder)
    files.sort()
    # files.remove(".DS_Store")
    for filename in files:
        view = filename.split(".")[0].strip()
        if view == "": continue
        view = int(view)
        view = view % 3

        img = cv2.imread(folder+filename)
        if dimension < 224:
            img = cv2.resize(img, dsize=(dimension, dimension), interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.nan_to_num(img)

        #This relies on the files being loaded in order. For that to happen, the 0 padding in the file name is crucial.
        #If you do not have that, then you need to change the logic of this loop.

        if img is not None:
            if view == 2:
                imagesSide.append(1. -img / 255.)
            elif view == 0:
                imagesTop.append(1. -img / 255.)
            else:
                imagesFront.append(1. -img / 255.)

    imagesTop = np.array(imagesTop)
    imagesFront = np.array(imagesFront)
    imagesSide = np.array(imagesSide)
    return imagesTop, imagesFront, imagesSide

def evaluate_model(model, dataloader):
    scores = []
    for batch_idx, ims in enumerate(dataloader):
        ims = ims[0].cpu()
        ims = torch.unsqueeze(ims, 1)
        outputs = model.forward(ims)
        _, preds = torch.max(outputs.data, 1)
        scores.append(preds.item())
    return scores

def load_evaluate():
    image_top_eval, image_front_eval, image_side_eval = load_eval_data(IM_SIZE)
    ev_top_dataset   = TensorDataset(torch.Tensor(image_top_eval))
    ev_front_dataset = TensorDataset(torch.Tensor(image_front_eval))
    ev_side_dataset  = TensorDataset(torch.Tensor(image_side_eval))
    ev_top_dataloader   = DataLoader(ev_top_dataset,   batch_size=1, shuffle=False, num_workers=0)
    ev_front_dataloader = DataLoader(ev_front_dataset, batch_size=1, shuffle=False, num_workers=0)
    ev_side_dataloader  = DataLoader(ev_side_dataset,  batch_size=1, shuffle=False, num_workers=0)
    return ev_top_dataloader, ev_front_dataloader, ev_side_dataloader

def load_single_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, dsize=(IM_SIZE, IM_SIZE), interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = np.nan_to_num(img)
    return 1. -img / 255.

def run_model(model, chair_im):
    """
    evaluates the chair image with a given model
    """
    # convert chair image to a tensor
    chair_tensor = torch.Tensor(chair_im)
    chair_tensor = torch.unsqueeze(chair_tensor, 0)
    chair_tensor = torch.unsqueeze(chair_tensor, 0)

    outputs = model.forward(chair_tensor)
    # print(outputs)
    _, preds = torch.max(outputs.data, 1)

    prob = nnf.softmax(outputs, dim=1)
    prob = prob.detach().numpy()
    # pprint.pprint(prob[0][1])
    # return prob of a good chair
    return prob[0][1]

def score_model(top, front, side):
    models = init_models()
    load_models(models)
    ims = { 
        "top": load_single_image(top), 
        "front": load_single_image(front), 
        "side": load_single_image(side) 
    }

    scores = []
    for mi, view in enumerate(["top", "front", "side"]):
        model = models[mi]
        model.eval()
        score = run_model(models[mi], ims[view])
        scores.append(score)
    scores = np.array(scores, dtype=float)

    print("TOP, FRONT, SIDE")
    # pprint.pprint(scores)
    # print("avg", np.mean(scores))
    # return np.min(scores)
    return np.mean(scores)

def test_train():
    models = init_models()
    # get the training dataset
    tr_top_dataloader, tr_front_dataloader, tr_side_dataloader, tr_top_datasize, tr_front_datasize, tr_side_datasize = load_train()
    tr_data = [
        {"name": "TOP",   "loader": tr_top_dataloader,   "size": tr_top_datasize},
        {"name": "FRONT", "loader": tr_front_dataloader, "size": tr_front_datasize},
        {"name": "SIDE",  "loader": tr_side_dataloader,  "size": tr_side_datasize},
    ]
    for model, dat in zip(models, tr_data):
        # optimizers and criterion
        optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
        criterion = nn.CrossEntropyLoss()
        # criterion = nn.BCELoss()

        print("Training {} model".format(dat["name"]))
        print("-"*30)
        for epoch in range(NUM_EPOCHS):
            train_model(model, optimizer, criterion, epoch+1, NUM_EPOCHS, dat["loader"], dat["size"])
        print("Finsihed Training")
        print("-"*30)

def test_evaluate():
    models = init_models()
    load_models(models)
    ev_top_dataloader, ev_front_dataloader, ev_side_dataloader = load_evaluate()
    ev_dataloaders = {"top": ev_top_dataloader, "front": ev_front_dataloader, "side": ev_side_dataloader}
    all_scores = []
    for mi, view in enumerate(["top", "front", "side"]):
        model = models[mi]
        model.eval()
        view_scores = evaluate_model(models[mi], ev_dataloaders[view])
        all_scores.append(view_scores)
        # scores[mi].append()

# ================= TEST =================
# files = os.listdir("./scorer/evaluate-chairs")
# files.sort()
# files.remove(".DS_Store")
# top = files[2::3]
# front = files[::3]
# side = files[1::3]

# for t, f, s in zip(top, front, side):
#     print(
#         score_model(
#             "./scorer/evaluate-chairs/{}".format(t),
#             "./scorer/evaluate-chairs/{}".format(f),
#             "./scorer/evaluate-chairs/{}".format(s)
#         )
#     )
# ================= TEST =================

