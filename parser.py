from pygments import highlight, format, lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_all_styles
from pygments.formatters import HtmlFormatter, Terminal256Formatter
from TSWrapper import TSWrapper

import os
import re

STYLE = 'monokai'
ROOT_DIR = os.path.abspath('.')
OUT_DIR = os.path.abspath('out/')
LEGAL_FILES = ['.py', '.rs', '.c', '.cpp', '.h', '.cs']
SCRIPT = '''\
  <script>
    function updateCss() {
      let newVal = document.getElementById('styleId').value;
      let link = document.getElementsByTagName('link')[0];
      console.log(link);
      console.log(newVal);
      link.href = newVal;
    }
  </script>
'''
HTML_TEMPLATE = '''\
<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <link rel="stylesheet" href="{cssfile}" type="text/css">
</head>
<body>
<label for="styles">Choose syntax color style:</label>
<select name="styles" id="styleId" onchange="updateCss()">
  {options}
</select>
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
        "emptyLineCount": emptyLineCount,
        "totalLineCount": lineNum + 1,
    }


def statsToMdString(statsDict):
    ''' returns a string of a markdown representation for statsDict '''
    buf = ''
    for key in statsDict:
        buf += f'#  {key}\n'
        buf += f'* total line count: {statsDict[key]["totalLineCount"]}\n'
        buf += f'* empty line count: {statsDict[key]["emptyLineCount"]}\n'
        buf += f'* code  line count: {statsDict[key]["totalLineCount"] - statsDict[key]["emptyLineCount"]}\n'
        buf += '\n'
    return buf


def statsToHtmlString(statsDict, key=None):
    ''' returns a string of a html representation for statsDict '''
    buf = ''
    if key:
        statsDict = {key: statsDict[key]}

    for key in statsDict:
        buf += "<div>"
        buf += f'<h5>Total: {statsDict[key]["totalLineCount"]}</h5>\n'
        buf += f'<h5>Empty: {statsDict[key]["emptyLineCount"]}</h5>\n'
        buf += f'<h5>Loc: {statsDict[key]["totalLineCount"] - statsDict[key]["emptyLineCount"]}</h5>\n'
        buf += "</div>"
    return buf


def tokenTest(lexer, code):
    ''' token test '''
    for index, token, vlue in lexer.get_tokens_unprocessed(code):
        print(index, token, vlue)


def srcToHtml():
    ''' generate an html file with all of the source code, stats for each file and dynamic syntax highlighting'''
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
        allFilesBuf += statsToHtmlString(fileStats, key=fileName)

        # tokenTest(lexer, code)
        allFilesBuf += highlight(code, lexer, HtmlFormatter())
        # print(highlight(code, lexer, Terminal256Formatter(style=STYLE)))

    allStyleOptions = "\n".join(
        [f'<option value="style/{style}.css">{style}</option>' for style in list(get_all_styles())])

    htmlString = HTML_TEMPLATE.format(
        cssfile=f"style/{STYLE}.css", body=allFilesBuf, title=os.path.basename(ROOT_DIR), options=allStyleOptions)

    headEndIndex = htmlString.find('</head>')
    htmlString = htmlString[:headEndIndex] + \
        f'{SCRIPT}</head>' + htmlString[headEndIndex+len('</head>'):]

    writeStringToFile("source", htmlString, 'html')
    writeStringToFile('stats', statsToMdString(
        fileStats), 'md', dir=f"{OUT_DIR}/meta")


def writeAllStylesToCss(name=None):
    ''' write all default styles into out/style/* as css files '''
    if name is None:
        allStyles = list(get_all_styles())
    else:
        allStyles = [name]
    for style in allStyles:
        cssStr = HtmlFormatter(style=style).get_style_defs(".highlight")

        # find the code block background color and inject black as text color if it does not exist
        pattern = re.compile(r'\.highlight  \{.*\}')
        match = pattern.search(cssStr)

        if 'color' not in match[0]:
            toReplace = match[0].replace(' }', ' color: #000000 }')
        else:
            toReplace = match[0]

        cssStr = cssStr[:match.start()] + \
            CSS_GLOBAL + \
            toReplace + \
            cssStr[match.end():]

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
        todos), 'md', dir=f'{OUT_DIR}/meta')


if __name__ == '__main__':
    from pprint import pprint

    # writeAllStylesToCss()
    # srcToHtml()
    # parseTODO()

    validFilePaths = getAllValidFiles(LEGAL_FILES, ROOT_DIR)
    tsWrapper = TSWrapper()
    funcs = []
    tsWrapper.parseCode(open(validFilePaths[0]).read())
    funcs.append(tsWrapper.getFunctions())
    tsWrapper.parseCode(open(validFilePaths[1]).read())
    funcs.append(tsWrapper.getFunctions())
    pprint(funcs)
