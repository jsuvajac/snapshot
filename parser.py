from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter, Terminal256Formatter

import os

STYLE = 'native'
ROOT_DIR = os.path.abspath('../POLYGUN')
OUT_DIR = os.path.abspath('out/')
LEGAL_FILES = ['.py', '.rs', '.c', '.cpp', '.h', '.cs']


def __isFileEndingMatch(file_name, ending):
    for i in range(1, len(ending)+1):
        if file_name[-i] != ending[-i]:
            return False
    return True


def writeStringToFile(file, buf, fileEnding):
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    print(OUT_DIR+'/'+os.path.basename(file)+'.'+fileEnding)
    with open(OUT_DIR+'/'+os.path.basename(file)+'.'+fileEnding, 'w') as f:
        f.write(buf)


def findTagsInFile(text, tag):
    lines = []
    for num, line in enumerate(text.split('\n')):
        if not line:
            continue
        elif tag in line:
            line = line.lstrip()
            line = line[line.find(tag):]
            lines.append(f'{str(num)} -> {line.lstrip()}')
    return lines


def tagsToMdString(tagDict):
    buf = ''
    for key in tagDict:
        buf += f'# {key}\n'
        buf += '\n```\n'
        for line in tagDict[key]:
            buf += line + '\n'
        buf += '```\n'
    return buf


def getAllValidFiles(whiteList, rootDir):
    filePaths = []
    for root, dirs, files in os.walk(rootDir):
        for f in files:
            for ending in whiteList:
                if __isFileEndingMatch(f, ending):
                    filePaths.append(root+'/'+f)
    return filePaths


def parseTODO():
    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)
    todos = {}

    for file in validFilePaths:
        lexer = get_lexer_for_filename(file)
        code = open(file).read()

        # tags
        todo_tags = findTagsInFile(code, 'TODO')
        if todo_tags:
            todos[os.path.basename(file)] = todo_tags

    writeStringToFile('TODO', tagsToMdString(todos), 'md')


def parseStats(fileName, text):
    emptyLineCount = 0
    for lineNum, line in enumerate(text.split('\n')):
        if len(line) == 0:
            emptyLineCount += 1
    return {
        "fileName": fileName,
        "emptyLineCount": emptyLineCount,
        "totalLineCount": lineNum + 1,
    }

def statsToMdString(fileStats):
    buf = ''
    for key in fileStats:
        buf += f'#  {key}\n'
        buf += f'* line count: {fileStats[key]["totalLineCount"]}\n'
        buf += '\n'
    return buf

def srcToHtml():
    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)
    allFilesBuf = ""
    fileStats = {}
    for file in validFilePaths:
        lexer = get_lexer_for_filename(file)
        code = open(file).read()
        allFilesBuf += highlight(code, lexer,
                                 HtmlFormatter(style=STYLE, noclasses=True))
        fileStats[os.path.basename(file)] = parseStats(os.path.basename(file), code)

        # print(HtmlFormatter().get_style_defs(STYLE))
        print(highlight(code, lexer, Terminal256Formatter(style=STYLE)))

    writeStringToFile("source", allFilesBuf, 'html')
    writeStringToFile('stats', statsToMdString(fileStats), 'md')

if __name__ == '__main__':
    parseTODO()
    srcToHtml()
