# Defines the helper functions for mixer

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
        
# save obj
def save(name, obj):
    test_obj = SimpleObj.merge_objs( [obj["result_obj"]["back"], obj["result_obj"]["seat"]] )
    if (obj["result_obj"]["arm_rests"] != []):
        test_obj = SimpleObj.merge_objs([test_obj, obj["result_obj"]["arm_rests"][0], obj["result_obj"]["arm_rests"][1]] )

    for leg in obj["result_obj"]["legs"]:
        test_obj = SimpleObj.merge_objs([test_obj, leg])
    SimpleObj.save(name, test_obj)
