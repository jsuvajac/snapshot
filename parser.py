from PygWrapper import srcToHtml, writeAllStylesToCss, parseTODO
from TSWrapper import TSWrapper
from utils import getAllValidFiles

import os

STYLE = 'monokai'
ROOT_DIR = os.path.abspath('.')
OUT_DIR = os.path.abspath('out/')
LEGAL_FILES = ['.py', '.rs', '.c', '.cpp', '.h', '.cs']


if __name__ == '__main__':
    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)

    # writeAllStylesToCss(OUT_DIR)
    # srcToHtml(validFilePaths, ROOT_DIR, OUT_DIR)
    # todos = parseTODO(validFilePaths, OUT_DIR)

    # funcs = {}
    # for path in validFilePaths:
    #     temp = TSWrapper(open(path).read())
    #     funcs[path] = temp.getFunctions()
