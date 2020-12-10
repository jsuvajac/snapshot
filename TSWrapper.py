from tree_sitter import Language, Parser
from pprint import pprint

import os

'''
tree_sitter api: https://github.com/tree-sitter/py-tree-sitter/blob/master/tree_sitter/binding.c
'''

LANG_LIST = ['python', 'c', 'cpp', 'c_sharp', 'rust', 'javascript']

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

def getLang(path):
    ''' return appropriate language for a file given path '''
    ending = path.split('.')[-1]
    if ending in ['cpp', 'h', 'cc', 'hh', 'hpp']:
        return Language('build/my-languages.so', 'cpp')
    elif ending in ['c']:
        return Language('build/my-languages.so', 'c')
    elif ending in ['py']:
        return Language('build/my-languages.so', 'python')
    elif ending in ['cs']:
        return Language('build/my-languages.so', 'c_sharp')
    elif ending in ['rs']:
        return Language('build/my-languages.so', 'rust')
    elif ending in ['js']:
        return Language('build/my-languages.so', 'javascript')
    else:
        raise Exception


class TSWrapper:
    def __init__(self):
        if not os.path.exists('build/my-languages.so'):
            Language.build_library(
                'build/my-languages.so',
                [
                    'vendor/tree-sitter-c',
                    'vendor/tree-sitter-cpp',
                    'vendor/tree-sitter-c-sharp',
                    'vendor/tree-sitter-rust',
                    'vendor/tree-sitter-javascript',
                    'vendor/tree-sitter-python'
                ]
            )

        self.ts = Parser()
        self.tree = None

    def __repr__(self):
        if self.tree:
            return __formatTreeStr(self.tree.root_node.sexp())
        else:
            return "<empty tree>"

    def parseCode(self, path):
        self.ts.set_language(getLang(path))
        code = open(path).read()
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
            # print(cursor.node)
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
            # print(f"\t{child}")
            if (child.type == "identifier"):
                func['name'] = self.__stringFromNodeBytes(child)
            elif (child.type == "parameters"):
                func['parameters'] = self.__stringFromNodeBytes(child)
        return func

    def __stringFromNodeBytes(self, node):
        ''' return string from source from the nodes start to end '''
        return self.codeBytes[node.start_byte:node.end_byte].decode()
