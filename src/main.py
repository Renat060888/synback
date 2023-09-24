import os
import json
import copy

class MyTestClass:
    def __init__(self):
        print("CTOR of MyTestClass")
        pass

    def SayBlaBla(self):
        pass

class Node:
    def __init__(self, name: str, timestamp: str, type: str = "file", data = None):
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

class NodeDeserializer:
    def __init__(self, file_full_name: str):
        self.dict_from_json: dict = {}
        self.root_node: Node = None

        with open(file_full_name, 'r') as json_file:
            self.dict_from_json = json.load(json_file)

        self.ConvertToTree()

    def GetRootNode(self) -> Node:
        return self.root_node

    def ConvertToTree(self):
        if len(self.dict_from_json.items()) != 1:
            raise Exception("root items in 'dict from json' is zero or greater than 1")

        root_node: Node = None
        for key, value in self.dict_from_json.items():
            root_node = Node(key, value["timestamp"], value["type"])
            self.FillNode(root_node, value["content"])

        self.root_node = root_node

    def FillNode(self, node: Node, dict_from_json: dict):
        for key, value in dict_from_json.items():
            child = Node(key, value["timestamp"], value["type"])
            node.children.add(child)
            child.parent = node

            if child.type == "dir":
                self.FillNode(child, value["content"])

class NodeSerializer:
    def __init__(self, file_full_name: str):
        self.json_file_name: str = file_full_name
        self.dict_for_json: dict = {}

    def __call__(self, node: Node) -> bool:
        # this is root element in json
        if len(self.dict_for_json) == 0:
            if node.parent:
                print("only node without parent can be root json element")
                return False

            self.dict_for_json = {node.name : {"type" : node.type, "timestamp" : node.timestamp, "content" : {}}}
            return True

        # find path for place
        if not node.parent:
            print("dict already has root, and only root node can be without parent")
            return False

        parent_elements_path: list[str] = [node.parent.name]
        parent_node: Node = node.parent
        while parent_node.parent:
            parent_node = parent_node.parent
            parent_elements_path.append(parent_node.name)
        parent_elements_path.reverse()

        # find place itself
        place_for_insert = self.dict_for_json
        for elem in parent_elements_path:
            place_for_insert = place_for_insert.get(elem)
            if place_for_insert:
                place_for_insert = place_for_insert.get("content")
            else:
                print("one of node's [{}] parents [{}] is not found in dictionary for json".format(node.name, elem))
                return False

        # append
        place_for_insert[node.name] = {"type" : node.type, "timestamp" : node.timestamp}
        if node.type == "dir":
            place_for_insert[node.name]["content"] = {}

        return True

    def Dump(self) -> bool:
        if len(self.json_file_name) == 0:
            print("dump file name is empty")
            return False

        if len(self.dict_for_json) == 0:
            print("nothing to dump")
            return False

        with open(self.json_file_name, 'w', encoding='utf8') as json_file:
            json.dump(self.dict_for_json, json_file, allow_nan=True)

        return True

class FileSystemTree:
    def __init__(self, root: Node = None):
        if root:
            self.root = root
        else:
            self.root: Node = None

    def AddNode(self, node: Node, parent_path: list[str]) -> bool:
        if len(parent_path) == 0:
            print("target path is empty")
            return False

        # this is first node
        if self.root == None:
            if len(parent_path) != 1:
                print("this is first node in tree, but path has more than one element in path")
                return False

            if node.type != "dir":
                print("first node must be directory type")
                return False

            self.root = node
            return True
        # find parent for this node
        else:
            if self.root.name != parent_path[0]:
                print("first element of path don't match to root node name")
                return False
            parent_path.pop(0)

            parent_node: Node = self.FindNode(self.root, parent_path)
            if parent_node:
                parent_node.children.add(node)
                node.parent = parent_node
                return True
            else:
                return False

    def FindNode(self, node: Node, target_path: list[str]) -> Node:
        if len(target_path) == 0:
            return node

        # try to find appropriate node
        for child in node.children:
            if child.name == target_path[0]:
                target_path.pop(0)
                return self.FindNode(child, target_path)

        return None

    def VisitNode(self, node: Node, node_processor):
        if node != None:
            node_processor(node)

            for child in node.children:
                self.VisitNode(child, node_processor)

    def Traverse(self, node_processor):
        self.VisitNode(self.root, node_processor)

def GetNodeNames(nodes: set[Node]):
    names: list[str] = []
    for node in nodes:
        names.append(node.name)
    return names

