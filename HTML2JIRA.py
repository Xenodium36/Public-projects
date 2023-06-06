import re
from vm.tools.boa import toboa
"""
    Description
        ----------
        Used to get next list tag while parsing HTML/JIRA lists
    Parameters
    ----------
    code : string
        Table code
    startIndex : int
        Starting index of searching in string *data*
    isNested : Bool
        If table is nested
"""


class TableStruct:
    def __init__(self, code, startIndex, nesting, parsedCode=""):
        self.code = code
        self.startIndex = startIndex
        self.nesting = nesting
        self.parsedCode = parsedCode


class Tables:
    def __init__(self):
        self.tables = []

    def push(self, table):
        self.tables.append(table)

    def popFirst(self):
        if len(self.tables) != 0:
            return self.tables.pop(0)

    def popLast(self):
        if len(self.tables) != 0:
            return self.tables.pop(len(self.tables)-1)

    def isEmpty(self):
        return len(self.tables)

    def getLastNesting(self):
        if len(self.tables) != 0:
            return self.tables[len(self.tables) - 1].nesting
        else:
            return -1


"""
    Description
    ----------
    Used to get next list tag while parsing HTML/JIRA lists

    Parameters
    ----------
    data : string
        Whole data string
    index : int
        Starting index of searching in string *data*
"""


def getListToken(data, index):
    return re.search(r"(<ol.*?>|</ol>|<ul.*?>|</ul>|<li.*?>|</li>)", data[index:])


"""
    Description
    ----------
    Used to get parse tokens from getToken
    Manual calculations of index are needed
    Couldnt find better way to do it

    Parameters
    ----------
    data : string
        Whole data string
    token : string
        Actual token
    strList : string
        List of * and #
    index : int
        Starting index of searching in string *data*
"""


def parseListToken(data, token, strList, index):
    if token.group(0).find("<ul") != -1:
        # If its start of the list (strList is empty), add panel...
        if strList == "":
            data = data.replace(token.group(0), "{panel:borderStyle=none}", 1)
            # len({panel:...}-len(<ul>))
            index += 20
        else:
            index = index - (token.end() - token.start())
            data = data.replace(token.group(0), "", 1)
        strList += "*"
    elif token.group(0).find("</ul") != -1:
        strList = strList[:-1]
        # If its end of the list (strList is empty), add panel...
        if strList == "":
            data = data.replace(token.group(0), "{panel}", 1)
            # len({panel}-len(</ul>))
            index += 3
        else:
            index = index - (token.end() - token.start())
            data = data.replace(token.group(0), "", 1)
    elif token.group(0).find("<ol") != -1:
        if strList == "":
            # If its start of the list (strList is empty), add panel...
            data = data.replace(token.group(0), "{panel:borderStyle=none}", 1)
            # len({panel:...}-len(<ol>))
            index += 20
        else:
            index = index - (token.end() - token.start())
            data = data.replace(token.group(0), "", 1)
        strList += "#"
    elif token.group(0).find("</ol") != -1:
        strList = strList[:-1]
        # If its end of the list (strList is empty), add panel...
        if strList == "":
            data = data.replace(token.group(0), "{panel}", 1)
            # len({panel}-len(</ul>))
            index += 3
        else:
            index = index - (token.end() - token.start())
            data = data.replace(token.group(0), "", 1)
    elif token.group(0).find("<li") != -1:
        index = index - (token.end() - token.start()) + len(strList)
        data = data.replace(token.group(0), strList + " ", 1)
    elif token.group(0).find("</li") != -1:
        index = index - (token.end() - token.start()) + 1
        data = data.replace(token.group(0), "\n", 1)
    return data, strList, index


"""
    Description
    ----------
    Starting function of parsing HTML/JIRA lists
    Iterates through all of lists in file

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseLists(data):
    backup = data
    try:
        # Get first token
        index = 0
        token = getListToken(data, index)
        if not token:
            return data
        index = token.start()
        # Parse list
        while token:
            data, index = parseList(data, index)
            token = getListToken(data, index)
        return data
    except:
        return backup


"""
    Description
    ----------
    Used to sort lists of strings by len
    ['\n', '\n\n', '\n', '\n\n\n'] -> ['\n\n\n', '\n\n', '\n']
    Parameters
    ----------
    arr : list
        List of strings to sort
"""


def sortList(arr):
    arr = list(dict.fromkeys(arr))
    arr.sort(key=len)
    arr.reverse()
    return arr


"""
    Description
    ----------
    Used to parse specific HTML/JIRA list

    Parameters
    ----------
    data : string
        Whole data string
    index : int
        Starting index of searching in string *data*

