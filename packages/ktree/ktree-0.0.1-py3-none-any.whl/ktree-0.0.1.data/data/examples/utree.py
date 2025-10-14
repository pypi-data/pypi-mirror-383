from ktree import KTree

tree = KTree([(0, 10)], 2)

tree.insert([2])
tree.insert([1])
tree.insert([2])
tree.insert([9])

for axis, nodes in tree.sort():
    print((axis, nodes))
