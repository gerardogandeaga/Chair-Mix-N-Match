import os
from scipy.io import loadmat
import json
import numpy as np
import pprint
import math
import torch
import copy
from sklearn.cluster import KMeans

from .grassdata import GRASSDataset


"""
Simple 
"""

DATASET_DIR = "./input/symh"
CHAIR_PARTS_DIR = "./input/partnet"

class SimpleObj:
	"""
	Simple class that holds the vertex and faces information.
	The faces values are indexed from 1-N, make sure to subtract 1 to
	get the actual vertex when rendering.
	"""

	# Takes a list of SimpleObjs and returns a new merged simple obj
	@staticmethod
	def merge_objs(simple_objs) -> 'SimpleObj':
		
		# new_obj = simple_objs[0]
		new_obj = SimpleObj.create(simple_objs[0].verts, copy.deepcopy(simple_objs[0].faces))

		if len(simple_objs) == 1:
			return new_obj

		# merge new simple objs 
		for simple_obj in simple_objs[1:]:
			n_verts = len(new_obj.verts)
			faces = copy.deepcopy(simple_obj.faces)
			faces = list(map(lambda f: f + n_verts, faces))
			new_obj.verts.extend(simple_obj.verts)
			new_obj.faces.extend(faces)

		return new_obj

	@staticmethod
	def save(file_name, simple_obj):
		"""
		Saves the simple obj to a file path
		"""
		with open("{}.obj".format(file_name), "w") as file:
			for v in simple_obj.verts:
				values = " ".join(str(x) for x in v.tolist())
				file.write("v " + values + "\n")
			
			for f in simple_obj.faces:
				values = " ".join(str(x) for x in f.tolist())
				file.write("f " + values + "\n")

	@staticmethod
	def create(verts, faces):
		simple_obj = SimpleObj(None, None)
		simple_obj.verts = verts
		simple_obj.faces = faces
		return simple_obj

	def __init__(self, model_name, obj_file):
		self.verts = []
		self.faces = []

		if model_name != None:
			full_path = os.path.join(CHAIR_PARTS_DIR, "{}/objs/{}.obj".format(model_name, obj_file))
			with open(full_path) as f:
				lines = f.readlines()
				self.verts = [np.array(line.split()[1:], dtype=float) for line in lines if line.startswith("v")]
				self.faces = [np.array(line.split()[1:], dtype=int)  for line in lines if line.startswith("f")]

	def append_verts_and_faces(self, verts, faces):
		n_verts = len(self.verts)
		faces = list(map(lambda f: f + n_verts, faces))
		self.verts.extend(verts)
		self.faces.extend(faces)

