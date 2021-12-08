import trimesh
import pyrender
import numpy as np
import matplotlib.pyplot as plt


def getViews(inputFileName):
    triMesh = trimesh.load("./_partnet-chairs/" + inputFileName)
    triMesh.
    chairMesh = pyrender.Mesh.from_trimesh(triMesh)
    scene = pyrender.Scene(ambient_light=[0.4, 0.4, 0.4])
    frontNode = pyrender.Node(mesh=chairMesh)
    sideNode = pyrender.Node(mesh=chairMesh, rotation=[ 0, 0.7071068, 0, 0.7071068 ])
    topNode = pyrender.Node(mesh=chairMesh, rotation=[ 0.7071068, 0, 0, 0.7071068 ])
    scene.add_node(frontNode)
    camera = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)
    front_pose = np.array([
        [1.0, 0.0,   0.0,   0.0],
        [0.0,  1.0, 0.0, 0.0],
        [0.0,  0.0,   1.0,   1.3],
        [0.0,  0.0, 0.0, 1.0],
    ])
    scene.add(camera, pose=front_pose)
    light = pyrender.SpotLight(color=np.array([1.0, 1.0, 1.0]), intensity=4.0,
                            innerConeAngle=np.pi/10.0,
                            outerConeAngle=np.pi/4.0)
    scene.add(light, pose=front_pose)
    r = pyrender.OffscreenRenderer(300, 300)
    color, depth = r.render(scene)
    plt.figure(figsize=(5, 5))
    plt.subplot(1, 2, 1)
    plt.axis('off')
    plt.imshow(color)
    plt.savefig('./scorer/renderOutput/front.png')
    
    scene.remove_node(frontNode)
    scene.add_node(sideNode)
    color, depth = r.render(scene)
    plt.imshow(color)
    plt.savefig('./scorer/renderOutput/side.png')

    scene.remove_node(sideNode)
    scene.add_node(topNode)
    color, depth = r.render(scene)
    plt.imshow(color)
    plt.savefig('./scorer/renderOutput/top.png')

# getViews('test_obj-1.obj')
