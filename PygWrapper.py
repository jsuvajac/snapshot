from pygments import highlight, format, lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_all_styles
from pygments.formatters import HtmlFormatter, Terminal256Formatter

from utils import (
    writeStringToFile,
    parseStats,
    statsToHtmlString,
    statsToMdString,
    findTagsInFile,
    tagsToMdString
)

import re
import os

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


def tokenTest(lexer, code):
    ''' token test '''
    for index, token, vlue in lexer.get_tokens_unprocessed(code):
        print(index, token, vlue)


def srcToHtml(validFilePaths, dir, outPath, style='monokai'):
    ''' generate an html file with all of the source code,
        stats for each file and dynamic syntax highlighting'''
    allFilesBuf = ""
    fileStats = {}

    for filePath in validFilePaths:
        title = filePath.replace(dir, os.path.basename(dir))
        fileName = os.path.basename(filePath)
        lexer = get_lexer_for_filename(filePath)
        code = open(filePath).read()
        allFilesBuf += f"<h2>{title}</h2>\n"
        fileStats[fileName] = parseStats(fileName, code)
        allFilesBuf += statsToHtmlString(fileStats, key=fileName)

        # tokenTest(lexer, code)
        allFilesBuf += highlight(code, lexer, HtmlFormatter())
        # print(highlight(code, lexer, Terminal256Formatter(style=style)))

    allStyleOptions = "\n".join(
        [f'<option value="style/{style}.css">{style}</option>' for style in list(get_all_styles())])

    htmlString = HTML_TEMPLATE.format(
        cssfile=f"style/{style}.css",
        body=allFilesBuf,
        title=os.path.basename(dir),
        options=allStyleOptions)

    headEndIndex = htmlString.find('</head>')
    htmlString = htmlString[:headEndIndex] + \
        f'{SCRIPT}</head>' + htmlString[headEndIndex+len('</head>'):]

    writeStringToFile("source", htmlString, 'html', dir=outPath)
    writeStringToFile('stats', statsToMdString(
        fileStats), 'md', dir=f"{outPath}/meta")


def writeAllStylesToCss(path):
    ''' write all default styles into 'path'/style/* as css files '''

    allStyles = list(get_all_styles())

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

        if not os.path.exists(f'{path}/style/{style}.css'):
            writeStringToFile(style, cssStr, "css", dir=f"{path}/style")


def parseTODO(validFilePaths, path):
    ''' parse out "TODO" from all LEGAL_FILES in 'validFilePaths' and write output
        to 'path'/meta/todo.md
    '''
    todos = {}

    for file in validFilePaths:
        lexer = get_lexer_for_filename(file)
        code = open(file).read()

        # tags
        todo_tags = findTagsInFile(code, 'TODO')
        if todo_tags:
            todos[os.path.basename(file)] = todo_tags

    writeStringToFile('todos', tagsToMdString(
        todos), 'md', dir=f'{path}/meta')
