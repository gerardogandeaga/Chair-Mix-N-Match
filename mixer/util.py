# Defines the helper functions for mixer

import numpy as np
from typing import List
from parser.parser import SimpleObj

# split vertex to x, y, z array
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

# get vertex by face
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

# get x, z of bottom of parts
def get_bottom_size(part):
    x, y, z = split_vertex(part)
    minY = min(y)
    xArray = []
    zArray = []
    for i in range(len(part.faces)-1):
        F1 = part.faces[i][0]
        F2 = part.faces[i][1]
        F3 = part.faces[i][2]
        v1 = part.verts[F1-1]
        v2 = part.verts[F2-1]
        v3 = part.verts[F3-1]
        
        if v1[1] >= minY and v1[1] <= minY + 0.04:
            xArray += [v1[0]]
            zArray += [v1[2]]
        if v2[1] >= minY and v2[1] <= minY + 0.04:
            xArray += [v2[0]]
            zArray += [v2[2]]
        if v3[1] >= minY and v3[1] <= minY + 0.04:
            xArray += [v3[0]]
            zArray += [v3[2]]
            
    return xArray, zArray

# get x, z of top of parts 
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
        
        if v1[1] <= maxY and v1[1] >= maxY - 0.04:
            xArray += [v1[0]]
            zArray += [v1[2]]
        if v2[1] <= maxY and v2[1] >= maxY - 0.04:
            xArray += [v2[0]]
            zArray += [v2[2]]
        if v3[1] <= maxY and v3[1] >= maxY - 0.04:
            xArray += [v3[0]]
            zArray += [v3[2]]
            
    #print(xArray, zArray)
    return xArray, zArray
        
# normalize a list of array[ x, y, z ] based on the axises between 0 and 1
def normalize_points( points: np.ndarray, p: np.ndarray = np.array([]) ) -> np.ndarray:
    if( p.size != 0 ):
        return ( p - np.amin( points, axis = 0 ) ) / ( np.amax( points, axis = 0 ) - np.amin( points, axis = 0 ) )
    else:
        return ( points - np.amin( points, axis = 0 ) ) / ( np.amax( points, axis = 0 ) - np.amin( points, axis = 0 ) )

# get a shallow copy of used vertices
def get_verts( obj: SimpleObj ) -> np.ndarray:
    return np.array( [ obj.verts[ i - 1 ] for face in obj.faces for i in face ] ) 

# get a shallow copy of the top 10% of vertices
def get_top_verts( verts: np.ndarray ) -> np.ndarray:
    norm_verts = normalize_points( verts )
    return np.array( [ v for v, nv in zip( verts, norm_verts ) if nv[1] > 0.9 ] )

# get a shallow copy of vertices within a specified range
# amin is an array that specifies the minimun x, y, z
# amax is an array that specifies the maximun x, y, z
def get_range_verts( verts: np.ndarray, amin: np.ndarray, amax: np.ndarray ) -> np.ndarray:
    return np.array( [ v for v in verts if( ( v >= amin ).all() and ( v <= amax ).all() ) ] )

# get the width, height, depth by using an array of vertices
def get_size( verts: np.ndarray ) -> np.ndarray:
    return np.amax( verts, axis = 0 ) - np.amin( verts, axis = 0 )

# save obj
def save(name, obj):
    test_obj = SimpleObj.merge_objs( [obj["result_obj"]["back"], obj["result_obj"]["seat"]] )
    if (obj["result_obj"]["arm_rests"] != []):
        test_obj = SimpleObj.merge_objs([test_obj, obj["result_obj"]["arm_rests"][0], obj["result_obj"]["arm_rests"][1]] )

    for leg in obj["result_obj"]["legs"]:
        test_obj = SimpleObj.merge_objs([test_obj, leg])
    SimpleObj.save(name, test_obj)
