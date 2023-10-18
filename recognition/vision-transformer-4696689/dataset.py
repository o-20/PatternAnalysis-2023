"""
Imports Here
"""
"""numpy and torch"""
import numpy as np
import torch

"""PIL"""
from PIL import Image

"""torchvision and utils"""
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset

"""os"""
import os

"""
Loading data from local file
"""

"""Assumes images have pixel values in range [0,255]"""
def getImages(trainDIRs, testDIRS):
    """Get image to tensor"""
    transform = transforms.Compose([
        transforms.PILToTensor()
    ])
    """Loading data into arrays"""
    xtrain, xtrain, xtest, ytest = [], [], [], []
    """training data"""
    size = [0, 0]
    for i, DIR in enumerate(trainDIRs):
        for filename in os.listdir(DIR):
            f = os.path.join(DIR, filename)
            img = Image.open(f)
            tensor = transform(img).float()
            tensor.require_grad = True
            xtrain.append(tensor/255)
            size[i] += 1
    xtrain = torch.stack(xtrain)
    ytrain = torch.from_numpy(np.concatenate((np.ones(size[0]), np.zeros(size[1])), axis=0))
    """testing data"""
    size = [0, 0]
    for i, DIR in enumerate(testDIRs):
        for filename in os.listdir(DIR):
            f = os.path.join(DIR, filename)
            img = Image.open(f)
            tensor = transform(img).float()
            tensor.require_grad = True
            xtest.append(tensor/255)
            size[i] += 1
    xtest = torch.stack(xtest)
    ytest = torch.from_numpy(np.concatenate((np.ones(size[0]), np.zeros(size[1])), axis=0))
    return xtrain, ytrain, xtest, ytest

def createPatches(imgs, patchsize):
    (N, C, W, H) = imgs.shape
    (wsize, hsize) = patchsize
    """check for errors with sizing"""
    if (W % wsize != 0) or (H % hsize != 0):
        raise Exception("patchsize is not appropriate")
    if (C != C) or (H != H):
        raise Exception("given sizes do not match")
    size = (N, C, W // wsize, wsize, H // hsize, hsize)
    perm = (0, 2, 4, 1, 3, 5) #bring col, row index of patch to front
    flat = (1, 2) #flatten (col, row) index into col*row entry index for patches
    imgs = imgs.reshape(size).permute(perm).flatten(*flat)
    return imgs #in format Nimgs, Npatches, C, Wpatch, Hpatch
    
def flattenPatches(imgs): #takes input (N, Npatches, C, W, H)
    return imgs.flatten(2, 4)

"""
Dataloader
"""

class DatasetWrapper(Dataset):
    def __init__(self, X, y=None):
        self.X, self.y = X, y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is None:
            return self.X[idx]
        else:
            return self.X[idx], self.y[idx]
        
trainDIRs = ['../../../AD_NC/train/AD/', '../../../AD_NC/train/NC']
testDIRs = ['../../../AD_NC/test/AD/', '../../../AD_NC/test/NC']
xtrain, ytrain, xtest, ytest = getImages(trainDIRs, testDIRs)
xtrain = flattenPatches(createPatches(xtrain, (16,16)))
xtest = flattenPatches(createPatches(xtest, (16,16)))

def trainloader(batchsize=16):
    return DataLoader(DatasetWrapper(xtrain, ytrain), batch_size=batchsize, shuffle=True)

def testloader():
    return DataLoader(DatasetWrapper(xtest, ytest), batch_size=1, shuffle=True)

def trainshape():
    return xtrain.shape[1:]

def testshape():
    return xtest.shape