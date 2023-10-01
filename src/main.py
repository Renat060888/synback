
import os
import copy

from node import Node
import serialization
import google_drive_client

class MyTestClass:
    def __init__(self):
        print("CTOR of MyTestClass")
        pass

    def SayBlaBla(self):
        pass





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

            parent_node = self.FindNode(self.root, parent_path)
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

def CreateDifferenceTree(node_1st: Node, node_2nd: Node) -> Node:
    assert(node_1st == node_2nd)

    if len(node_1st.children) == 0 and len(node_2nd.children) == 0:
        return copy.deepcopy(node_1st)

    # find difference
    new_in_1st = node_1st.children.difference(node_2nd.children)
    removed_in_1st = node_2nd.children.difference(node_1st.children)
    common_childs = node_1st.children.intersection(node_2nd.children)

    print("new childs in 1st node: {}".format(GetNodeNames(new_in_1st)))
    print("removed childs in 1st node: {}".format(GetNodeNames(removed_in_1st)))
    print("common childs: {}".format(GetNodeNames(common_childs)))

    result = Node(node_1st.name, node_1st.timestamp, node_1st.type)

    # add info about changed entities
    for new_child in new_in_1st:
        child = copy.deepcopy(new_child)
        child.label_new = True
        result.children.add(child)

    for removed_child in removed_in_1st:
        child = copy.deepcopy(removed_child)
        child.label_removed = True
        result.children.add(child)

    # TODO: modified

    # add common entities
    list_repr_of_1st_node_children = list(node_1st.children)
    list_repr_of_2nd_node_children = list(node_2nd.children)
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

def TestDifference() -> None:
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

    serializer = serialization.NodeSerializer(dump_file_name)
    tree.Traverse(serializer)
    serializer.Dump()

    deserializer = serialization.NodeDeserializer(dump_file_name)
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

    gdc = google_drive_client.GoogleDriveClient("../cfg/token.json", "../cfg/credentials.json")
    gdc.RefreshMetadataTree()
    exit(0)


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
