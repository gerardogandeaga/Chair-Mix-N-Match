import random
import numpy as np
import pprint
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model

#models = Model.load_models([66, 4037, 2177, 3453])


def random_choose_test(objs):
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
    
def random_choose(objs):
    # get seat
    original = random.randint(0, len(objs)-1)
    print(original)
    seat = objs[original].components["objs"]["seat"]   
    
    #get back 
    num = random.randint(0, len(objs)-1)
    print(num)
    back = objs[num].components["objs"]["back"]
    back_center = objs[num].components["part_centers"]["back"]
    
    # get arm rest
    num = random.randint(0, len(objs)-1)
    i = 0
    while objs[num].components["objs"]["arm_rests"] != [] or i >= 5:
        num = random.randint(0, len(objs)-1)
        i += 1
    arm_rest = objs[num].components["objs"]["arm_rests"]
    arm_rests_center = objs[num].components["part_centers"]["arm_rests"]
    
    # get leg
    num = random.randint(0, len(objs)-1)
    print(num)
    legs = objs[num].components["objs"]["legs"]
    legs_center = objs[num].components["part_centers"]["legs"]

    
    return {
        "original_obj": {
            "back": objs[original].components["objs"]["back"],
            "legs": objs[original].components["objs"]["back"],
            "arm_rests": objs[original].components["objs"]["arm_rests"],
        },
        "result_obj": {
            "back": back,
            "seat": seat,
            "legs": legs,
            "arm_rests": arm_rest,
        },
        "original_center": {
            "back": objs[original].components["part_centers"]["back"],
            "seat": objs[original].components["part_centers"]["seat"],
            "legs": objs[original].components["part_centers"]["legs"],
            "arm_rests": objs[original].components["part_centers"]["arm_rests"],
        },
        "center": {
            "back": back_center,
            "legs": legs_center,
            "arm_rests": arm_rests_center,
        }
    }
    
def test(objs):
    # get seat
    original = 1
    print(original)
    seat = objs[original].components["objs"]["seat"]   
    
    #get back 
    num = 2
    print(num)
    back = objs[num].components["objs"]["back"]
    back_center = objs[num].components["part_centers"]["back"]
    
    # get arm rest
    num = 3
    i = 0
    while objs[num].components["objs"]["arm_rests"] != [] or i >= 5:
        num = random.randint(0, len(objs)-1)
        i += 1
    arm_rest = objs[num].components["objs"]["arm_rests"]
    arm_rests_center = objs[num].components["part_centers"]["arm_rests"]
    
    # get leg
    num = 4
    print(num)
    legs = objs[num].components["objs"]["legs"]
    legs_center = objs[num].components["part_centers"]["legs"]

    
    return {
        "original_obj": {
            "back": objs[original].components["objs"]["back"],
            "legs": objs[original].components["objs"]["back"],
            "arm_rests": objs[original].components["objs"]["arm_rests"],
        },
        "result_obj": {
            "back": back,
            "seat": seat,
            "legs": legs,
            "arm_rests": arm_rest,
        },
        "original_center": {
            "back": objs[original].components["part_centers"]["back"],
            "seat": objs[original].components["part_centers"]["seat"],
            "legs": objs[original].components["part_centers"]["legs"],
            "arm_rests": objs[original].components["part_centers"]["arm_rests"],
        },
        "center": {
            "back": back_center,
            "legs": legs_center,
            "arm_rests": arm_rests_center,
        }
    }
    
def mixer(objs):
    #component = random_choose(objs)
    component = test(objs)
    backX = []
    backY = []
    backZ = []
    for v in component["original_obj"]["back"].verts:
        backX += [v[0]]
        backY += [v[1]]
        backZ += [v[2]]
        
    resultBackX = []
    resultBackY = []
    resultBackZ = []

    for v in component["result_obj"]["back"].verts:
        resultBackX += [v[0]]
        resultBackY += [v[1]]
        resultBackZ += [v[2]]
    
    x1 = abs(max(backX) - min(backX)) 
    x2 = abs(max(resultBackX) - min(resultBackX))
    aX = x1/x2
    y1 = abs(max(backY) - min(backY)) 
    y2 = abs(max(resultBackY) - min(resultBackY))
    aY = y1/y2
    bY = min(backY) - min(resultBackY) * aY
    
    z1 = abs(max(backZ) - min(backZ)) 
    z2 = abs(max(resultBackZ) - min(resultBackZ))
    aZ = z1/z2
    
    bZ = min(backZ) - min(resultBackZ) * aZ
    print(min(backZ))
    print(min(resultBackZ))
    print(bZ)
    save("ori_obj", component)
    SimpleObj.save("seat1", component["result_obj"]["seat"])
    SimpleObj.save("back1", component["result_obj"]["back"])
    for v1 in component["result_obj"]["back"].verts:
        v1[0] = v1[0] * aX
        v1[1] = v1[1] * aY + 5
        v1[2] = v1[2] * aZ
    save("result_obj", component)
    SimpleObj.save("back2", component["result_obj"]["back"])
    legsX = []
    legsY = []
    legsZ = []
    i = 0
    #SimpleObj.save("legs", component["original_obj"]["legs"])
    for v in component["original_obj"]["legs"].verts:
        legsX += [v[0]]
        legsY += [v[1]]
        legsZ += [v[2]]
        i+=1
    
    if component["original_obj"]["arm_rests"] != []:
        armX1 = []
        armY1 = []
        armZ1 = []
        armX2 = []
        armY2 = []
        armZ2 = []
        
        for v in component["original_obj"]["arm_rests"][0].verts:
            armX1 += [v[0]]
            armY1 += [v[1]]
            armZ1 += [v[2]]
        for v in component["original_obj"]["arm_rests"][1].verts:
            armX2 += [v[0]]
            armY2 += [v[1]]
            armZ2 += [v[2]]
    
def save(name, obj):
    test_obj = SimpleObj.merge_objs( [obj["result_obj"]["back"], obj["result_obj"]["seat"]] )
    if (obj["result_obj"]["arm_rests"] != []):
        test_obj = SimpleObj.merge_objs([test_obj, obj["result_obj"]["arm_rests"][0], obj["result_obj"]["arm_rests"][1]] )

    for leg in obj["result_obj"]["legs"]:
        test_obj = SimpleObj.merge_objs([test_obj, leg])
    SimpleObj.save(name, test_obj)