"""


def parseList(data, index):
    token = getListToken(data, index)
    start = index + token.start()
    strList = ""
    # Iterate, while there is a symbol in strList
    while True:
        index += token.end()
        data, strList, index = parseListToken(data, token, strList, index)
        if len(strList) == 0:
            break
        token = getListToken(data, index)
    # Replace all \t and multiple \n
    string = data[start:index]
    length = len(data[start:index])
    string = string.replace("\t", "")
    newLines = re.findall(r"(\n{2,})", string)
    if newLines:
        newLines = sortList(newLines)
        for nl in newLines:
            string = string.replace(nl, "\n")
    data = data.replace(data[start:index], string)
    index = index - (length - len(string))
    return data, index


"""
    Description
    ----------
    Used to parse head of tables

    Parameters
    ----------
    head : string
        Head of table
"""


def parseTableHead(head):
    head = head[0]
    head = head.replace("\n", "")
    head = head.replace("\t", "")
    head = head.replace("</tr>", "")
    start = re.findall(r"(<tr.*?>)", head)
    head = head.replace(start[0], "\n")
    head = head.replace("<br>", " \\\\ ")
    head = head.replace("<br />", " \\\\ ")
    # Find all columns
    # [(starting_line_tag)(body)(end_line_tag)]
    hColums = re.findall(r"(<th.*?>)(.*?)(</th>)", head)
    for i, c in enumerate(hColums):
        head = head.replace(c[0], "||")
        head = head.replace(c[2], "")
        if i == len(hColums) - 1:
            head = head.replace(c[1], c[1] + "||")

    # replace |||| |||||| ... lazy fix, Bug ocured, when: b1 b1 b1 -> ||b1||||||b1||||||b1||||||
    fix = re.findall(r"\|{3,}", head)
    if fix:
        fix = sortList(fix)
        for f in fix:
            head = head.replace(f, "||")
    return head


"""
    Description
    ----------
    Used to parse body of tables

    Parameters
    ----------
    body : string
        Body of table
"""


def parseTableBody(body):
    body = body.replace("\t", "")
    # if there is panel or codeblock, i want to keep it, as it is, otherwise delete \n
    panels = re.findall(r"({panel:borderStyle=none}[\w\W]*?{panel})", body)
    codeBlocks = re.findall(r"({code:None}[\w\W]*?{code})", body)
    body = body.replace("\n", "")
    for p in panels:
        body = body.replace(p.replace("\n", ""), p)
    for cb in codeBlocks:
        body = body.replace(cb.replace("\n", ""), cb)
    body = body.replace("<br>", " \\\\ ")
    body = body.replace("<br />", " \\\\ ")
    # Find all rows in table body
    # [(row)]
    bRows = re.findall(r"(<tr.*?>)([\w\W]*?)</tr>", body)
    for br in bRows:
        # Find all columns in table body to add |
        # [(column)]
        bColums = re.findall(r"(<td.*?>)([\w\W]*?)</td>", br[1])
        body = body.replace(br[0], "\n")
        for bc in bColums:
            body = body.replace(bc[0], "|")
        body = body.replace("|" + bColums[-1][1] + "</td>", "|" + bColums[-1][1] + "|")
    body = body.replace("</tr>", "")
    # body = body.replace("<tr>", "\n")
    body = body.replace("</td>", "")
    fix = re.findall(r"\|{2,}", body)
    if fix:
        fix = sortList(fix)
        for f in fix:
            body = body.replace(f, "|")
    return body


"""
    Description
    ----------
    Used to get next table tag while parsing HTML/JIRA tables

    Parameters
    ----------
    data : string
        Whole data string
    index : int
        Starting index of searching in string *data*
"""


def getTableToken(data, index):
    return re.search(r"(<table.*?>|</table>)", data[index:])


"""
    Description
    ----------
    Find all tables and save them to array

    Parameters
    ----------
    data : string
        Whole data string
    index : int
        Starting index of searching in string *data*
