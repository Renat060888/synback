
import json

from node import Node

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