from ktree import KTree

tree = KTree([(0., 1.), (0., 1.)], 2)

tree.insert([0.1, 0.1])
tree.insert([0.01, 0.2])
tree.insert([0.01, 0.5])

for axis, nodes in tree:
    print((axis, nodes))
