import os


def __isFileEndingMatch(file_name, ending):
    ''' returns true if file_name ends with ending '''
    for i in range(1, len(ending)+1):
        if file_name[-i] != ending[-i]:
            return False
    return True


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


def writeStringToFile(file, buf, fileEnding, dir):
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
