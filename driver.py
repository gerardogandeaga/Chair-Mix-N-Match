import numpy as np
import math
import pprint
import random
import os

from parser.parser import SimpleObj, Model
from mixer.test_mix import test_mix
from mixer.mixer import random_choose
from mixer.mixer_v2 import mixer
from scorer.renderer import generate_views
from scorer.scorer import score_model

OUT_DIR = "./output"
OUT_OBJ_PATH = os.path.join(OUT_DIR, "new_chair")
# from mixer.mixer import mixer 

if __name__ == "__main__":
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

    # TODO: ABBY and ROSSS
    # choose some random models from the sets, however you like.
    # you can use random.sample(list, N) to select N items from a list.
    # random.sample(final_chairs_symh_id["C"], 4) <- returns a list of 4 random ids (without repition) from the C set
    # you can implement however you like
    symh_ids = random.sample(final_chairs_symh_id["C"], 4)

    # ======================== PARSER ========================
    print("Reference models chosen: {} (symh_ids)".format(symh_ids))
    print("Loading models...")
    models = Model.load_models(symh_ids)
    # ======================== PARSER ========================

    # ======================== MIXER =========================
    print("Creating a new chair...")
    # TODO: ABBY and ROSS
    # use the models variable to pass into your mixer.
    # Mixer.mix(models, OUT_OBJ_PATH)
    # ======================== MIXER =========================

    # ====================== RENDERER ========================
    # create the 3 view images
    print("Generating TOP, SIDE and FRONT view renders...")
    front_path, side_path, top_path = os.path.join(OUT_DIR, "front.png"), os.path.join(OUT_DIR, "side.png"), os.path.join(OUT_DIR, "top.png")
    generate_views(OUT_OBJ_PATH, front_path, side_path, top_path)
    # ====================== RENDERER ========================

    # ======================= SCORER =========================
    # print if the chair generated is probable or not
    print("Scoring chair...")
    probable = score_model(top_path, front_path, side_path)
    if probable == 0:
        print("Not a probable chair")
    else:
        print("Probable chair")
    print("Output chair -> '{}'".format(OUT_OBJ_PATH))
    # ======================= SCORER =========================

    # ======================== END ===========================

    # models = Model.load_models([1919, 3366, 3521, 3204, 1131, 173, 3749, 2313, 5117, 1920]) # you should be passing the output here into the mixer

    #     # 1.
    #     # all you should care about from the Models class is the .components variable as that will contain all 
    #     # part Objs and centers for transformations
    #     # pprint.pprint(model.components) 

    #     # 2.
    #     # You can use this nifty save function from the SimpleObj class
    #     # Note: the save function takes in a type of SimpleObj

    #     # SimpleObj.save("back-{}".format(i), parts["objs"]["back"]) # this will save the back component of a chair

    #     # 3.
    #     # You can also merge SimpleObjs like this...
    #     # back_and_seat_obj = SimpleObj.merge_objs([parts["objs"]["back"], parts["objs"]["seat"]]) # this will merge the back and seat SimpleObjects
    #     # SimpleObj.save("back-and-seat-{}".format(i), back_and_seat_obj)
    #     # SimpleObj.save("back-{}".format(i), parts["objs"]["back"]) # this will save the back component of a chair

    # # ------------------- Mixer -------------------------
    # # the the function below hasnt been created yet, make sure to put your mixer logic in the .mixer/ folder 
    # # mixer_result = Mixer.create_new_chair(models)

    # ------------------- Mixer -------------------------
    # the the function below hasnt been created yet, make sure to put your mixer logic in the .mixer/ folder 
    # mixer_result = Mixer.create_new_chair(models)
    
    # mixer( models, 'test' )
    
    # num = 9
    # legs = models[num].components["objs"]["legs"]
    # for i, l in enumerate( legs ):
        # SimpleObj.save( 'legs-{}-{}'.format( num, i ), l )
