from pygments import highlight, format, lex
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter, Terminal256Formatter

import os
import re

STYLE = 'monokai'
ROOT_DIR = os.path.abspath('.')
OUT_DIR = os.path.abspath('out/')
LEGAL_FILES = ['.py', '.rs', '.c', '.cpp', '.h', '.cs']

HTML_TEMPLATE = '''\
<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <link rel="stylesheet" href="{cssfile}" type="text/css">
</head>
<body>
{body}
</body>
</html>
'''
CSS_GLOBAL = '''\
body  { background: #1c1d19; color: #f8f8f2 }
'''


def __isFileEndingMatch(file_name, ending):
    ''' returns true if file_name ends with ending '''
    for i in range(1, len(ending)+1):
        if file_name[-i] != ending[-i]:
            return False
    return True


def writeStringToFile(file, buf, fileEnding, dir=OUT_DIR):
    ''' writes buf to file . fileEnding '''
    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(dir+'/'+os.path.basename(file)+'.'+fileEnding, 'w') as f:
        f.write(buf)


def findTagsInFile(text, tag):
    ''' returns list of lines that contain tag
        and strips all characters to the left of the tag
    '''
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
    ''' returns a string containing data from tagDict '''
    buf = ''
    for key in tagDict:
        buf += f'# {key}\n'
        buf += '\n```\n'
        for line in tagDict[key]:
            buf += line + '\n'
        buf += '```\n'
    return buf


def getAllValidFiles(whiteList, rootDir):
    ''' walks through rootDir recurisively and adds all paths with a file ending
        in whiteList to filePath
    '''
    filePaths = []
    for root, dirs, files in os.walk(rootDir):
        for f in files:
            for ending in whiteList:
                if __isFileEndingMatch(f, ending):
                    filePaths.append(root+'/'+f)
    return filePaths


def parseStats(fileName, text):
    ''' parse out stats (fileName, lines of code, empty lines ...)
        from fileName and return as dict
    '''
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
    ''' returns a string of a markdown representation for tagDict '''
    buf = ''
    for key in fileStats:
        buf += f'#  {key}\n'
        buf += f'* line count: {fileStats[key]["totalLineCount"]}\n'
        buf += '\n'
    return buf


def srcToHtml():
    ''' parse all legal files and write syntax highlighted code to source.html '''
    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)
    allFilesBuf = ""
    fileStats = {}
    for filePath in validFilePaths:
        title = filePath.replace(ROOT_DIR, os.path.basename(ROOT_DIR))
        fileName = os.path.basename(filePath)
        lexer = get_lexer_for_filename(filePath)
        code = open(filePath).read()
        allFilesBuf += f"<h2>{title}</h2>\n"
        fileStats[fileName] = parseStats(fileName, code)
        allFilesBuf += f'<h3>Loc: {fileStats[fileName]["totalLineCount"]}</h3>\n'
        allFilesBuf += highlight(code, lexer, HtmlFormatter())

        # print(highlight(code, lexer, Terminal256Formatter(style=STYLE)))

    writeStringToFile("source",
                      HTML_TEMPLATE.format(
                          cssfile=f"style/{STYLE}.css", body=allFilesBuf, title=os.path.basename(ROOT_DIR)),
                      'html')
    writeStringToFile('stats', statsToMdString(
        fileStats), 'md', dir=f"{OUT_DIR}/meta")


def writeAllStylesToCss(name=None):
    ''' write all default styles into out/style/* as css files '''
    from pygments.styles import get_all_styles
    if name is None:
        allStyles = list(get_all_styles())
    else:
        allStyles = [name]
    for style in allStyles:
        cssStr = HtmlFormatter(style=style).get_style_defs(".highlight")
        cssStr = CSS_GLOBAL + cssStr
        # find the code block background color and injecti it as the body color
        # pattern = re.compile(r'\.highlight  \{.*\}')
        # match = pattern.search(cssStr)

        # cssStr = cssStr[:match.start()] + \
        #     match[0].replace(".highlight", "body") + '\n' + \
        #     match[0] + \
        #     cssStr[match.end():]

        if not os.path.exists(f'{OUT_DIR}/style/{style}.css'):
            writeStringToFile(style, cssStr, "css", dir=f"{OUT_DIR}/style")


def parseTODO():
    ''' parse out "TODO" from all LEGAL_FILES in ROOT_DIR and write output
        to out/meta/todo.md
    '''
    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)
    todos = {}

    for file in validFilePaths:
        lexer = get_lexer_for_filename(file)
        code = open(file).read()

        # tags
        todo_tags = findTagsInFile(code, 'TODO')
        if todo_tags:
            todos[os.path.basename(file)] = todo_tags

    writeStringToFile('todos', tagsToMdString(
        todos), 'md', dir=f"{OUT_DIR}/meta")


if __name__ == '__main__':
    writeAllStylesToCss()
    srcToHtml()
    parseTODO()
