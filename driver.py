import numpy as np
import torch
import math
import pprint
import copy
from matplotlib.pyplot import box
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model
import pprint

from mixer.test_mix import test_mix
from mixer.mixer import random_choose

if __name__ == "__main__":
    # ------------------- Parser -------------------------
    # 66, 4037, 2177
    # 6012, 3453, 3336, 2234, 1392
    # 653, 18, 734, 1791, 2207, 3663, 4903, 2428, 722, 4294

    models = Model.load_models([2177]) # you should be passing the output here into the mixer

    for i,model in enumerate(models):
        parts = model.components

        # 1.
        # all you should care about from the Models class is the .components variable as that will contain all 
        # part Objs and centers for transformations
        # pprint.pprint(model.components) 

        # 2.
        # You can use this nifty save function from the SimpleObj class
        # Note: the save function takes in a type of SimpleObj

        # SimpleObj.save("back-{}".format(i), parts["objs"]["back"]) # this will save the back component of a chair

        # 3.
        # You can also merge SimpleObjs like this...
        # back_and_seat_obj = SimpleObj.merge_objs([parts["objs"]["back"], parts["objs"]["seat"]]) # this will merge the back and seat SimpleObjects
        # SimpleObj.save("back-and-seat-{}".format(i), back_and_seat_obj)
        # SimpleObj.save("back-{}".format(i), parts["objs"]["back"]) # this will save the back component of a chair

    # ------------------- Mixer -------------------------
    # the the function below hasnt been created yet, make sure to put your mixer logic in the .mixer/ folder 
    # mixer_result = Mixer.create_new_chair(models)


    test_mix( models )
    random_choose( models )

