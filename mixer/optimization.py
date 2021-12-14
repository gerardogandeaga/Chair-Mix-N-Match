# This file optimizes the chair after a bunch of manipulation that resembled the chair

import numpy as np
import mixer.util as util
from parser.parser import SimpleObj
from mixer.change_leg import find_pieces

# optimize leg
def optimize_leg( component ):
    print( 'optimizing legs...' )
    legs = component['result_obj']['legs']

    # get other parts except for legs, and merge them for the convenience of optimizing legs
    others = []
    others.append( component['result_obj']['seat'] )
    for a in component['result_obj']['arm_rests']:
        others.append( a )
    others = SimpleObj.merge_objs( others )
    others_verts = util.get_verts( others )
    others_size = util.get_size( others_verts )

    # temporary get the whole leg to do a global optimization
    whole_leg = SimpleObj.merge_objs( legs )
    whole_leg_verts = util.get_verts( whole_leg )
    whole_leg_top = util.get_top_verts( whole_leg_verts )
    whole_leg_top_size = util.get_size( whole_leg_top )


#---------- scale whole leg by x and z ----------#


    # if leg top is wider than other parts in x axis
    if( whole_leg_top_size[0] > others_size[0] ):
        print( 'optimizing the width of leg...' )
        ratio = others_size[0] / whole_leg_top_size[0]
        for l in legs:
            for v in l.verts:
                v[0] *= ratio 

    # if leg top is wider than other parts in z axis
    if( whole_leg_top_size[2] > others_size[2] ):
        print( 'optimizing the depth of leg...' )
        ratio = others_size[2] / whole_leg_top_size[2]
        for l in legs:
            for v in l.verts:
                v[2] *= ratio 



#---------- split leg ----------#



    # if the leg is one piece, try to split it into pieces
    if( len( legs ) == 1 ):
        legs = find_pieces( legs[0], component['center']['legs'][0] )

    # get the vertices and top vertices
    legs_verts = [ util.get_verts( l ) for l in legs ]
    legs_top = [ util.get_top_verts( lv ) for lv in legs_verts ]



#---------- translate individual leg pieces by x and z ----------# 



    for li, l_top in enumerate( legs_top ):
        # get leg top min and max and others min and max
        l_top_min = np.amin( l_top, axis = 0 )
        l_top_max = np.amax( l_top, axis = 0 )
        others_min = np.amin( others_verts, axis = 0 )
        others_max = np.amax( others_verts, axis = 0 )

        # for x and z axises
        for i in range( 0, 3, 2 ):
            # if leg top is less than others min in x or z axis
            if( l_top_min[i] < others_min[i] ):
                print( 'move leg {} in +{} direction'.format( li, 'x' if i == 0 else 'z' ) )
                offset = others_min[i] - l_top_min[i]
                for l in legs:
                    for v in l.verts:
                        v[i] += offset
            # if leg top is greater than others min in x or z axis
            elif( l_top_max[i] > others_max[i] ):
                print( 'move leg {} in -{} direction'.format( li, 'x' if i == 0 else 'z' ) )
                offset = others_max[i] - l_top_max[i]
                for l in legs:
                    for v in l.verts:
                        v[i] += offset



