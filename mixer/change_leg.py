# This file defines the algorithm for composing the leg based on the seat

import numpy as np
from numpy import linalg as la
from typing import List
from parser.parser import SimpleObj
from mixer.util import split_vertex, get_top_size, get_used_vertex, normalize_points



# separate the leg into different pieces
def find_pieces( leg: SimpleObj, center: np.ndarray ) -> List[ SimpleObj ]:
    out = [ leg ]

    # normalize all vertices between 0 and 1
    norm_verts = normalize_points( np.array( leg.verts ) )
    norm_center = normalize_points( np.array( leg.verts ), p = center )
    norm_center_top = np.copy( norm_center )
    norm_center_top[1] = 1

    # determine if the leg can be attached at its centre (one piece)
    # if there is no vertex within a normalized radius of 10% of the top center 
    if( len( [ v for v in norm_verts if la.norm( v - norm_center_top ) < 0.1 ] ) == 0 ):
        # then detect vertex in four directions (-x, +x, -z, +z) using kmean center
        print( 'leg cannot be directly attach, looking for sub-legs...' )

        # (-x, +x, -z, +z): (left, right, back, front)
        quadrants = np.full( [ 4, 3 ], np.copy( norm_center ) )
        quadrants[0][0] = 0
        quadrants[1][0] = 1
        quadrants[2][2] = 0
        quadrants[3][2] = 1
        quadrants_bool = np.full( 4, False )

        epsilon = 0.01
        for i, q in enumerate( quadrants ):
            print( 'scaning quadrant {}...'.format( i ) )
            for f in leg.faces:
                for fv in f:
                    v = norm_verts[fv - 1]
                    abs_cross = abs( np.cross( q - norm_center, v - norm_center ) )
                    dot = np.dot( q - norm_center, v - norm_center )
                    length = la.norm( q - norm_center )

                    # if v is collinear with the plane between center and q with a tolerance of epsilon
                    # and v and q are on the same side of center
                    # and v is between center and q
                    if( abs_cross[1] < epsilon 
                        and any( [ abs_cross[0] < epsilon, abs_cross[2] < epsilon ] )
                        and dot >= 0 
                        and dot <= length 
                    ):
                        quadrants_bool[i] = True
                        break
        
        # if legs found in all direction, then don't split 
        if( quadrants_bool.all() ):
            print( 'cannot find sub-leg' )

        # if the legs are at -x and +x (left and right)
        elif( quadrants_bool[0] and quadrants_bool[1] ):
            print( 'left and right sub-legs found' )

            left_faces = []
            right_faces = []
            
            # split the faces into 2 arrays
            for f in leg.faces:
                # if all the vertices in face is less than center in x component
                if( all( [ leg.verts[ fv - 1 ][0] < center[0] for fv in f ] ) ):
                    left_faces.append( np.copy( f ) )
                # if all the vertices in face is greater than center in x component
                elif( all( [ leg.verts[ fv - 1 ][0] > center[0] for fv in f ] ) ):
                    right_faces.append( np.copy( f ) )

            # create SimpleObj to output
            left = SimpleObj.create( np.copy( leg.verts ), left_faces )
            right = SimpleObj.create( np.copy( leg.verts ), right_faces )
            out = [ left, right ]
        
        # else if the legs are at -z and +z (back and front)
        elif( quadrants_bool[2] and quadrants_bool[3] ):
            print( 'back and front sub-legs found' )
            
            back_faces = []
            front_faces = []

            # split the faces into 2 arrays
            for f in leg.faces:
                #if all the vertices in face is less than center in z component
                if( all( [ leg.verts[ fv - 1 ][2] < center[2] for fv in f ] ) ):
                    back_faces.append( np.copy( f ) )
                # if all the vertices in face is greater than center in z component
                elif( all( [ leg.verts[ fv - 1 ][2] > center[2] for fv in f ] ) ):
                    front_faces.append( np.copy( f ) )

            # create SimpleObj to output
            back = SimpleObj.create( np.copy( leg.verts ), back_faces )
            front = SimpleObj.create( np.copy( leg.verts ), front_faces )
            out = [ back, front ]

        # else
        else:
            print( 'cannot find sub-leg' )

    return out



