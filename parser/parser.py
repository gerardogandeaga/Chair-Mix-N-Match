import os
from scipy.io import loadmat
import json
import numpy as np
import pprint

from .grassdata import GRASSDataset

"""
Simple 
"""

DATASET_DIR = "./dataset"
CHAIR_PARTS_DIR = "./_partnet-chairs"

class SimpleObj:

	# Takes a list of SimpleObjs and returns a new merged simple obj
	@staticmethod
	def merge_objs(simple_objs) -> 'SimpleObj':
		new_obj = simple_objs[0]

		if len(simple_objs) == 1:
			return new_obj

		# merge new simple objs 
		for simple_obj in simple_objs[1:]:
			n_verts = len(new_obj.verts)
			faces = simple_obj.faces
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

	def __init__(self, model_name, obj_file):
		self.verts = []
		self.faces = []
		full_path = os.path.join("./_partnet-chairs/Chair_parts/{}/objs/{}.obj".format(model_name, obj_file))
		with open(full_path) as f:
			lines = f.readlines()
			self.verts = [np.array(line.split()[1:], dtype=float) for line in lines if line.startswith("v")]
			self.faces = [np.array(line.split()[1:], dtype=int)  for line in lines if line.startswith("f")]

	def append_verts_and_faces(self, verts, faces):
		n_verts = len(self.verts)
		faces = list(map(lambda f: f + n_verts, faces))
		self.verts.extend(verts)
		self.faces.extend(faces)

def create_chair_part(model_name, all_obj_file_names, pmi) -> "SimpleObj":
	# recall, pmi is a list of indices from 1-N into the "objs" array
	# we need to go from 0-(N-1)
	part_obj_files = [obj_f for i,obj_f in enumerate(all_obj_file_names) if i in (pmi-1)] # simple filter, gets names only if its in pmi-1 list
	
	objs = [SimpleObj(model_name, obj_file) for obj_file in part_obj_files]
	merged = SimpleObj.merge_objs(objs)
	return merged

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
		obj_dir = os.path.join(CHAIR_PARTS_DIR, "Chair_parts/{}".format(obj_name))
		with open(os.path.join(obj_dir, "result_after_merging.json")) as f:
			result_after_merging_json = json.load(f)
			all_obj_file_names = result_after_merging_json[0]["objs"]
			parts = []
			for i,pmi in enumerate(pmis):
				part = create_chair_part(obj_name, all_obj_file_names, pmi)
				parts.append(part)
				# SimpleObj.save("t{}".format(i), part)

			model_parts.append({
				"symh_id": model, 
				"obj_id": obj_name, 
				"labels": labels, 
				"parts": parts,
				"symh_tree": model_trees[mi]
			})
			# SimpleObj.save("merged", SimpleObj.merge_objs(parts))

	return model_parts
