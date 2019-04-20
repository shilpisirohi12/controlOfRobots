class Tree(object):
    def __init__(self):
        self.left = None
        self.child = []
        self.data = []

    def createChildren(self, amount):
        for i in range(0, amount):
            self.child.append(Tree())

    def setChildrenValues(self, list):
        for i in range(0, len(list)):
            self.data.append(list[i])


root = Tree()
root.createChildren(3)
root.setChildrenValues([5, 6, 7])

root.child[0].createChildren(2)
root.child[0].setChildrenValues([1, 2])

# print some values in the tree
print(root.data[0],"  ",root.data[1],"  ",root.data[2])
print(root.child[0].data[0],"  ",root.child[0].data[1])