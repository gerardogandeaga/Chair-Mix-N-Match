# This file defines the algorithm for composing the back based on the seat

import numpy as np
from mixer.util import split_vertex;
from mixer.util import get_bottom_size;

def change_seat_back(component):
    backX, backY, backZ = split_vertex(component["original_obj"]["back"])
    bottomX, bottomZ = get_bottom_size(component["result_obj"]["back"])
    seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
    resultBackX, resultBackY, resultBackZ = split_vertex(component["result_obj"]["back"])
    
    # using data of original back of seat to translate and scale
    x1 = max(backX) - min(backX)
    x2 = max(resultBackX) - min(resultBackX)
    aX = x1/x2
    y1 = max(backY) - min(backY) 
    y2 = max(resultBackY) - min(resultBackY)
    aY = y1/y2
    bY = min(backY) - min(resultBackY) * aY
    
    z1 = max(backZ) - min(backZ)
    z2 = max(resultBackZ) - min(resultBackZ)
    aZ = z1/z2
    bZ = max(backZ) - max(resultBackZ) * aZ
    
    # if use max(back) can't connect seat correctly
    # back move forward using bottom of back
    if min(seatZ) - (max(bottomZ)*aZ+bZ) > 0.05:
        print( "back move forward" )
        bZ = min(seatZ) - max(bottomZ) * aZ + 0.05
    
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
