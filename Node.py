class Node:
    def __init__(self, value: str) -> None:
        self.relation = []
        self.neighbor = []
        self.value = value

    def __str__(self) -> str:
        return f"Node: {self.value}, Relations: {self.relation}, Neighbors: {self.neighbor}"

    def add_relation(self, relation: str, node2: 'Node') -> None:
        self.relation.append(relation)
        self.neighbor.append(node2)
