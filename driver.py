import numpy as np
import math
import pprint
import random
import os
import sys

from parser.parser import SimpleObj, Model
from mixer.test_mix import test_mix
from mixer.mixer import random_choose
from mixer.mixer_v2 import mixer
from scorer.renderer import generate_views
from scorer.scorer import score_model

OUT_DIR = "./output"
# OUT_OBJ_PATH = os.path.join(OUT_DIR, "new_chair")
# from mixer.mixer import mixer 

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("Usage: python3 driver.py <set type> <Number of Outputs>")
        sys.exit(1)
    elif sys.argv[1] not in set(["A","B","C"]):
        print ("Set Index out of range")
        sys.exit(1)

    setIndex = sys.argv[1]
    num_outputs = int(sys.argv[2])

    # ------------------- Parser -------------------------
    example_chairs_symh_id = {
        "A": [66, 4037, 2177],
        "B": [6012, 3453, 3336, 2234, 1392],
        "C": [653, 18, 734, 1791, 2207, 3663, 4903, 2428, 722, 4294]
    }
    final_chairs_symh_id = { # THIS SET IS USED FOR THE PRESENTATION
        "A": [369, 175, 5540],
        "B": [2999, 2150, 3492, 4474, 2160],
        "C": [1919, 3366, 3521, 3204, 1131, 173, 3749, 2313, 5117, 1920]
    }

    # choose some random models from the sets, however you like.
    # you can use random.sample(list, N) to select N items from a list.
    # random.sample(final_chairs_symh_id["C"], 4) <- returns a list of 4 random ids (without repition) from the C set
    # you can implement however you like
    symh_ids = final_chairs_symh_id[setIndex]

    # ======================== PARSER ========================
    print("Reference models chosen: {} (symh_ids)".format(symh_ids))
    print("Loading models...")
    models = Model.load_models(symh_ids)
    # ======================== PARSER ========================

    indexs = []
    probables = []

    for i in range(num_outputs):
        OUT_OBJ_PATH = os.path.join(OUT_DIR, "new_chair_" + str(i))
        # ======================== MIXER =========================
        print("Creating a new chair...")
        # use the models variable to pass into your mixer.
        mixer( models, OUT_OBJ_PATH )
        # ======================== MIXER =========================

        # ====================== RENDERER ========================
        
        # create the 3 view images
        print("Generating TOP, SIDE and FRONT view renders...")
        front_path, side_path, top_path = os.path.join(OUT_DIR, str(i) + "_front.png"), os.path.join(OUT_DIR, str(i) + "_side.png"), os.path.join(OUT_DIR, str(i) + "_top.png")
        generate_views(OUT_OBJ_PATH + '.obj', front_path, side_path, top_path)
        # ====================== RENDERER ========================

        # ======================= SCORER =========================
        # print if the chair generated is probable or not
        print("Scoring chair...")
        probable = score_model(top_path, front_path, side_path)
        print("Probability of a good chair: {}".format(probable))
        print("Output chair -> '{}'".format(OUT_OBJ_PATH))
        indexs.append(i)
        probables.append(probable)
        # ======================= SCORER =========================

    combine = list(zip(indexs, probables))
    combine.sort(key=lambda x:x[1])

    for x in combine:
        print(x[0], x[1])

    # ======================== END ===========================
