import random
from parser.parser import SimpleObj

# choose the parts for the chair
# @param List objs - an list of models parsed by the parser
# @param int seat_i - an optional index to specify a targeted seat
# @param int back_i - an optional index to specify a targeted back
# @param int arm_i - an optional index to specify a targeted arm rest
# @param int leg_i - an optional index to specify a targeted leg
def choose(objs, seat_i: int = -1, back_i: int = -1, arm_i: int = -1, leg_i: int = -1):
    # get seat index
    if( seat_i > -1 and seat_i < len( objs ) ):
        original = seat_i
    else:
        original = random.randint(0, len(objs)-1)

    # get seat
    seat = objs[original].components["objs"]["seat"]   
    seat_center = objs[original].components["part_centers"]["seat"]

    # debug
    print( 'seat: {}'.format( original ))
    # SimpleObj.save( 'seat-{}'.format( original ), seat )
    
    
    
    # get back index
    if( back_i > -1 and back_i < len( objs ) ):
        num = back_i
    else:
        num = random.randint(0, len(objs)-1)

    #get back 
    back = objs[num].components["objs"]["back"]
    back_center = objs[num].components["part_centers"]["back"]
    
    # debug
    print( 'back: {}'.format( num ))
    # SimpleObj.save( 'back-{}'.format( num ), back )
    
    
    
    # get arm rest index
    if( arm_i > -1 and arm_i < len( objs ) ):
        num = arm_i
    else:
        num = random.randint(0, len(objs)-1)

    # get arm rest
    # i = 1
    # while objs[num].components["objs"]["arm_rests"] == [] and i <=3:
        # num = random.randint(0, len(objs)-1)
        # i += 1
    arm_rest = objs[num].components["objs"]["arm_rests"]
    arm_rests_center = objs[num].components["part_centers"]["arm_rests"]
    arm_rests_seat = objs[num].components["objs"]["seat"]

    # debug
    print( 'arm rest: {}'.format( num ))
    # for i, ar in enumerate( arm_rest ):
        # SimpleObj.save( 'arm_rest-{}-{}'.format( num, i ), ar )
    
    
    
    # get leg index
    if( leg_i > -1 and leg_i < len( objs ) ):
        num = leg_i
    else:
        num = random.randint(0, len(objs)-1)

    # get leg
    legs = objs[num].components["objs"]["legs"]
    legs_center = objs[num].components["part_centers"]["legs"]
    legs_seat = objs[num].components["objs"]["seat"]
    
    #debug
    print( 'legs: {}'.format( num ))
    # for i, l in enumerate( legs ):
        # SimpleObj.save( 'legs-{}-{}'.format( num, i ), l )
    
    
    
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
            "seat": seat_center,
            "legs": legs_center,
            "arm_rests": arm_rests_center,
        }
    }
