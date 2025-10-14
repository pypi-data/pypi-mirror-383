import random

from ktree import KTree

N_DIMENSION = 3

tree = KTree([(0., 1.) for _ in range(N_DIMENSION)], 1)

for _ in range(3):
    tree.insert([random.uniform(0, 1) for _ in range(N_DIMENSION)])

for axis, nodes in tree.sort():
    print((axis, nodes))