#---------- transform leg pieces by y ----------#


    # y translation tolerance
    epsilon_y = 0

    # refresh the vertices and top vertices
    legs = component['result_obj']['legs']
    legs_verts = [ util.get_verts( l ) for l in legs ]
    legs_top = [ util.get_top_verts( lv ) for lv in legs_verts ]
    
    # if the leg is still one piece, then attach the leg to the bottom of the seat
    if( len( legs ) == 1 ):
        # get leg top min and max
        leg_top_max = np.amax( legs_top[0], axis = 0 )
        leg_top_min = np.amin( legs_top[0], axis = 0 )

        # construct range to retrieved vertices from other parts and get the min
        range_min = np.copy( leg_top_min )
        range_max = np.copy( leg_top_max )
        range_min[1] = np.NINF
        range_max[1] = np.inf
        others_relative_verts = util.get_range_verts( others_verts, range_min, range_max )

        if( len( others_relative_verts ) == 0 ):
            # get seat center
            dist_vert = component['center']['seat'][0]
        else:
            dist_vert = np.amin( others_relative_verts, axis = 0 )

        # calculate the distance between them in y axis
        dist = dist_vert[1] - leg_top_max[1] + epsilon_y

        # translate the leg in y axis
        for v in legs[0].verts:
            v[1] += dist
    
    # else there are more than one leg piece, then attach each leg piece to the bottom of the seat
    else:
        for i, ( l, l_top ) in enumerate( zip( legs, legs_top ) ):
            # get used vertices
            l_verts = util.get_verts( l )

            # get leg top min and max
            l_top_min = np.amin( l_top, axis = 0 )
            l_top_max = np.amax( l_top, axis = 0 )

            # construct range to retrieved vertices from other parts and get the min
            range_min = np.copy( l_top_min )
            range_max = np.copy( l_top_max )
            range_min[1] = np.NINF
            range_max[1] = np.inf
            others_relative_verts = util.get_range_verts( others_verts, range_min, range_max )

            # sometimes you just cannot get the vertices...
            for attempt in range( 3 ):
                if( len( others_relative_verts ) == 0 ):
                    for axis in range( 0, 3, 2 ):
                        if( l_top_min[axis] < 0 ):
                            print( 'move leg {} in +{} direction'.format( i, 'x' if axis == 0 else 'z' ) )
                            offset = 0.1
                        else:
                            print( 'move leg {} in -{} direction'.format( i, 'x' if axis == 0 else 'z' ) )
                            offset = -0.1

                        for v in l.verts:
                            v += offset
                            l_top_max[axis] += offset
                            l_top_min[axis] += offset
                    
                    # retry
                    range_min = np.copy( l_top_min )
                    range_max = np.copy( l_top_max )
                    range_min[1] = np.NINF
                    range_max[1] = np.inf
                    others_relative_verts = util.get_range_verts( others_verts, range_min, range_max )
                else:
                    break
            else:
                print( 'leg optimization failed' )
                break

            others_relative_min = np.amin( others_relative_verts, axis = 0 )

            # calculate the distance between the leg top and whatever that's directly above it (y axis)
            dist = others_relative_min[1] - l_top_max[1] + epsilon_y

            # calculate the scaling ratio in y axis
            l_size = util.get_size( l_verts )
            ratio = ( l_size[1] + dist ) / l_size[1]

            # calculate the translation offset in y axis
            offset = others_relative_min[1] - l_top_max[1] * ratio

            # transform the leg in y axis
            for v in l.verts:
                v[1] = v[1] * ratio + offset 
    
    component['result_obj']['legs'] = legs
    return

def optimize_back( component ):
    print( 'optimizing back...' )
    chairX = 0
    
    # width of arm rests + seat, if chair has arm rests 
    if component["result_obj"]["arm_rests"] != []: 
        armX, armY, armZ = util.split_vertex(component["result_obj"]["arm_rests"][0])
        armX1, armY1, armZ1 = util.split_vertex(component["result_obj"]["arm_rests"][1])
        chairX = max(armX1) - min(armX)
    # width of seat
    else:
        seatX, seatY, seatZ = util.split_vertex(component["result_obj"]["seat"])
        chairX = max(seatX) - min(seatX)
    backX, backY, backZ = util.split_vertex(component["result_obj"]["back"])
    
    # if back too wide for chair
    if max(backX)-min(backX) > chairX:
        print( "scaling width of arm rests..." )
        x = max(backX)-min(backX)
        aX = chairX/x
        for v in component["result_obj"]["back"].verts:
            v[0] *= aX
    return

# optimize the chair
def optimize( component ):
    optimize_leg( component )
    optimize_back( component )
    return component