class Model:

	def __init__(self, data):
		self.data = data # save the raw map
		self.symh_id = data["symh_id"]
		self.obj_id = data["obj_id"]
		self.labels = data["labels"]
		self.parts = data["parts"]
		self.symh_tree = data["symh_tree"]
		self.bboxes = []
		self.components = self._decode_symh_tree() # decode the symmetry tree to get all the info for the model


	def _decode_symh_tree(self):
		self.bboxes, bbox_labels, new_parts = self._decode_structure()
		bboxes = list(map(lambda x: x[:].squeeze(0).numpy(), self.bboxes))
		bbox_centers = list(map(lambda x: x[0:3], bboxes))

		# create a tuple of bboxes and their labels
		bboxes_labelled = []
		for bbox,label in zip(bboxes, bbox_labels):
			bboxes_labelled.append((label, bbox))

		# group the armrest parts
		backs,back_is = [],[]
		seats,seats_is = [],[]
		legs,legs_is = [],[]
		arm_rests,arm_rests_is = [],[]
		# get the centers
		i = 0
		has_arm_rests = False
		for bbox,label in zip(bboxes, bbox_labels):
			if label == 0:
				backs.append(bbox[0:3])
				back_is.append(i)
			if label == 1:
				seats.append(bbox[0:3])
				seats_is.append(i)
			if label == 2:
				legs.append(bbox[0:3])
				legs_is.append(i)
			if label == 3:
				arm_rests.append(bbox[0:3])
				arm_rests_is.append(i)
				has_arm_rests = True
			i += 1

		# perform k-means grouping
		tmp_parts = []

		X = backs
		kmeans = KMeans(n_clusters=1, random_state=0).fit(X)
		back_group = kmeans.labels_
		back_center = kmeans.cluster_centers_
		X = seats
		kmeans = KMeans(n_clusters=1, random_state=0).fit(X)
		seat_group = kmeans.labels_
		seat_center = kmeans.cluster_centers_
		X = legs
		# legs can vary
		kmeans1 = KMeans(n_clusters=1, random_state=0).fit(X) # for one leg chairs
		kmeans4 = None
		if len(X) >= 4:
			kmeans4 = KMeans(n_clusters=4, random_state=0).fit(X) # for 4 leg chairs
		has_four_legs = False
		if (kmeans4 is not None) and (len(kmeans4.labels_) == 4):
			legs_group = kmeans4.labels_
			legs_centers = kmeans4.cluster_centers_
			has_four_legs = True
		else:
			legs_group = kmeans1.labels_
			legs_centers = kmeans1.cluster_centers_
			has_four_legs = False
		
		arm_rests_centers = [[]]
		if has_arm_rests:
			X = arm_rests
			kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
			arm_rests_group = kmeans.labels_
			arm_rests_centers = kmeans.cluster_centers_

		back_objs, seat_objs, legs_objs, armrests_objs = [[]], [[]], [[],[],[],[]], [[],[]]
		bi,si,li,ai = 0,0,0,0
		for label in bbox_labels:
			if label == 0:
				group_idx = back_group[bi]
				part_idx = back_is[bi] # index back into the parts
				back_objs[group_idx].append(new_parts[part_idx])
				bi += 1
			if label == 1:
				group_idx = seat_group[si]
				part_idx = seats_is[si] # index back into the parts
				seat_objs[group_idx].append(new_parts[part_idx])
				si += 1
			if label == 2:
				group_idx = legs_group[li]
				part_idx = legs_is[li] # index back into the parts
				legs_objs[group_idx].append(new_parts[part_idx])
				li += 1
			if label == 3:
				group_idx = arm_rests_group[ai]
				part_idx = arm_rests_is[ai] # index back into the parts
				armrests_objs[group_idx].append(new_parts[part_idx])
				ai += 1

		# TODO: remove test
		back = SimpleObj.merge_objs(back_objs[0])
		seat = SimpleObj.merge_objs(seat_objs[0])
		legs = []
		arm_rests = []
		if has_four_legs:
			legs = [SimpleObj.merge_objs(legs_objs[i]) for i in range(4)]
		else:
			legs.append(SimpleObj.merge_objs(legs_objs[0]))
		if has_arm_rests:
			arm_rests = [SimpleObj.merge_objs(armrests_objs[i]) for i in range(2)]

		parts = {
			"objs": {
				"back": back, 
				"seat": seat, 
				"legs": legs, 
				"arm_rests": arm_rests},
			"part_centers": {
				"back": back_center, 
				"seat": seat_center, 
				"legs": legs_centers, 
				"arm_rests": arm_rests_centers,
				},
		}

		self.fix_model(parts)

		return parts
		# merge the part objs

	def fix_model(self, parts):
		"""
		Some models have weird tranlation artifacts
		this function will fix some specific models
		"""
		objs = parts["objs"]
		centers = parts["part_centers"]
		if self.symh_id == 1392:
			# only 1 leg
			self.translate(objs["legs"][0], centers["legs"][0], np.array([0, 0.15, 0]))
			self.translate(objs["back"], centers["back"], np.array([0, 0, 0.05]))
			# left arm
			self.translate(objs["arm_rests"][0], centers["arm_rests"][0], np.array([0.02, 0, 0]))
			# right arm
			self.translate(objs["arm_rests"][1], centers["arm_rests"][1], np.array([-0.02, 0, 0]))


	# this will translate the part and its part center
	def translate(self, part, part_center, translation):
		part_center += translation
		for vert in part.verts:
			vert += translation

	def _vrrotvec2mat(self, rotvector):
		"""
		Computes a rotation vector 
		"""
		s = math.sin(rotvector[3])
		c = math.cos(rotvector[3])
		t = 1 - c
		x = rotvector[0]
		y = rotvector[1]
		z = rotvector[2]
		#m = torch.FloatTensor([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]]).cuda()
		m = torch.FloatTensor([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]])
		return m

	def _decode_structure(self):
		"""
		Decode a root code into a tree structure of boxes
		"""
		part_i = 0
		# decode = model.sampleDecoder(root_code)
		syms = [torch.ones(8).mul(10)] # create a list
		stack = [self.symh_tree.root]
		boxes = []
		boxes_labels = []
		new_parts = []
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
			if node_type == 2:  # SYM
				# left, s = model.symDecoder(f)
				# s = s.squeeze(0)
				stack.append(node.left)
				syms.pop()
				syms.append(node.sym.squeeze(0))
			if node_type == 0:  # BOX
				# grab the model part
				model_part = self.parts[part_i]
				reBox = node.box
				reBoxes = [reBox]
				new_parts.append(model_part)
				s = syms.pop()
				l1 = abs(s[0] + 1) # rotation marker
				l2 = abs(s[0])     # reflection marker
				l3 = abs(s[0] - 1) # translation marker
				if l1 < 0.15:
					# this is a rotation!!!!
					sList = torch.split(s, 1, 0)
					f1 = torch.cat([sList[1], sList[2], sList[3]]).to(torch.float64)
					f1 = f1/torch.norm(f1)
					f2 = torch.cat([sList[4], sList[5], sList[6]]).to(torch.float64)
					folds = round(1/s[7].item()) # number of times to rotate
					for i in range(folds-1):
						rotvector = torch.cat([f1, sList[7].mul(2*3.1415).mul(i+1)]).to(torch.float64)
						rotm = self._vrrotvec2mat(rotvector).to(torch.float64)

						rotated_verts = copy.deepcopy(model_part.verts)
						for i,vert in enumerate(rotated_verts):
							center = torch.from_numpy(vert)
							newcenter = rotm.matmul(center.add(-f2)).add(f2)
							rotated_verts[i] = newcenter.numpy().astype(float)
						# model_part.append_verts_and_faces(rotated_verts, model_part.faces)
						new_parts.append(SimpleObj.create(rotated_verts, model_part.faces))

					f1 = torch.cat([sList[1], sList[2], sList[3]])
					f1 = f1/torch.norm(f1)
					f2 = torch.cat([sList[4], sList[5], sList[6]])
					folds = round(1/s[7].item())
					bList = torch.split(reBox.data.squeeze(0), 1, 0)
					for i in range(folds-1):
						rotvector = torch.cat([f1, sList[7].mul(2*3.1415).mul(i+1)])
						rotm = self._vrrotvec2mat(rotvector)
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
					sList = torch.split(s, 1, 0)
					bList = torch.split(reBox.data.squeeze(0), 1, 0)
					trans = torch.cat([sList[1], sList[2], sList[3]])
					trans_end = torch.cat([sList[4], sList[5], sList[6]])
					center = torch.cat([bList[0], bList[1], bList[2]])
					trans_length = math.sqrt(torch.sum(trans**2))
					trans_total = math.sqrt(torch.sum(trans_end.add(-center)**2))
					folds = round(trans_total/trans_length) # number of trime to translate? doesnt seem to work well
					for i in range(folds):
						center = torch.cat([bList[0], bList[1], bList[2]])
						dir0 = torch.cat([bList[3], bList[4], bList[5]])
						dir1 = torch.cat([bList[6], bList[7], bList[8]])
						dir2 = torch.cat([bList[9], bList[10], bList[11]])
						newcenter = center.add(trans.mul(i+1))
						newbox = torch.cat([newcenter, dir0, dir1, dir2])
						reBoxes.append(newbox)
						new_parts.append(model_part)

				if l2 < 0.15:
					# this is a reflecion!!!!
					sList = torch.split(s, 1, 0)                     # list of symetry data
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
					# model_part.append_verts_and_faces(reflected_verts, model_part.faces)
					new_parts.append(SimpleObj.create(reflected_verts, model_part.faces))

					bList = torch.split(reBox.data.squeeze(0), 1, 0) # list of bbox coords
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

				# create box labels
				boxes_labels.extend([self.labels[part_i] for b in reBoxes])
				boxes.extend(reBoxes)
				part_i += 1

		return boxes, boxes_labels, new_parts

	@staticmethod
	def _create_chair_part(model_name, all_obj_file_names, pmi) -> "SimpleObj":
		# recall, pmi is a list of indices from 1-N into the "objs" array
		# we need to go from 0-(N-1)
		part_obj_files = [obj_f for i,obj_f in enumerate(all_obj_file_names) if i in (pmi-1)] # simple filter, gets names only if its in pmi-1 list
		
		objs = [SimpleObj(model_name, obj_file) for obj_file in part_obj_files]
		merged = SimpleObj.merge_objs(objs)
		return merged

	@staticmethod
	def load_models(models):
		# first load the trees
		model_trees = GRASSDataset("chair", models)

		# we want to get 3-4 parts: back, seat, leg and/or armrest
		model_parts = []

		for mi,model in enumerate(models):
			# pmi: part mesh indices
			# obj_name: name of the obj file this model belongs to. This name is actually a number and will be used to get the data from the _partnet-chairs
			pmi_and_obj_name = loadmat(os.path.join(DATASET_DIR, "part mesh indices/{}.mat".format(model)))
			labels = loadmat(os.path.join(DATASET_DIR, "labels/{}.mat".format(model)))

			# get the pmis
			pmis = pmi_and_obj_name["cell_boxs_correspond_objSerialNumber"][0]
			pmis = list(map(lambda x: x[0], pmis)) 
			# get the obj name
			obj_name = pmi_and_obj_name["shapename"][0]
			# part type labels
			labels = labels["label"][0]

			# now we want to get the parts of the model
			# the pmis is an array of array, where each inter array have elements that index 
			# into the top level obj list in the result_after_merging files.
			# the objs is a list of .obj files that map to a component of the decomosed object.
			# we need for each pmi, we need to grab the decomposed .objs and merge them to create
			# a single part of a chair.
			obj_dir = os.path.join(CHAIR_PARTS_DIR, format(obj_name))
			with open(os.path.join(obj_dir, "result_after_merging.json")) as f:
				result_after_merging_json = json.load(f)
				all_obj_file_names = result_after_merging_json[0]["objs"]
				parts = []
				for i,pmi in enumerate(pmis):
					part = Model._create_chair_part(obj_name, all_obj_file_names, pmi)
					parts.append(part)

				# create a Model object and append it to a list
				model_parts.append(Model({
					"symh_id": model, 
					"obj_id": obj_name, 
					"labels": labels, 
					"parts": parts,
					"symh_tree": model_trees[mi]
				}))

		return model_parts

