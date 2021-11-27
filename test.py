import numpy as np
import torch
import math
import pprint
import copy
from matplotlib.pyplot import box
from parser.draw3dobb import showGenshape
from parser.grassdata import GRASSDataset
from parser.parser import load_models, SimpleObj


def vrrotvec2mat(rotvector):
    s = math.sin(rotvector[3])
    c = math.cos(rotvector[3])
    t = 1 - c
    x = rotvector[0]
    y = rotvector[1]
    z = rotvector[2]
    #m = torch.FloatTensor([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]]).cuda()
    m = torch.FloatTensor([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]])
    return m

def decode_structure(root, model):
    """
    Decode a root code into a tree structure of boxes
    """
    part_i = 0
    # decode = model.sampleDecoder(root_code)
    syms = [torch.ones(8).mul(10)] # create a list
    stack = [root]
    boxes = []
    # print(syms[0])
    while len(stack) > 0:
        node = stack.pop()
        # label_prob = model.nodeClassifier(f)
        # _, label = torch.max(label_prob, 1)
        #label = node.label.item()
        node_type = torch.LongTensor([node.node_type.value]).item()
        if node_type == 1:  # ADJ
            # left, right = model.adjDecoder(f)
            stack.append(node.left)
            stack.append(node.right)
            s = syms.pop()
            syms.append(s)
            syms.append(s)
            # pprint.pprint(syms)
        if node_type == 2:  # SYM
            # left, s = model.symDecoder(f)
            # s = s.squeeze(0)
            stack.append(node.left)
            syms.pop()
            syms.append(node.sym.squeeze(0))
        if node_type == 0:  # BOX
            # grab the model part
            model_part = model["parts"][part_i]
            reBox = node.box
            reBoxes = [reBox]
            s = syms.pop()
            l1 = abs(s[0] + 1)
            l2 = abs(s[0])
            l3 = abs(s[0] - 1)
            print(node.label.item())
            # print(l1, l2, l3)
            if l1 < 0.15:
                # this is a rotation!!!!
                print("l1")
                sList = torch.split(s, 1, 0)
                f1 = torch.cat([sList[1], sList[2], sList[3]]).to(torch.float64)
                f1 = f1/torch.norm(f1)
                f2 = torch.cat([sList[4], sList[5], sList[6]]).to(torch.float64)
                folds = round(1/s[7].item())
                print("folds -> ", folds)
                for i in range(folds-1):
                    rotvector = torch.cat([f1, sList[7].mul(2*3.1415).mul(i+1)]).to(torch.float64)
                    rotm = vrrotvec2mat(rotvector).to(torch.float64)

                    rotated_verts = copy.deepcopy(model_part.verts)
                    for i,vert in enumerate(rotated_verts):
                        center = torch.from_numpy(vert)
                        newcenter = rotm.matmul(center.add(-f2)).add(f2)
                        rotated_verts[i] = newcenter.numpy().astype(float)
                    model_part.append_verts_and_faces(rotated_verts, model_part.faces)

                    # center = torch.cat([bList[0], bList[1], bList[2]])
                    # dir0 = torch.cat([bList[3], bList[4], bList[5]])
                    # dir1 = torch.cat([bList[6], bList[7], bList[8]])
                    # dir2 = torch.cat([bList[9], bList[10], bList[11]])
                    # newcenter = rotm.matmul(center.add(-f2)).add(f2)
                    # newdir1 = rotm.matmul(dir1)
                    # newdir2 = rotm.matmul(dir2)
                    # newbox = torch.cat([newcenter, dir0, newdir1, newdir2])
                    # reBoxes.append(newbox)

                f1 = torch.cat([sList[1], sList[2], sList[3]])
                f1 = f1/torch.norm(f1)
                f2 = torch.cat([sList[4], sList[5], sList[6]])
                folds = round(1/s[7].item())
                bList = torch.split(reBox.data.squeeze(0), 1, 0)
                for i in range(folds-1):
                    rotvector = torch.cat([f1, sList[7].mul(2*3.1415).mul(i+1)])
                    rotm = vrrotvec2mat(rotvector)
                    center = torch.cat([bList[0], bList[1], bList[2]])
                    dir0 = torch.cat([bList[3], bList[4], bList[5]])
                    dir1 = torch.cat([bList[6], bList[7], bList[8]])
                    dir2 = torch.cat([bList[9], bList[10], bList[11]])
                    newcenter = rotm.matmul(center.add(-f2)).add(f2)
                    newdir1 = rotm.matmul(dir1)
                    newdir2 = rotm.matmul(dir2)
                    newbox = torch.cat([newcenter, dir0, newdir1, newdir2])
                    reBoxes.append(newbox)
            if l3 < 0.15:
                # this is a translation!!!!
                print("l3")
                sList = torch.split(s, 1, 0)
                bList = torch.split(reBox.data.squeeze(0), 1, 0)
                trans = torch.cat([sList[1], sList[2], sList[3]])
                trans_end = torch.cat([sList[4], sList[5], sList[6]])
                center = torch.cat([bList[0], bList[1], bList[2]])
                trans_length = math.sqrt(torch.sum(trans**2))
                trans_total = math.sqrt(torch.sum(trans_end.add(-center)**2))
                folds = round(trans_total/trans_length)
                for i in range(folds):
                    center = torch.cat([bList[0], bList[1], bList[2]])
                    dir0 = torch.cat([bList[3], bList[4], bList[5]])
                    dir1 = torch.cat([bList[6], bList[7], bList[8]])
                    dir2 = torch.cat([bList[9], bList[10], bList[11]])
                    newcenter = center.add(trans.mul(i+1))
                    newbox = torch.cat([newcenter, dir0, dir1, dir2])
                    reBoxes.append(newbox)

            if l2 < 0.15:
                # this is a reflecion!!!!
                print("l2")
                sList = torch.split(s, 1, 0)                     # list of symetry data
                # bList = torch.split(reBox.data.squeeze(0), 1, 0) # list of bbox coords
                # pprint.pprint(bList)
                ref_normal = torch.cat([sList[1], sList[2], sList[3]]).to(torch.float64)
                ref_normal = ref_normal/torch.norm(ref_normal)
                ref_point = torch.cat([sList[4], sList[5], sList[6]]).to(torch.float64)
                reflected_verts = copy.deepcopy(model_part.verts)
                for i,vert in enumerate(reflected_verts):
                    center = torch.from_numpy(vert)
                    if ref_normal.matmul(ref_point.add(-center)) < 0:
                        ref_normal = -ref_normal
                    newcenter = ref_normal.mul(2*abs(torch.sum(ref_point.add(-center).mul(ref_normal)))).add(center)
                    reflected_verts[i] = newcenter.numpy().astype(float)
                model_part.append_verts_and_faces(reflected_verts, model_part.faces)


                bList = torch.split(reBox.data.squeeze(0), 1, 0) # list of bbox coords
                # pprint.pprint(bList)
                ref_normal = torch.cat([sList[1], sList[2], sList[3]])
                ref_normal = ref_normal/torch.norm(ref_normal)
                ref_point = torch.cat([sList[4], sList[5], sList[6]])
                center = torch.cat([bList[0], bList[1], bList[2]])
                if ref_normal.matmul(ref_point.add(-center)) < 0:
                    ref_normal = -ref_normal
                newcenter = ref_normal.mul(2*abs(torch.sum(ref_point.add(-center).mul(ref_normal)))).add(center)
                dir0 = torch.cat([bList[3], bList[4], bList[5]])
                dir1 = torch.cat([bList[6], bList[7], bList[8]])
                dir2 = torch.cat([bList[9], bList[10], bList[11]])
                if ref_normal.matmul(dir1) < 0:
                    ref_normal = -ref_normal
                dir1 = dir1.add(ref_normal.mul(-2*ref_normal.matmul(dir1)))
                if ref_normal.matmul(dir2) < 0:
                    ref_normal = -ref_normal
                dir2 = dir2.add(ref_normal.mul(-2*ref_normal.matmul(dir2)))
                newbox = torch.cat([newcenter, dir0, dir1, dir2])
                reBoxes.append(newbox)

            # print(node.label.item(), "->", len(reBoxes))
            boxes.extend(reBoxes)
            part_i += 1

    return boxes


if __name__ == "__main__":
    # 66, 4037, 2177
    # 6012, 3453, 3336, 2234, 1392
    # 653, 18, 734, 1791, 2207, 3663, 4903, 2428, 722, 4294
    models_parts = load_models([3453])
    # SimpleObj.save("notmerged", models_parts[0]["parts"][8])

    boxes = decode_structure(models_parts[0]["symh_tree"].root, models_parts[0])
    pprint.pprint(models_parts[0])

    # showGenshape(boxes)
    SimpleObj.save("merged", SimpleObj.merge_objs(models_parts[0]["parts"]))
    # SimpleObj.save("merged", models_parts[0]["parts"][8])
    
    # pprint.pprint(boxes[0])
    # pprint.pprint(models_parts)