"""


def findTables(data):
    tables = Tables()
    tmpTables = Tables()
    index = 0
    nesting = 0
    token = getTableToken(data, index)
    if not token:
        return tables.tables
    nesting += 1
    startIndex = token.start()
    index = token.end()
    tmpTables.push(TableStruct("", startIndex, 0))
    test = 0
    while True:
        test += 1
        if test > 500:
            break
        token = getTableToken(data, index)
        if not token:
            break
        index += token.end()
        if token.group(0) == "</table>":
            nesting -= 1
            t = tmpTables.popLast()
            t.code = data[t.startIndex:index]
            tables.push(t)
        else:
            startIndex = index - len(token.group(0))
            tmpTables.push(TableStruct("", startIndex, nesting))
            nesting += 1
    return tables


def parseTable(code, panel=False):
    code = code.replace(u"\u00A0", " ")
    code = code.replace("&nbsp;", " ")

    # Try to find head of table to further work with it
    # [(body_of_head)]
    head = (re.findall(r"<thead>([\w\W]*?)</thead>", code))
    if head:
        head = parseTableHead(head)
        hBool = True
    else:
        hBool = False
    # Find the table body to further work with it
    # [(table_body)]
    body = (re.findall(r"<tbody>([\w\W]*?)</tbody>", code))
    if body:
        body = body[0]
    else:
        body = (re.findall(r"<table.*?>([\w\W]*?)</table>", code))[0]
    body = parseTableBody(body)
    # If there was header
    if panel:
        if hBool:
            parsedTable = " {panel:borderStyle=none}" + head + body + "{panel} "
        else:
            parsedTable = " {panel:borderStyle=none}" + body + "{panel} "
    else:
        if hBool:
            parsedTable = head + body
        else:
            parsedTable = body

    return parsedTable


"""
    Description
    ----------
    Used to parse tables
    Table can contain head, and must contain body

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseTables(data):
    backup = data
    try:
        # Find all tables
        # [(starting_table_tag)(body)(end_table_tag)]

        tables = findTables(data)
        stack = Tables()
        index = 0

        # tables = re.findall(r"(<table.*?>)([\w\W]*?)(</table>)", data)
        while tables.isEmpty():
            t = tables.popFirst()
            if t.nesting > index or t.nesting == index:
                index = t.nesting
                if t.nesting == 0:
                    t.parsedCode = parseTable(t.code)
                    data = data.replace(t.code, t.parsedCode)
                else:
                    t.parsedCode = parseTable(t.code, True)
                    stack.push(t)
            if index > t.nesting:
                parsedCode = t.code
                while stack.getLastNesting() > t.nesting:
                    tmpTable = stack.popLast()
                    parsedCode = parsedCode.replace(tmpTable.code, tmpTable.parsedCode)
                t.parsedCode = parsedCode
                index = t.nesting
                if t.nesting == 0:
                    t.parsedCode = parseTable(t.parsedCode)
                    data = data.replace(t.code, t.parsedCode)
                else:
                    t.parsedCode = parseTable(t.code, True)
                    stack.push(t)

        return data
    except:
        return backup


"""
    Description
    ----------
    Used to parse hyperlinks

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseLinks(data):
    backup = data
    try:
        # find all links
        # [(Link)]
        links = re.findall(r"(<a.*?>.*?</a>)", data)
        for l in links:
            # Find link and text
            # [(link)(text_to_replace_link)]
            link = (re.findall(r"<a.*?(?<=href=\")(.*?)(?=\").*?>(.*?)</a>", l))[0]
            data = data.replace(l, "[" + link[1] + "|" + link[0] + "]")
        return data
    except:
        return backup


"""
    Description
    ----------
    Used to parse code block

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseCodeBlocks(data):
    backup = data
    try:
        # Find all code blocks
        # [(starting_tag)(body)(end_tag)]
        codeBlocks = re.findall(r"(<div.*?>)([\w\W]*?)(</div>)", data)
        for cb in codeBlocks:
            code = cb[1].replace("<br>", "\n")
            code = code.replace("<br />", "\n")
            data = data.replace(cb[0] + cb[1] + cb[2], "{code:None}" + code + "{code}")
        return data
    except:
        return backup


"""
    Description
    ----------
    Used to delete other unparsed tags

    Parameters
    ----------
    data : string
        Whole data string
"""


def deleteUnsupportedTags(data):
    backup = data
    try:
        # Find any unparsed tag
        # [(tag)]
        otherTags = re.findall(r"(<.*?>)", data)
        for ot in otherTags:
            data = data.replace(ot, "")
        return data
    except:
        return backup


def getImageNameForEmbededPicture(botName, boId, attachmentName):
    botype = VM.getBOType(botName)
    result = botype.find(transaction, "ticketdescId == %s" % (boId))
    ticketdesc = toboa(result.getBObject())
    fileName = ""
    if ticketdesc:
        ticketNo = ticketdesc.ticket__ticketno
        descNo = ticketdesc.descno
        fileName = "%s_%s%s" % (ticketNo, descNo, attachmentName)
    return fileName


