import numpy as np
from parser.parser import SimpleObj, Model
from mixer.get_component import choose
from mixer.change_leg import change_seat_legs
from mixer.change_back import change_seat_back
from mixer.change_arm_rest import change_arm_rests
from mixer.util import save
    
def mixer(objs, filename):
    
    component = choose(objs)
    # component = choose(objs, 1, 5, 9, 2) ->  choose(objs)
    print( 'parts choosen' )

    com = change_seat_legs(component)
    component["result_obj"] = com["result_obj"]
    component["original_obj"] = com["original_obj"]
    print( 'leg composed' )
    
    component["result_obj"] = change_seat_back(component)["result_obj"]
    print( 'back composed' )
    
    component["result_obj"] = change_arm_rests(component)["result_obj"]
    print( 'arm composed' )
    
    save(filename, component)
    print( 'obj saved' )
