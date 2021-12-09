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
    while objs[num].components["objs"]["arm_rests"] == [] and i <=1:
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
    original =4
    print(original)
    seat = objs[original].components["objs"]["seat"]   
    
    #get back 
    num = 2
    print(num)
    back = objs[num].components["objs"]["back"]
    back_center = objs[num].components["part_centers"]["back"]
    
    # get arm rest
    num = 0
    i = 0
    while objs[num].components["objs"]["arm_rests"] == [] or i == 5:
        num = random.randint(0, len(objs)-1)
        i += 1
    arm_rest = objs[num].components["objs"]["arm_rests"]
    arm_rests_seat = objs[num].components["objs"]["seat"]
    arm_rests_center = objs[num].components["part_centers"]["arm_rests"]
    
    # get leg
    num = 4
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

def get_used_vertex(part):
    vertex = []
    for i in range(len(part.faces)-1):
        F1 = part.faces[i][0]
        F2 = part.faces[i][1]
        F3 = part.faces[i][2]
        v1 = part.verts[F1-1]
        v2 = part.verts[F2-1]
        v3 = part.verts[F3-1]
        vertex += [v1, v2, v3]
    return vertex   

def get_top_size(part):
    x, y, z = split_vertex(part)
    #print("legs max", max(z),  min(z))
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

def change_seat_back(component):
    backX, backY, backZ = split_vertex(component["original_obj"]["back"])
        
    resultBackX, resultBackY, resultBackZ = split_vertex(component["result_obj"]["back"])
    
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
        v1[2] = v1[2] * aZ + bZ
    return {
        "result_obj": {
            "back": component["result_obj"]["back"],
            "seat": component["result_obj"]["seat"],
            "legs": component["result_obj"]["legs"],
            "arm_rests": component["result_obj"]["arm_rests"],
        }
    }

def change_seat_legs(component):
    seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
    SimpleObj.save("leg", component["result_obj"]["legs"][0])
    SimpleObj.save("leg1", component["original_obj"]["legs"][0])
    legsX, legsY, legsZ = split_vertex(component["original_obj"]["legs"][0]) 
    resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])
    
    
    bY = max(legsY) - max(resultLegsY)
    y2 = max(resultLegsY) - min(resultLegsY)
    y1 = max(legsY) - min(legsY)
    aY = y1/y2
    print(max(resultLegsY), max(legsY))
    print("by", bY)
    for leg in component["result_obj"]["legs"]:               
        for v in leg.verts:
            v[1] += bY
    resultLegsY += bY    
      
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
    else:
        topX, topZ = get_top_size(component["result_obj"]["legs"][0])        
    # change seat size by Z         
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
        for arm in component["original_obj"]["arm_rests"]:
            for v in arm.verts:
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
        #print("aZ", min(topZ), oZmin, max(topZ), oZmax)
        while minTopZ < oZmin or maxTopZ > oZmax:
            #print("aZ", aZ)
            aZ = int(aZ) + (aZ - int(aZ))/4
            for v in component["result_obj"]["seat"].verts:
                v[2] = v[2] * aZ
            for v in component["original_obj"]["back"].verts:
                v[2] = v[2] * aZ
            for arm in component["original_obj"]["arm_rests"]:
                for v in arm.verts:
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
    
    
    # change seat size by X          
    if min(topX) < min(seatX) or max(topX) > max(seatX):
        print("change x")
        x1 = max(origX) - min(origX)
        x2 = max(seatZ) - min(seatZ)
        aX = x1/x2
        for v in component["result_obj"]["seat"].verts:
            v[0] = v[0] * aX
        for v in component["original_obj"]["back"].verts:
            v[0] = v[0] * aX
        for arm in component["original_obj"]["arm_rests"]:
            for v in arm.verts:
                v[0] = v[0] * aX
        oXmax *= aX
        oXmin *= aX
        while min(topX) < oXmin or max(topX) > oXmax:
            aX = int(aX) + (aX - int(aX))/4
            for v in component["result_obj"]["seat"].verts:
                v[0] = v[0] * aX
            for v in component["original_obj"]["back"].verts:
                v[0] = v[0] * aX
            for arm in component["original_obj"]["arm_rests"]:
                for v in arm.verts:
                    v[0] = v[0] * aX
            oXmax *= aX
            oXmin *= aX              
        #print("aX", aX)
        
    # check legs height
    check = []
    topX1, topZ1 = get_top_size(component["result_obj"]["legs"][0])
    #SimpleObj.save("seat-3", component["result_obj"]["legs"][1])

    vertex = get_used_vertex(component["result_obj"]["seat"])
    for v in vertex: 
        if v[0] > min(topX1) and v[0] < max(topX1) and v[2] > min(topZ1) and v[2] < max(topZ1):
            check += [v[1]]
    #print(len(check))
    #print("check", min(check), max(resultLegsY))
    #if check != [] and min(check) > max(resultLegsY):
        #print("move up")
    #    bY = min(check) - max(resultLegsY)
    #    for leg in component["result_obj"]["legs"]:               
    #        for v in leg.verts:
    #            v[1] += bY    
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


