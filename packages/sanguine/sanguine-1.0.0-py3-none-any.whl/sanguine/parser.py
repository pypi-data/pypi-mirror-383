from tree_sitter_language_pack import get_parser

import sanguine.constants as c
from sanguine.utils import prog_lang_schema


def extract_symbols(code: str, lang: str) -> dict:
    nodes = prog_lang_schema.get(lang.lower())
    if not nodes:
        raise ValueError(f"Language '{lang}' not supported")

    parser = get_parser(lang)
    tree = parser.parse(code.encode("utf8"))
    root = tree.root_node

    result = {c.FLD_FUNCTIONS: [], c.FLD_CLASSES: []}

    def extract_function(node):
        data = {
            c.FLD_NAME: None,
            c.FLD_PARAMETERS: None,
            c.FLD_DOCSTRING: None,
            c.FLD_BODY: None,
            c.FLD_RETURN: None,
        }
        for child in node.children:
            if child.type == nodes["identifier"]:
                data[c.FLD_NAME] = code[child.start_byte : child.end_byte]
            elif child.type == nodes["parameters"]:
                data[c.FLD_PARAMETERS] = code[
                    child.start_byte : child.end_byte
                ]
            elif child.type == nodes["body"]:
                body_bytes = code[child.start_byte : child.end_byte]
                docstring = None
                if child.children:
                    first_stmt = child.children[0]
                    if first_stmt.type in nodes["docstring_expr"]:
                        if first_stmt.children:
                            docstring_node = first_stmt.children[0]
                            if docstring_node.type == "string":
                                docstring = code[
                                    docstring_node.start_byte : docstring_node.end_byte
                                ]
                data[c.FLD_DOCSTRING] = docstring
                data[c.FLD_BODY] = body_bytes
            elif child.type == "type":
                data[c.FLD_RETURN] = code[child.start_byte : child.end_byte]
        return data

    def traverse(node, class_context=None):
        if node.type == nodes["function"]:
            func_data = extract_function(node)
            if class_context:
                class_context[c.FLD_METHODS].append(func_data)
            else:
                result[c.FLD_FUNCTIONS].append(func_data)

        elif node.type == nodes["class"]:
            cls_data = {
                c.FLD_NAME: None,
                c.FLD_SUPERCLASSES: None,
                c.FLD_ATTRIBUTES: [],
                c.FLD_METHODS: [],
            }
            for child in node.children:
                if child.type == nodes["identifier"]:
                    cls_data[c.FLD_NAME] = code[
                        child.start_byte : child.end_byte
                    ]
                elif child.type == "body":
                    attributes = []
                    for stmt in child.children:
                        if stmt.type == nodes["assignment"] and stmt.children:
                            left = stmt.children[0]
                            if left.type == nodes["attribute"]:
                                attr_name = code[
                                    left.start_byte : left.end_byte
                                ]
                                attributes.append(attr_name)
                    cls_data[c.FLD_ATTRIBUTES] = attributes

                    for stmt in child.children:
                        traverse(stmt, class_context=cls_data)
            result[c.FLD_CLASSES].append(cls_data)

        for child in node.children:
            traverse(child, class_context=class_context)

    traverse(root)
    return result
