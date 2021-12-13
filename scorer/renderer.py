import trimesh
import pyrender
import numpy as np
import matplotlib.pyplot as plt
import copy
import pprint
import cv2

LT_GRAY = [100, 100, 100]
DK_GRAY = [38, 38, 38]
X, Y, Z = 0, 1, 2

def read_obj(input_obj):
    verts = []
    faces = []
    with open(input_obj) as obj:
        lines = obj.readlines()
        num_lines = len(lines)
        print("Lines:", num_lines)
        for line in lines:
            line = line.split(" ")
            if line[0] == "v":
                line = np.array(line[1:], dtype=float)
                verts.append(line)
            elif line[0] == "f":
                line = np.array(line[1:], dtype=int) - 1
                faces.append(line)
            else:
                print("ERROR:", line)

    return verts, faces

def generate_views(input_obj, front_path, side_path, top_path):
    # creates a timesh with the given input file
    tri_mesh = trimesh.load(input_obj, validate=True)
    # print(len(tri_mesh.vertices), len(tri_mesh.triangles))

    # verts, faces = read_obj(input_obj)
    # tri_mesh = trimesh.Trimesh(vertices=verts, faces=faces, validate=True)

    # tri_mesh.face_normals = -tri_mesh.face_normals
    # tri_mesh.vertex_normals = -tri_mesh.vertex_normals
    # # tri_mesh.fix_normals()
    # # print(len(tri_mesh.vertices), len(tri_mesh.faces))
    # # pprint.pprint(tri_mesh.face_normals[:10])
    # # pprint.pprint(-tri_mesh.face_normals[:10])
    # # tri_mesh.centroid

    # create a list of colors for each vertex
    midpoint = np.mean(tri_mesh.vertices, axis=0)
    top_colors = np.zeros(shape=tri_mesh.vertices.shape, dtype=float)
    front_colors = np.zeros(shape=tri_mesh.vertices.shape, dtype=float)
    side_colors = np.zeros(shape=tri_mesh.vertices.shape, dtype=float)
    # we can set the colors in a single loop
    for position, top_color, front_color, side_color in zip(tri_mesh.vertices, top_colors, front_colors, side_colors):
        # set the top color
        if position[Y] < midpoint[Y]:
            top_color[X], top_color[Y], top_color[Z] = LT_GRAY[X], LT_GRAY[Y], LT_GRAY[Z]
        else:
            top_color[X], top_color[Y], top_color[Z] = DK_GRAY[X], DK_GRAY[Y], DK_GRAY[Z]
        # set the front color
        if position[Z] < midpoint[Z]:
            front_color[X], front_color[Y], front_color[Z] = LT_GRAY[X], LT_GRAY[Y], LT_GRAY[Z]
        else:
            front_color[X], front_color[Y], front_color[Z] = DK_GRAY[X], DK_GRAY[Y], DK_GRAY[Z]
        # set the side color
        if position[X] > midpoint[X]:
            side_color[X], side_color[Y], side_color[Z] = LT_GRAY[X], LT_GRAY[Y], LT_GRAY[Z]
        else:
            side_color[X], side_color[Y], side_color[Z] = DK_GRAY[X], DK_GRAY[Y], DK_GRAY[Z]

    # create the different color meshes
    tri_mesh.visual.vertex_colors = front_colors
    chair_front_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    tri_mesh.visual.vertex_colors = top_colors
    chair_top_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    tri_mesh.visual.vertex_colors = side_colors
    chair_side_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    # create the scene
    scene = pyrender.Scene(ambient_light=[0.4, 0.4, 0.4])

    # chair rotations
    front_node = pyrender.Node(mesh=chair_front_mesh)
    side_node  = pyrender.Node(mesh=chair_side_mesh, rotation=[ 0, 0.7071068, 0, 0.7071068 ])
    top_node   = pyrender.Node(mesh=chair_top_mesh, rotation=[ 0.7071068, 0, 0, 0.7071068 ])

    scene.add_node(front_node)
    camera = pyrender.OrthographicCamera(xmag=1.5, ymag=1.5)
    front_pose = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.5],
        [0.0, 0.0, 0.0, 1.0],
    ])
    scene.add(camera, pose=front_pose)
    r = pyrender.OffscreenRenderer(300, 300)

    light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=6.0)
    # light = pyrender.SpotLight(color=[1.0, 1.0, 1.0], intensity=2.0,
    #                         innerConeAngle=0.05, outerConeAngle=0.5)
    # light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)

    # light = pyrender.SpotLight(color=np.array([1.0, 1.0, 1.0]), intensity=5.0,
    #                         innerConeAngle=np.pi/10.0,
    #                         outerConeAngle=np.pi/4.0)

    light_pos = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.5],
        [0.0, 0.0, 0.0, 1.0],
    ])
    scene.add(light, pose=light_pos)
    
    color, depth = r.render(scene)
    save = cv2.resize(color, (224, 224), 0, 0, interpolation = cv2.INTER_NEAREST)
    cv2.imwrite(front_path, save)
    
    scene.remove_node(front_node)
    scene.add_node(side_node)
    color, depth = r.render(scene)
    save = cv2.resize(color, (224, 224), 0, 0, interpolation = cv2.INTER_NEAREST)
    cv2.imwrite(side_path, save)

    scene.remove_node(side_node)
    scene.add_node(top_node)
    color, depth = r.render(scene)
    save = cv2.resize(color, (224, 224), 0, 0, interpolation = cv2.INTER_NEAREST)
    cv2.imwrite(top_path, save, )

# import os
# outdir = "./scorer/test/"
# generate_views(
#     os.path.join(outdir, "new_chair.obj"),
#     os.path.join(outdir, "front.png"),
#     os.path.join(outdir, "side.png"),
#     os.path.join(outdir, "top.png"),
# )

# from scorer import score_model
# score = score_model(
#     os.path.join(outdir, "front.png"),
#     os.path.join(outdir, "top.png"),
#     os.path.join(outdir, "side.png"),
# )

# import os
# base_dir = "./dataset-scorer/LeChairs/chairs-data/my-positive/"
# src_dir = "dataset/models/"
# objs = os.listdir(src_dir)
# objs.sort(key=lambda x: int(x.split(".")[0]))
# # pprint.pprint(objs[:100])
# # N_MODELS = 2500
# start = 5395
# i = start
# # print(objs[(start-1)//3:])
# for obj in objs[(start-1)//3:]:
#     print(obj)
#     get_views('./dataset/models/{}'.format(obj), 
#         os.path.join(base_dir, "{}.png".format(i)),
#         os.path.join(base_dir, "{}.png".format(i+1)),
#         os.path.join(base_dir, "{}.png".format(i+2)))
#     i += 3
