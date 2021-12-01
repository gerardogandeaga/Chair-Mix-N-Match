import random
import numpy as np
import pprint
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model

#models = Model.load_models([66, 4037, 2177, 3453])

def random_choose(objs):
    #objs = models
    objsResult = []
    centerResult = []
    # get seat
    num = random.randint(0, len(objs)-1)
    print(num)
    seat = objs[num].components["objs"]["seat"]   
    SimpleObj.save("seat", seat)
    
    #get back 
    num = random.randint(0, len(objs)-1)
    print(num)
    back = objs[num].components["objs"]["back"]
    SimpleObj.save("back", back)
    
    # get arm rest
    num = random.randint(0, len(objs)-1)
    i = 0
    while objs[num].components["objs"]["arm_rests"] != [] or i >= 5:
        num = random.randint(0, len(objs)-1)
        i += 1
    
    # get leg
    num = random.randint(0, len(objs)-1)
    print(num)
    legs = objs[num].components["objs"]["legs"]
    result = SimpleObj.merge_objs([seat, back])
    if (objs[num].components["objs"]["arm_rests"] != []):
        arm_rest = objs[num].components["objs"]["arm_rests"]
        #pprint.pprint(arm_rest)
        SimpleObj.save("arm_rest", SimpleObj.merge_objs([arm_rest[0], arm_rest[1]]))
        result = SimpleObj.merge_objs([result, arm_rest[0], arm_rest[1]])
    
    for leg in legs:
        result = SimpleObj.merge_objs([result, leg])
       
    SimpleObj.save("test", result)
    pprint.pprint(result)
        
    

    