# -------------------------
# Parser Tree Node
# -------------------------
class TreeNode:
    def __init__(self, label):
        self.label = label
        self.children = []

    def add(self, child):
        if child is not None:
            self.children.append(child)

    def pretty(self, level=0):
        out = " " * (level * 4) + self.label + "\n"
        for c in self.children:
            out += c.pretty(level + 1)
        return out
