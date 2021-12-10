# This file defines the algorithm for composing the leg based on the seat

import numpy as np
from parser.parser import SimpleObj
from mixer.util import split_vertex, get_top_size, get_used_vertex

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
    # move legs up or down
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
    # if has 4 legs
    if len(component["result_obj"]["legs"]) != 1:     
        for leg in component["result_obj"]["legs"]:
            tX, tZ = get_top_size(leg)
            topX += tX
            topZ += tZ
    else:
        # one legs
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
            print("move")
            z = (oZmax - maxTopZ)*(2/3)
            for leg in component["result_obj"]["legs"]:               
                for v in leg.verts:
                    v[2] += z
            minTopZ += z
            maxTopZ += z
    
        while minTopZ < oZmin or maxTopZ > oZmax:
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