def CreateDifferenceTree(first_tree_root: Node, second_tree_root: Node) -> Node:
    assert(first_tree_root == second_tree_root)

    if len(first_tree_root.children) == 0 and len(second_tree_root.children) == 0:
        return copy.deepcopy(first_tree_root)

    # find difference
    new_children_in_first_node: set[Node] = first_tree_root.children.difference(second_tree_root.children)
    removed_children_in_first_node: set[Node] = second_tree_root.children.difference(first_tree_root.children)
    common_childs: set[Node] = first_tree_root.children.intersection(second_tree_root.children)

    print("new childs in 1st node: {}".format(GetNodeNames(new_children_in_first_node)))
    print("removed childs in 1st node: {}".format(GetNodeNames(removed_children_in_first_node)))
    print("common childs: {}".format(GetNodeNames(common_childs)))

    result = Node(first_tree_root.name, first_tree_root.timestamp, first_tree_root.type)

    # add info about changed entities
    for new_child in new_children_in_first_node:
        child: Node = copy.deepcopy(new_child)
        child.label_new = True
        result.children.add(child)

    for removed_child in removed_children_in_first_node:
        child: Node = copy.deepcopy(removed_child)
        child.label_removed = True
        result.children.add(child)

    # TODO: modified

    # add common entities
    list_repr_of_1st_node_children: list[Node] = list(first_tree_root.children)
    list_repr_of_2nd_node_children: list[Node] = list(second_tree_root.children)
    for common_entity in common_childs:
        first_node_child: Node = None
        for child in list_repr_of_1st_node_children:
            if child == common_entity:
                first_node_child = child
                break
        second_node_child: Node = None
        for child in list_repr_of_2nd_node_children:
            if child == common_entity:
                second_node_child = child
                break

        if first_node_child and second_node_child:
            result.children.add(CreateDifferenceTree(first_node_child, second_node_child))
        else:
            print("common entity with name '{}' not found in one of nodes".format((common_entity.name)))

    return result

class NodePrinter:
    def __call__(self, node: Node):
        state: str = "_"
        if node.label_new:
            state = "new"
        elif node.label_removed:
            state = "removed"
        print("node '{}' type '{}' ts '{}' state '{}'".format(node.name, node.type, node.timestamp, state))

def TestDifference():
    node_1_0 = Node("a", ".")
    node_1_1 = Node("b", ".")
    node_1_2 = Node("c", ".")
    node_1 = Node("1st", "2023", "dir")
    node_1.children.add(node_1_0)
    node_1.children.add(node_1_1)
    node_1.children.add(node_1_2)

    node_2_0 = Node("a", ".,")
    node_2_1 = Node("b", ".,")
    node_2_2 = Node("w", ".,")
    node_2 = Node("1st", "2023", "dir")
    node_2.children.add(node_2_0)
    node_2.children.add(node_2_1)
    node_2.children.add(node_2_2)

    diff_tree = FileSystemTree(CreateDifferenceTree(node_1, node_2))
    print("diff tree >")
    diff_tree.Traverse(NodePrinter())
    print("diff tree <")

def PrintHiToConsole(name: str):
    print('Hi, {}'.format(name))  # Press Ctrl+F8 to toggle the breakpoint.

    #
    s1 = {Node("a", "")}
    s2 = {Node("b", ""), Node("a", "")}

    diff_set = s1.symmetric_difference(s2)
    print("diff >")
    for node in diff_set:
        print(node.name)
    print("diff <")
    #

    path: str = "/var/log"


    node1 = Node("var", "2017-07-15", "dir")
    node2 = Node("log", "2020-03-11", "dir")
    node3 = Node("mosesd.log", "2012-04-01")

    tree = FileSystemTree()
    tree.AddNode(node1, ["/"])
    tree.AddNode(node2, ["var"])
    tree.AddNode(node3, ["var", "log"])

    dump_file_name: str = "dumped_tree.json"

    serializer = NodeSerializer(dump_file_name)
    tree.Traverse(serializer)
    serializer.Dump()

    deserializer = NodeDeserializer(dump_file_name)
    root_node: Node = deserializer.GetRootNode()
    tree: FileSystemTree(root_node)



    tree.Traverse(NodePrinter())

    ml = list()

    ii_abc: int = 1

    mtc2 = MyTestClass()
    mtc2.SayBlaBla()


    ml.append(5)

    # traverse root directory, and list directories as dirs and files as files
    for root_path, dir_names, file_names in os.walk("./pseudo_cloud"):
        path: list[str] = root_path.split(os.sep)
        print((len(path) - 1) * '-->', os.path.basename(root_path))
        for file_name in file_names:
            print(len(path) * '---', file_name)
            print(root_path + "</>" + file_name)

    TestDifference()


class TreeFactory:
    def CreateTree(self):
        pass


class FileSystemReader(TreeFactory):
    def __init__(self, dir_full_path: str):
        self.dir_full_path = dir_full_path

    def CreateTree(self):
        print("create tree by FileSystemReader")

class JournalReader(TreeFactory):
    def __init__(self, file_full_path: str):
        self.file_full_path = file_full_path

    def CreateTree(self):
        print("create tree by JournalReader")

class GoogleDriveReader(TreeFactory):
    def __init__(self, token_full_path: str, creds_full_path: str):
        self.token_full_path = token_full_path
        self.creds_full_path = creds_full_path

    def CreateTree(self):
        print("create tree by GoogleDriveReader")

# entry point
if __name__ == '__main__':
    PrintHiToConsole('PyCharm')

    tf1: TreeFactory = FileSystemReader("bla")
    tf2: TreeFactory = JournalReader("bla")
    tf3: TreeFactory = GoogleDriveReader("bla", "ble")
    tf1.CreateTree()
    tf2.CreateTree()
    tf3.CreateTree()

    # 0.
    # read cfg file: workspace address, cloud address
    # create journal if not exist
    # 1.
    # compare workspace state with journal -> workspace tree (new/removed)
    # connect to cloud -> cloud tree (new/removed)
    # 2.
    # compare workspace tree <-> cloud tree: difference tree
    # execute difference tree <!> log every action (create, delete, udpate)
    # 3.
    # actualize journal (overwrite with refreshed workspace tree)
    # remind about monthly backup
    # 4. work on modified entities...
