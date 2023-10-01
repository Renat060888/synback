
class NodeSourceType:
    JOURNAL: int = 1
    LOCAL_FILE_SYSTEM: int = 2
    GOOGLE_DRIVE: int = 3
    UNDEFINED: int = 9999

class Node:
    def __init__(self, name: str, timestamp: str, type: str = "file", data = None):
        self.source_type: int = NodeSourceType.UNDEFINED
        self.name: str = name
        self.timestamp: str = timestamp
        self.type: str = type
        self.data = data
        self.parent: Node = None
        self.children: set[Node] = set()
        self.label_new: bool = False
        self.label_removed: bool = False
        # ?
        self.label_fresher: bool = False

    def __call__(self, msg: str):
        print("this is Functor with message: {}".format(msg))

    def __hash__(self):
        return hash(self.name + self.type)

    def __eq__(self, other):
        if other == None:
            return False
        return self.name == other.name and self.type == other.type