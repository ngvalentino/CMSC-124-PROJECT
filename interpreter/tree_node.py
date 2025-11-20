# -------------------------
# Parser Tree Node
# -------------------------
class TreeNode:
    def __init__(self, node_type, value=None, line=None):
        self.node_type = node_type  # e.g., "VAR_DECL", "FUNC_CALL"
        self.value = value          # e.g., var name, literal value, operator
        self.line = line            # line number from lexer
        self.children = []

    def add(self, child):
        if child is not None:
            self.children.append(child)

    def pretty(self, level=0):
        indent = " " * (level * 4)
        out = f"{indent}{self.node_type}: {self.value}\n"
        for c in self.children:
            out += c.pretty(level + 1)
        return out
