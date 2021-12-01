import numpy as np
import torch
import math
import pprint
import copy
from matplotlib.pyplot import box
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model

def test_mix( models ):
    parts0 = models[0].components
    parts1 = models[1].components
    parts2 = models[2].components
    parts3 = models[3].components

    test_parts = []
    test_parts += [ parts0["objs"]["back"] ]
    test_parts += [ parts1["objs"]["seat"] ]
    test_parts += parts2["objs"]["legs"]
    test_parts += parts3["objs"]["arm_rests"]
    print( test_parts )
    test_obj = SimpleObj.merge_objs( test_parts )
    SimpleObj.save( "test_obj", test_obj )
