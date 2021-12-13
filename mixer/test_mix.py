import numpy as np
import torch
import math
import pprint
import copy
from matplotlib.pyplot import box
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model

def test_mix( models, filename ):
    parts0 = models[4].components
    parts1 = models[4].components
    parts2 = models[4].components
    parts3 = models[4].components

    test_parts = []
    test_parts += [ parts0["objs"]["back"] ]
    test_parts += [ parts1["objs"]["seat"] ]
    test_parts += parts2["objs"]["legs"]
    test_parts += parts3["objs"]["arm_rests"]
    test_obj = SimpleObj.merge_objs( test_parts )
    SimpleObj.save( filename, test_obj )