"""
    Description
    ----------
    Used to parse images

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseImages(data):
    backup = data
    try:
        # Find all images
        # [(whole_tag)]
        images = re.findall(r"(<IMG.*?>)", data)
        images += re.findall(r"(<img.*?>)", data)
        for image in images:
            # get link to image
            # (src)
            src = re.search(r"(?<=src=\")(.*?)(?=\")", image)
            if src:
                src = src.group(0)
                if re.search(r"moniker", src):
                    moniker = re.findall(r"moniker=M_(.*?)-(\d*?)%.*?path=(.*)", src)[0]
                    src = getImageNameForEmbededPicture(moniker[0], moniker[1], moniker[2])
                data = data.replace(image, " !" + src + "! ")
        return data
    except:
        return backup


"""
    Description
    ----------
    Used to parse colors

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseColors(data):
    backup = data
    try:
        # Find all style=color
        # [(whole_color)]
        colors = re.findall(r"(<span style=\"color:.*?\">)([\w\W]*?)(</span>)", data)
        for x in colors:
            # Get value of color
            # (color_value)
            colorHEX = re.search(r"color:#[a-z\d]{6}", x[0])
            colorRGB = re.search(r"color: rgb\((\d{1,3}).*?(\d{1,3}).*?(\d{1,3})\)", x[0])
            if colorHEX:
                colorHEX = colorHEX.group(0)
                data = data.replace(x[0] + x[1] + x[2], "{" + colorHEX + "}" + x[1] + "{color}")
            elif colorRGB:
                colorRGB = ("#%02x%02x%02x" % (int(colorRGB.group(1)), int(colorRGB.group(2)), int(colorRGB.group(3))))
                data = data.replace(x[0] + x[1] + x[2], "{color:" + colorRGB + "}" + x[1] + "{color}")
        return data
    except:
        return backup


"""
    Description
    ----------
    Used to parse simple tags

    Parameters
    ----------
    data : string
        Whole data string
"""


def parseSimpleTags(data):
    backup = data
    try:
        # Paragraph
        # data = data.replace("<p>", "")
        # data = data.replace("</p>", "\n")

        # Bold
        data = data.replace("<strong>", "*")
        strong = re.findall(r"(<strong.*?>)", data)
        for s in strong:
            data = data.replace(s, "*")
        data = data.replace("</strong>", "*")

        # Underline
        data = data.replace("<u>", "+")
        data = data.replace("</u>", "+")

        # Italic
        data = data.replace("<em>", "_")
        data = data.replace("</em>", "_")

        # Strikethrough
        data = data.replace("<s>", "-")
        data = data.replace("</s>", "-")

        # New line
        data = data.replace("<br />", "\n")
        data = data.replace("<br>", "\n")

        # Headers
        headings = re.findall(r"(<(h\d)>([\w\W]*?)</h\d>)", data)
        for h in headings:
            tmp = h[2].replace("\n", "")
            data = data.replace(h[0], h[1] + ". " + tmp)
        return data
    except:
        return backup


"""
    Description
    ----------
    Convert HTML codes to characters

    Parameters
    ----------
    data : string
        Whole data string
"""


def convertHTMLChars(data):
    backup = data
    try:
        # New backspace
        data = data.replace(u"\u00A0", "")

        # HTML characters
        data = data.replace("&nbsp;", " ")
        data = data.replace("&amp;", "&")
        data = data.replace("&gt;", ">")
        data = data.replace("&lt;", "<")
        return data
    except:
        return backup


def fixImageHyperLinks(data):
    backup = data
    try:
        ihl = re.findall(r"(\[.*?(\!.*?\!).*?(\|.*?\]))", data)
        for h in ihl:
            data = data.replace(h[0], "[" + h[1] + h[2])
        return data
    except:
        return backup


"""
    Description
    ----------
    Main function

    Parameters
    ----------
    data : string
        Body of issue/comment
    wholeTickeet : string
        String containing short description and description of comment/issue
"""


def parse(data, wholeTicket=""):
    if data == "":
        if wholeTicket != "":
            return wholeTicket
        else:
            return data
    backup = data
    if re.search(r"<head.*?>", data):
        data = re.sub(r"<head>[\w\W]*?</head>", "", data)
    data = data.replace("|", "/")
    data = parseLists(data)
    # data = parseCodeBlocks(data)
    data = parseTables(data)
    data = parseLinks(data)
    data = parseSimpleTags(data)
    data = parseColors(data)
    data = parseImages(data)
    data = fixImageHyperLinks(data)
    data = deleteUnsupportedTags(data)
    data = convertHTMLChars(data)

    if wholeTicket:
        if data[0] != "\n":
            data = "\n" + data
        return wholeTicket.replace(backup, data)
    else:
        return data