def change_seat_legs(component):
    seatX, seatY, seatZ = split_vertex(component["result_obj"]["seat"])
    SimpleObj.save("leg", component["result_obj"]["legs"][0])
    SimpleObj.save("leg1", component["original_obj"]["legs"][0])
    legsX, legsY, legsZ = split_vertex(component["original_obj"]["legs"][0]) 
    resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])
    resultSeatCenter = component['center']['seat']
    resultLegsCenter = component['center']['legs']
    
    
    bY = max(legsY) - max(resultLegsY)
    y2 = max(resultLegsY) - min(resultLegsY)
    y1 = max(legsY) - min(legsY)
    aY = y1/y2
    # move legs up or down
    for leg in component["result_obj"]["legs"]:               
        for v in leg.verts:
            v[1] += bY
    for c in resultLegsCenter:
        c[1] += bY
    resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])  
    
    # if leg too short for seat
    if min(resultLegsY) > min(seatY):
        y1 = (max(seatY) - min(seatY)) * 1.1
        y2 = max(resultLegsY) - min(resultLegsY)
        aY = y1/y2
        bY = max(legsY) - max(resultLegsY) * aY
        for leg in component["result_obj"]["legs"]:               
            for v in leg.verts:
                v[1] = v[1] * aY + bY
        for c in resultLegsCenter:
            c[1] = c[1] * aY + bY
        resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])
    
    # if leg too short for arm rests
    if len(component["result_obj"]["arm_rests"]) != 0:
        armX, armY, armZ = split_vertex(component["result_obj"]["arm_rests"][0])
        if min(resultLegsY) > min(armY):
            y1 = max(armY) - min(armY)
            y2 = max(resultLegsY) - min(resultLegsY)
            aY = y1/y2
            bY = max(legsY) - max(resultLegsY) * aY
            for leg in component["result_obj"]["legs"]:               
                for v in leg.verts:
                    v[1] = v[1] * aY + bY
            for c in resultLegsCenter:
                c[1] = c[1] * aY + bY
            resultLegsX, resultLegsY, resultLegsZ = split_vertex(component["result_obj"]["legs"][0])
      
    oXmax = max(seatX)
    oXmin = min(seatX)
    oZmax = max(seatZ)
    oZmin = min(seatZ)
    topX = [] 
    topZ = []
    # if has more than one leg 
    if len(component["result_obj"]["legs"]) != 1:     
        for leg in component["result_obj"]["legs"]:
            tX, tZ = get_top_size(leg)
            topX += tX
            topZ += tZ
    else:
        # one legs
        topX, topZ = get_top_size(component["result_obj"]["legs"][0])        
        
        
        
#---------- change seat size by Z ----------#       

    minTopZ = min(topZ)
    maxTopZ = max(topZ) 
    minTopX = min(topX)
    maxTopX = max(topX) 
    origX, origY, origZ = split_vertex(component["original_obj"]["legs_seat"])
    
    # if min leg top z < min seat z || max leg top z > max seat z
    if( minTopZ < oZmin or maxTopZ > oZmax ):
        print( "scaling seat depth..." )
        z1 = max(origZ) - min(origZ)
        z2 = max(seatZ) - min(seatZ)
        aZ = z1/z2
        for v in component["result_obj"]["seat"].verts:
            v[2] = v[2] * aZ
            resultSeatCenter[0][2] = resultSeatCenter[0][2] * aZ
        for v in component["original_obj"]["back"].verts:
            v[2] = v[2] * aZ
        for arm in component["original_obj"]["arm_rests"]:
            for v in arm.verts:
                v[2] = v[2] * aZ
        oZmax *= aZ
        oZmin *= aZ

        # min_leg_top_z < min_seat_z && max_leg_top_z < max_seat_z
        if minTopZ < oZmin and maxTopZ < oZmax:
            print("leg moving forward...")
            z = min( (oZmin - minTopZ), (oZmax - maxTopZ) )
            for leg in component["result_obj"]["legs"]:               
                for v in leg.verts:
                    v[2] += z
                for c in resultLegsCenter:
                    c[2] += z
            minTopZ += z
            maxTopZ += z
        # max_leg_top_z > max_seat_z && min_leg_top_z > min_seat_z
        elif maxTopZ > oZmax and minTopZ > oZmin:
            print("leg moving backward...")
            z = min( (oZmin - minTopZ), (oZmax - maxTopZ) )
            for leg in component["result_obj"]["legs"]:               
                for v in leg.verts:
                    v[2] += z
                for c in resultLegsCenter:
                    c[2] += z
            minTopZ += z
            maxTopZ += z
    


#---------- change seat size by X ----------#
    
    
    
    # if min leg top x < min seat x || max leg top x > max seat x
    if( minTopX < oXmin or maxTopX > oXmax ):
        print( "scaling seat width..." )
        x1 = max(origX) - min(origX)
        x2 = max(seatX) - min(seatX)
        aX = x1/x2
        for v in component["result_obj"]["seat"].verts:
            v[0] = v[0] * aX
            resultSeatCenter[0][0] = resultSeatCenter[0][0] * aX
        for v in component["original_obj"]["back"].verts:
            v[0] = v[0] * aX
        for arm in component["original_obj"]["arm_rests"]:
            for v in arm.verts:
                v[0] = v[0] * aX
        oXmax *= aX
        oXmin *= aX



#---------- returns ----------#



    component['center']['legs'] = resultLegsCenter
    component['center']['seat'] = resultSeatCenter
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