def change_arm_rests(component):
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


def change_arm_rest(component):
    #pprint.pprint(component)
    if component["result_obj"]["arm_rests"] != []:
        resultArmX, resultArmY, resultArmZ = split_vertex(component["result_obj"]["arm_rests"][0])
        resultArmX1, resultArmY1, resultArmZ1 = split_vertex(component["result_obj"]["arm_rests"][1])
        if component["original_obj"]["arm_rests"] != []:
            print("change arm")
            armX, armY, armZ = split_vertex(component["original_obj"]["arm_rests"][0])    
            armX1, armY1, armZ1 = split_vertex(component["original_obj"]["arm_rests"][1])       
            x1 = max(armX) - min(armX)
            x2 = max(resultArmX) - min(resultArmX)
            aX = x1/x2
            bX = max(armX) - max(resultArmX) * aX
            
            x11 = max(armX1) - min(armX1)
            x21 = max(resultArmX1) - min(resultArmX1)
            aX1 = x11/x21
            bX1 = min(armX1) - min(resultArmX1) * aX1
            
            y1 = max(armY) - min(armY)
            y2 = max(resultArmY) - min(resultArmY)
            aY = y1/y2
            bY = min(armY) - min(resultArmY) * aY
            
            z1 = max(armZ) - min(armZ)
            z2 = max(resultArmZ) - min(resultArmZ)
            aZ = z1/z2
            bZ = max(armZ) - max(resultArmZ) * aZ
            print(bX, bX1)
            for v in component["result_obj"]["arm_rests"][0].verts:
                v[0] = v[0] * aX + bX
                v[1] = v[1] * aY + bY
                v[2] = v[2] * aZ + bZ 
            
            for v in component["result_obj"]["arm_rests"][1].verts:
                v[0] = v[0] * aX + bX1
                v[1] = v[1] * aY + bY
                v[2] = v[2] * aZ + bZ 
    
    return {
        "result_obj": {
            "back": component["result_obj"]["back"],
            "seat": component["result_obj"]["seat"],
            "legs": component["result_obj"]["legs"],
            "arm_rests": component["result_obj"]["arm_rests"],
        }
    }
def mixer(objs, filename):
    
    component = random_choose(objs)
    #component = test(objs)
    com = change_seat_legs(component)
    component["result_obj"] = com["result_obj"]
    component["original_obj"] = com["original_obj"]
    component["result_obj"] = change_seat_back(component)["result_obj"]
    component["result_obj"] = change_arm_rest(component)["result_obj"]
    
    #back_seat = SimpleObj.merge_objs([component["result_obj"]["seat"], component["result_obj"]["legs"][0], 
    #                                 component["result_obj"]["legs"][1], component["result_obj"]["legs"][2],
    #                                 component["result_obj"]["legs"][3]])
    #back_seat = SimpleObj.merge_objs([component["result_obj"]["seat"], component["result_obj"]["legs"][2]])
    save(filename, component)
    ##SimpleObj.save("legs_seat", back_seat)
    
        
def save(name, obj):
    test_obj = SimpleObj.merge_objs( [obj["result_obj"]["back"], obj["result_obj"]["seat"]] )
    if (obj["result_obj"]["arm_rests"] != []):
        test_obj = SimpleObj.merge_objs([test_obj, obj["result_obj"]["arm_rests"][0], obj["result_obj"]["arm_rests"][1]] )

    for leg in obj["result_obj"]["legs"]:
        test_obj = SimpleObj.merge_objs([test_obj, leg])
    SimpleObj.save(name, test_obj)