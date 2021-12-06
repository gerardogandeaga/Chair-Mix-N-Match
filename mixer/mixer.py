import random
import numpy as np
import pprint
from parser.draw3dobb import showGenshape
# from parser.grassdata import GRASSDataset
from parser.parser import SimpleObj, Model


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
    arm_rests_seat = objs[num].components["objs"]["seat"]
    
    # get leg
    num = random.randint(0, len(objs)-1)
    print(num)
    legs = objs[num].components["objs"]["legs"]
    legs_center = objs[num].components["part_centers"]["legs"]
    legs_seat = objs[num].components["objs"]["seat"]
    
    return {
        "original_obj": {
            "back": objs[original].components["objs"]["back"],
            "legs": objs[original].components["objs"]["legs"],
            "arm_rests": objs[original].components["objs"]["arm_rests"],
            "arm_rests_seat": arm_rests_seat,
            "legs_seat": legs_seat,
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
    original = 2
    print(original)
    seat = objs[original].components["objs"]["seat"]   
    
    #get back 
    num = 2
    print(num)
    back = objs[num].components["objs"]["back"]
    back_center = objs[num].components["part_centers"]["back"]
    
    # get arm rest
    num = 1
    i = 0
    while objs[num].components["objs"]["arm_rests"] == [] or i == 5:
        num = random.randint(0, len(objs)-1)
        i += 1
    arm_rest = objs[num].components["objs"]["arm_rests"]
    arm_rests_seat = objs[num].components["objs"]["seat"]
    arm_rests_center = objs[num].components["part_centers"]["arm_rests"]
    
    # get leg
    num = 0
    print(num)
    legs = objs[num].components["objs"]["legs"]
    legs_center = objs[num].components["part_centers"]["legs"]
    legs_seat = objs[num].components["objs"]["seat"]

    
    return {
        "original_obj": {
            "back": objs[original].components["objs"]["back"],
            "legs": objs[original].components["objs"]["legs"],
            "arm_rests": objs[original].components["objs"]["arm_rests"],
            "arm_rests_seat": arm_rests_seat,
            "legs_seat": legs_seat,
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
  
def change_seat_back(component):
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
    
    x1 = max(backX) - min(backX)
    x2 = max(resultBackX) - min(resultBackX)
    aX = x1/x2
    y1 = max(backY) - min(backY) 
    y2 = abs(max(resultBackY) - min(resultBackY))
    aY = y1/y2
    bY = min(backY) - min(resultBackY) * aY
    
    z1 = max(backZ) - min(backZ)
    z2 = max(resultBackZ) - min(resultBackZ)
    aZ = z1/z2
    
    bZ = min(backZ) - min(resultBackZ) * aZ
    
    for v1 in component["result_obj"]["back"].verts:
        v1[0] = v1[0] * aX
        v1[1] = v1[1] * aY + bY
        v1[2] = v1[2] * aZ
    return {
        "result_obj": {
            "back": component["result_obj"]["back"],
            "seat": component["result_obj"]["seat"],
            "legs": component["result_obj"]["legs"],
            "arm_rests": component["result_obj"]["arm_rests"],
        }
    }

def split_vertex(part):
    x = []
    y = []
    z = []
    for i in range(len(part.faces)-1):
        F1 = part.faces[i][0]
        F2 = part.faces[i][1]
        F3 = part.faces[i][2]
        v1 = part.verts[F1-1]
        v2 = part.verts[F2-1]
        v3 = part.verts[F3-1]
        x += [v1[0], v2[0], v3[0]]
        y += [v1[1], v2[1], v3[1]]
        z += [v1[2], v2[2], v3[2]]  
    return x, y, z   

def get_top_size(part):
    x, y, z = split_vertex(part)
    print("legs max", max(z),  min(z))
    maxY = max(y)
    xArray = []
    zArray = []
    for i in range(len(part.faces)-1):
        F1 = part.faces[i][0]
        F2 = part.faces[i][1]
        F3 = part.faces[i][2]
        v1 = part.verts[F1-1]
        v2 = part.verts[F2-1]
        v3 = part.verts[F3-1]
        
        if v1[1] == maxY:
            xArray += [v1[0]]
            zArray += [v1[2]]
        if v2[1] == maxY:
            xArray += [v2[0]]
            zArray += [v2[2]]
        if v3[1] == maxY:
            xArray += [v3[0]]
            zArray += [v3[2]]
            
    #print(xArray, zArray)
    return xArray, zArray

def change_seat_legs(component):
    seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
    SimpleObj.save("leg", component["result_obj"]["legs"][0])
    legsX, legsY, legsZ = split_vertex(component["original_obj"]["legs"][0]) 
    resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])
    
    
    bY = max(legsY) - max(resultLegsY)
    y2 = max(resultLegsY) - min(resultLegsY)
    y1 = max(legsY) - min(legsY)
    aY = y1/y2
    
    for leg in component["result_obj"]["legs"]:               
        for v in leg.verts:
            v[1] += bY
           
    oXmax = max(seatX)
    oXmin = min(seatX)
    oZmax = max(seatZ)
    oZmin = min(seatZ)
    topX = [] 
    topZ = []
    if len(component["result_obj"]["legs"]) != 1:     
        for leg in component["result_obj"]["legs"]:
            tX, tZ = get_top_size(leg)
            topX += tX
            topZ += tZ
            
            
    minTopZ = min(topZ)
    maxTopZ = max(topZ)    
    origX, origY, origZ = split_vertex(component["original_obj"]["legs_seat"])
    if min(topZ) < min(seatZ) or max(topZ) > max(seatZ):
        z1 = max(origZ) - min(origZ)
        z2 = max(seatZ) - min(seatZ)
        aZ = z1/z2
        for v in component["result_obj"]["seat"].verts:
            v[2] = v[2] * aZ
        for v in component["original_obj"]["back"].verts:
            v[2] = v[2] * aZ
        oZmax *= aZ
        oZmin *= aZ
        if minTopZ < oZmin and maxTopZ < oZmax:
            #print("move")
            z = (oZmax - maxTopZ)*(2/3)
            for leg in component["result_obj"]["legs"]:               
                for v in leg.verts:
                    v[2] += z
            minTopZ += z
            maxTopZ += z
        print("aZ", min(topZ), oZmin, max(topZ), oZmax)
        while minTopZ < oZmin or maxTopZ > oZmax:
            #print("aZ", aZ)
            aZ = int(aZ) + (aZ - int(aZ))/4
            for v in component["result_obj"]["seat"].verts:
                v[2] = v[2] * aZ
            for v in component["original_obj"]["back"].verts:
                v[2] = v[2] * aZ
            oZmax *= aZ
            oZmin *= aZ
            #print("move", minTopZ, oZmin, maxTopZ, oZmax)
            if minTopZ < oZmin and maxTopZ < oZmax:
                #print("move")
                z = (oZmax - maxTopZ)*(2/3)
                for leg in component["result_obj"]["legs"]:               
                    for v in leg.verts:
                        v[2] += z
                minTopZ += z
                maxTopZ += z
                    
    if min(topX) < min(seatX) or max(topX) > max(seatX):
        x1 = max(origX) - min(origX)
        x2 = max(seatZ) - min(seatZ)
        aX = x1/x2
        for v in component["result_obj"]["seat"].verts:
            v[0] = v[0] * aX
        for v in component["original_obj"]["back"].verts:
            v[0] = v[0] * aX
        oXmax *= aX
        oXmin *= aX
        while min(topX) < oXmin or max(topX) > oXmax:
            aX = int(aX) + (aX - int(aX))/4
            for v in component["result_obj"]["seat"].verts:
                v[0] = v[0] * aX
            for v in component["original_obj"]["back"].verts:
                v[0] = v[0] * aX
            oXmax *= aX
            oXmin *= aX              
        print("aX", aX)
    #print("original seat", max(resultLegsY), min(seatY),  max(legsY), component["original_center"]["seat"][0][1]) 
    return {
        "original_obj": {
            "back": component["original_obj"]["back"],
            "legs": component["original_obj"]["legs"],
            "arm_rests": component["original_obj"]["arm_rests"],
            "arm_rests_seat": component["original_obj"]["arm_rests_seat"],
            "legs_seat": component["original_obj"]["legs_seat"],
        },
        "result_obj": {
            "back": component["result_obj"]["back"],
            "seat": component["result_obj"]["seat"],
            "legs": component["result_obj"]["legs"],
            "arm_rests": component["result_obj"]["arm_rests"],
        }
    } 

def mixer(objs):
    
    #component = random_choose(objs)
    component = test(objs)
    com = change_seat_legs(component)
    component["result_obj"] = com["result_obj"]
    component["original_obj"] = com["original_obj"]
    component["result_obj"] = change_seat_back(component)["result_obj"]
    
    x = component["original_center"]["seat"][0][0]
    y = component["original_center"]["seat"][0][1]
    z = component["original_center"]["seat"][0][2]
     
    SimpleObj.save("seat", component["result_obj"]["seat"])
    seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
    if component["original_obj"]["arm_rests"] != [] and component["result_obj"]["arm_rests"] != []:
        armX = []
        armY = []
        armZ = []
        resultArmX = []
        resultArmY = []
        resultArmZ = []
        
        for v in component["result_obj"]["arm_rests"][0].verts:
            resultArmX += [v[0]]
            resultArmY += [v[1]]
            resultArmZ += [v[2]]
            
        x1 = min(seatX)
        x2 = min(resultArmX)
        bX = x1 - x2
        
        y1 = min(seatY) 
        y2 = min(resultArmY)
        bY = y1 -y2
        
        z1 = max(seatZ) - min(seatZ)
        z2 = max(resultArmZ) - min(resultArmZ)
        aZ = z1/z2
        bZ = min(seatZ) - min(resultArmZ) * aZ
        
        print(z1, z2)
        #for v in component["result_obj"]["arm_rests"][0].verts:
        #    v[0] = v[0] - bX
        #    v[1] = v[1] + bY
        #    v[2] = v[2] * aZ + bZ
    back_seat = SimpleObj.merge_objs([component["result_obj"]["seat"], component["result_obj"]["legs"][0], 
                                     component["result_obj"]["legs"][1], component["result_obj"]["legs"][2],
                                     component["result_obj"]["legs"][3]])
    save("result_obj", component)
    #SimpleObj.save("legs_seat", back_seat)
    
        
def save(name, obj):
    test_obj = SimpleObj.merge_objs( [obj["result_obj"]["back"], obj["result_obj"]["seat"]] )
    if (obj["result_obj"]["arm_rests"] != []):
        test_obj = SimpleObj.merge_objs([test_obj, obj["result_obj"]["arm_rests"][0], obj["result_obj"]["arm_rests"][1]] )

    for leg in obj["result_obj"]["legs"]:
        test_obj = SimpleObj.merge_objs([test_obj, leg])
    SimpleObj.save(name, test_obj)