from tree_sitter import Language, Parser
from pprint import pprint

import os

PY_LANGUAGE = Language('build/my-languages.so', 'python')


def __formatTreeStr(tree):
    ''' temp stringifyer for parse tree '''
    paren = []
    out = ""
    for char in tree:
        if char == '(':
            if len(paren) < 1:
                pass
            elif paren[-1] == char:
                out += '\n' + '  '*len(paren)
            paren.append('(')
        elif char == ')':
            paren.pop(-1)
        out += char
    return "".join(out)


class TSWrapper:
    def __init__(self, code=None):
        if not os.path.exists('build/my-languages.so'):
            Language.build_library(
                'build/my-languages.so',
                [
                    'vendor/tree-sitter-python'
                ]
            )
        self.ts = Parser()
        self.ts.set_language(PY_LANGUAGE)
        self.tree = None

        if code:
            self.parseCode(code)

    def __repr__(self):
        if self.tree:
            return __formatTreeStr(self.tree.root_node.sexp())
        else:
            return "<empty tree>"

    def parseCode(self, code):
        self.code = code.splitlines()
        self.codeBytes = bytes(code, "utf8")
        self.tree = self.ts.parse(self.codeBytes)

    def getFunctions(self):
        ''' traverse source tree and return a dict of function/metnod declerations '''
        cursor = self.tree.root_node.walk()
        cursor.goto_first_child()
        allFuncs = {}
        globalFuncs = []
        while True:
            if (cursor.node.type == "function_definition"):
                # print(cursor.node)
                globalFuncs.append(self.__parseFuncs(cursor.node))

            if (cursor.node.type == "class_definition"):
                # print(f"----> class")
                className = ''
                classCursor = None
                for child in cursor.node.children:
                    if child.type == "identifier":
                        className = self.__stringFromNodeBytes(child)
                    if child.type == "block":
                        # print(f'block: {child}')
                        classCursor = child.walk()
                classCursor.goto_first_child()
                methods = []
                while True:
                    if (classCursor.node.type == "function_definition"):
                        methods.append(self.__parseFuncs(classCursor.node))
                    if not classCursor.goto_next_sibling():
                        break

                allFuncs[className] = methods

            if not cursor.goto_next_sibling():
                break
        allFuncs['globalScope'] = globalFuncs
        return allFuncs

    def __parseFuncs(self, root_node):
        ''' return dict of all functions in root_node '''
        func = {}
        for child in root_node.children:
            # print(child)
            if (child.type == "identifier"):
                func['name'] = self.__stringFromNodeBytes(child)
            elif (child.type == "parameters"):
                func['parameters'] = self.__stringFromNodeBytes(child)
        return func

    def __stringFromNodeBytes(self, node):
        ''' return string from source from the nodes start to end '''
        return self.codeBytes[node.start_byte:node.end_byte].decode()
