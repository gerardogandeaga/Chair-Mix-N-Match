# This file defines the algorithm for composing the arm rest based on the seat

import numpy as np
from mixer.util import split_vertex, get_bottom_size

def change_arm_rests(component):
    if component["result_obj"]["arm_rests"] != []:
        resultArmX, resultArmY, resultArmZ = split_vertex(component["result_obj"]["arm_rests"][0])
        resultArmX1, resultArmY1, resultArmZ1 = split_vertex(component["result_obj"]["arm_rests"][1])
        seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
        
        # change arm rests by original arm rest of seat
        if component["original_obj"]["arm_rests"] != []:
            print("change arm")
            armX, armY, armZ = split_vertex(component["original_obj"]["arm_rests"][0])    
            armX1, armY1, armZ1 = split_vertex(component["original_obj"]["arm_rests"][1])       
            x1 = max(armX) - min(armX)
            x2 = max(resultArmX) - min(resultArmX)
            aX = x1/x2
            bX = min(armX) - min(resultArmX) * aX
            
            x11 = max(armX1) - min(armX1)
            x21 = max(resultArmX1) - min(resultArmX1)
            aX1 = x11/x21
            bX1 = max(armX1) - max(resultArmX1) * aX1
            
            y1 = max(armY) - min(armY)
            y2 = max(resultArmY) - min(resultArmY)
            aY = y1/y2
            bY = min(armY) - min(resultArmY) * aY
            
            z1 = max(armZ) - min(armZ)
            z2 = max(resultArmZ) - min(resultArmZ)
            aZ = z1/z2
            bZ = max(armZ) - max(resultArmZ) * aZ

            for v in component["result_obj"]["arm_rests"][0].verts:
                v[0] = v[0] * aX + bX
                v[1] = v[1] * aY + bY
                v[2] = v[2] * aZ + bZ 
            
            for v in component["result_obj"]["arm_rests"][1].verts:
                v[0] = v[0] * aX + bX1
                v[1] = v[1] * aY + bY
                v[2] = v[2] * aZ + bZ 
        
        # change arm rest without original arm rest or not fit chair after first condition
        resultArmX, resultArmY, resultArmZ = split_vertex(component["result_obj"]["arm_rests"][0])
        resultArmX1, resultArmY1, resultArmZ1 = split_vertex(component["result_obj"]["arm_rests"][1])
        if not component["original_obj"]["arm_rests"] or max(resultArmX) < min(seatX) or min(resultArmX1) > max(seatX):
            print( "can't get original arm seat or arm rest not fit, calculating..." )
            backX, backY, backZ = split_vertex(component["result_obj"]["back"])
            bottomX, bottomZ = get_bottom_size(component["result_obj"]["arm_rests"][0])
            bottomX1, bottomZ1 = get_bottom_size(component["result_obj"]["arm_rests"][1])
            
            x1 = (max(seatX) - min(seatX)) * 0.15
            x2 = max(resultArmX) - min(resultArmX)
            aX = x1/x2
            
            bX = min(seatX) - min(bottomX) * aX
            bX1 = max(seatX) - max(bottomX1) * aX
            
            y1 = (max(backY) - min(backY)) * 0.5
            y2 = max(resultArmY) - min(resultArmY)
            aY = y1/y2
            # connect arm rest with botttom of seat
            bY = min(seatY) - min(resultArmY) * aY
            
            # if max of arm rests lower than seat after translate by bY
            if max(resultArmY)*aY+bY < max(seatY):
                bY = max(seatY) - min(resultArmY)*aY -0.09
            
            # scaling length using distance of max(seat Z) to middle of back Z
            z1 = (max(seatZ) - max(backZ) + (max(backZ)-min(backZ)/2)) * 0.9
            z2 = max(resultArmZ) - min(resultArmZ)
            aZ = z1/z2
            bZ = min(seatZ) - min(resultArmZ) * aZ
            
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
