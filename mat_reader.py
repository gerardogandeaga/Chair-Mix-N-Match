import scipy.io


print("PMI:", scipy.io.loadmat("./dataset/part mesh indices/3.mat"))
print("Lab:", scipy.io.loadmat("./dataset/labels/3.mat"))
print("BBs:", scipy.io.loadmat("./dataset/boxes/3.mat"))
print("SYM:", scipy.io.loadmat("./dataset/syms/3.mat"))
print("Ops:", scipy.io.loadmat("./dataset/ops/3.mat"))
# print("OBB:", scipy.io.loadmat("./dataset/obbs/1095.mat"))