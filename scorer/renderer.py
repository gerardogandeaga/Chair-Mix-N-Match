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

def get_views(input_obj, front_path, side_path, top_path):
    # creates a timesh with the given input file
    tri_mesh = trimesh.load(input_obj)
    # tri_mesh.apply_translation(np.array([1, , 1]))

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

    tri_mesh.visual.vertex_colors = front_colors
    chair_front_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    tri_mesh.visual.vertex_colors = top_colors
    chair_top_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    tri_mesh.visual.vertex_colors = side_colors
    chair_side_mesh = pyrender.Mesh.from_trimesh(tri_mesh)

    scene = pyrender.Scene(ambient_light=[0.4, 0.4, 0.4])

    # chair rotations
    front_node = pyrender.Node(mesh=chair_front_mesh)
    side_node  = pyrender.Node(mesh=chair_side_mesh, rotation=[ 0, 0.7071068, 0, 0.7071068 ])
    top_node   = pyrender.Node(mesh=chair_top_mesh, rotation=[ 0.7071068, 0, 0, 0.7071068 ])

    scene.add_node(front_node)
    camera = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)
    front_pose = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.5],
        [0.0, 0.0, 0.0, 1.0],
    ])
    scene.add(camera, pose=front_pose)
    r = pyrender.OffscreenRenderer(300, 300)
    
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

import os
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
