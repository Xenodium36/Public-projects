import re
import sys
import getopt
import xml.etree.ElementTree as ET


class ErrCodes:
    PAR_ERR = 10
    IN_FILE_ERR = 11
    OUT_FILE_ERR = 12

    XML_FORMAT_ERR = 31
    XML_STRUCT_LEX_SYNTAX_ERR = 32

    SEMANTIC_ERR = 52
    INVALID_OPERAND_TYPE = 53
    NONEXISTENT_VAR = 54
    NONEXISTENT_FRAME = 55
    MISSING_VALUE = 56
    INVALID_OPERAND_VALUE = 57
    STRING_ERR = 58

    INTERNAL_ERR = 99


class Instruction:
    def __init__(self, opcode):
        self.opcode = opcode


class Argument:
    def __init__(self, value):
        self.value = value


class Variable:
    def __init__(self, name, varType, value):
        self.name = name
        self.varType = varType
        self.value = value


class DataStackEl:
    def __init__(self, elType, value):
        self.elType = elType
        self.value = value


def closeFile():
    """Closes file for statistics, if --stats was used
    """
    global datafile
    if datafile is not None:
        datafile.close()


def printToStderr(err):
    """Function prints error message
                Parameters
                ----------
                err : str
                    Error message
    """
    print(err, file=sys.stderr)


def errExit(errcode, errmsg):
    """Function prints error message, closes opened files an ends program with Error code = errcode
                Parameters
                ----------
                errcode : ErrCodes
                    Code with error number, with which should program end
                errmsg : string
    """
    closeFile()
    printToStderr("ERROR: " + errmsg)
    sys.exit(errcode)


def printFrameStderr(frame, frames):
    """Function prints informations about specific frame before ending program
                Parameters
                ----------
                frame : string
                    Type of frame (LF or TF or GF)
                frames : list of strings
                    List of all frames
    """
    if len(frames[frame]) == 0:
        printToStderr("Frame is empty.")
    else:
        for var in frames[frame]:
            varType = frames[frame][var].varType
            value = frames[frame][var].value

            if varType is None:
                varType = "None"
                value = "None"

            printToStderr(var + "\t|\t" + varType + "\t|\t" + str(value))


def dealWithEscape(editstr):
    """Function replaces number sequences for chars (\65B\67 => abc) using regex
                Parameters
                ----------
                editstr : String
                    String, which should be converted
                Return values
                ---------
                editstr : string
                    converted string
    """
    escseqlist = re.findall(r'\\\d{3}', editstr)

    while len(escseqlist) > 0:
        escseq = escseqlist[0]
        editstr = editstr.replace(escseq, chr(int(escseq.replace("\\", ""))))

        while escseq in escseqlist:
            escseqlist.remove(escseq)

    return editstr


def varInFrame(varname, frame, frames):
    """Checks, if variable is in frame
                Parameters
                ----------
                varname : string
                    Name of variable
                frame : string
                    type of frame
                frames : list of strings

                Return values
                ---------
                : bool
                    True, if var is in frame
    """
    if varname in frames[frame]:
        return True
    else:
        return False


def frameExist(frame, frames):
    """Checks, if frame existx
                Parameters
                ----------
                frame : string
                    type of frame
                frames : list of strings
                    List of frames
                Return values
                ---------
                : bool
                    True, if frame exists
    """
    if frames[frame] is None:
        return False
    else:
        return True


def checkVarExistance(varName, frame, frames):
    """Checks, if it exists
                Parameters
                ----------
                varname : string
                    Name of variable
                frame : string
                    type of frame
                frames : list of strings
    """
    if not frameExist(frame, frames):
        errExit(ErrCodes.NONEXISTENT_FRAME, "Frame does not exist!")
    elif not varInFrame(varName, frame, frames):
        errExit(ErrCodes.NONEXISTENT_VAR, "Varialbe does not exist!")


def checkVarInit(varName, frame, frames):
    """Check, if var is initialized
    """
    if frames[frame][varName].varType is None:
        errExit(ErrCodes.MISSING_VALUE, "Variable is not initialized!")


def getArg(instr, frames, dataType, x=2):
    """Check argument and argument type of instruction
                Parameters
                ----------
                instr : instr
                    intruction
                frames : List of frames
                dataType : string
                x : int
                    which instruction should be controlled, default = 2
                Return values
                ---------
                value :
                    return value of argument
    """
    if x == 2:
        tmp = instr.arg2
    else:
        tmp = instr.arg3
    if tmp.type == "var":
        var = tmp.value.split('@')
        checkVarExistance(var[1], var[0], frames)
        checkVarInit(var[1], var[0], frames)
        if frames[var[0]][var[1]].varType != dataType:
            errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
        value = frames[var[0]][var[1]].value
    else:
        if tmp.type != dataType:
            errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

        value = tmp.value

    return value


def getArgWType(instr, frames, x=2):
    """Check argument and returns argument type and value
                Parameters
                ----------
                instr : instr
                    intruction
                frames : List of frames
                x : int
                    which instruction should be controlled, default = 2
                Return values
                ---------
                value :
                    return value of argument
                dataType :
                    return type of argument
    """
    if x == 2:
        tmp = instr.arg2
    else:
        tmp = instr.arg3
    if tmp.type == "var":
        var = tmp.value.split('@')
        checkVarExistance(var[1], var[0], frames)
        checkVarInit(var[1], var[0], frames)
        dataType = frames[var[0]][var[1]].varType
        value = frames[var[0]][var[1]].value
    else:
        dataType = tmp.type
        value = tmp.value

    return dataType, value


def getDStackEl(datastack, datatype):
    if len(datastack) == 0:
        errExit(ErrCodes.MISSING_VALUE, "Data stack is empty!")
    else:
        datatmp = datastack.pop()

    if datatmp.elType != datatype:
        errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

    return datatmp.value


def getDStackElWType(datastack):
    if len(datastack) == 0:
        errExit(ErrCodes.MISSING_VALUE, "Data stack is empty!")
    else:
        data = datastack.pop()

    return data.elType, data.value


def writeStats(statsfiles, statsrecords, numofinstr, numofvars):
    for fileName in statsfiles:
        try:
            filedata = open(fileName, "w")
        except:
            errExit(ErrCodes.OUT_FILE_ERR, "Can not open output statistic file!")

        for record in statsrecords:
            if record == "vars":
                print(numofvars, file=filedata)
            else:
                print(numofinstr, file=filedata)

        filedata.close()


def checkVar(var):
    if re.match(r'^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$', var) is None:
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid var name!")


def checkNil(nil):
    if nil != "nil":
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid nil value!")


def checkInt(intval):
    if re.match(r'^[+\-]?\d+$', intval):
        return True
    return False


def checkBool(boolval):
    if boolval in ["true", "false"]:
        return True
    return False


def checkString(stringval):
    if stringval is None:
        stringval = ""

    if re.match(r'^([^\s\\#]|(\\\d{3}))*$', stringval):
        return True
    return False


def checkLabel(label):
    if re.match(r'^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$', label) is None:
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Ivalid label name!")


def checkType(typeval):
    if typeval not in ["int", "string", "bool"]:
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid name of data type!")


def checkXMLArgs(args, numOfArgs, expectedTypes):
    if len(args) != numOfArgs:
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid number of arguments!")

    expectedTags = []
    ordOfArgs = []

    for num in range(1, numOfArgs + 1):
        expectedTags.append("arg" + str(num))

    for arg in args:
        if len(arg) != 0:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Arguments can not have children!")

        if arg.tag not in expectedTags:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid argument tag!")

        if len(arg.attrib) != 1:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Argument has invalid number of attributes!")

        if "type" not in arg.attrib:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid argument attribute!")

        expectedTags.remove(arg.tag)

        ordOfArgs.append(arg.tag)

        if expectedTypes[int(arg.tag[3]) - 1] == "symb":
            if arg.attrib["type"] == "var":
                if arg.text is None:
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing name of variable!")

                checkVar(arg.text)
            elif arg.attrib["type"] == "nil":
                if arg.text is None:
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing nil value!")

                checkNil(arg.text)
            elif arg.attrib["type"] == "int":
                if arg.text is None:
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing int value!")

                if not checkInt(arg.text):
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument invalid int value!")
            elif arg.attrib["type"] == "bool":
                if arg.text is None:
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing bool value!")

                if not checkBool(arg.text):
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument invalid bool value!")
            elif arg.attrib["type"] == "string":
                if not checkString(arg.text):
                    errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument invalid string value!")
            else:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid XML argument type!")
        elif expectedTypes[int(arg.tag[3]) - 1] == "var":
            if arg.attrib["type"] != "var":
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid XML argument type!")

            if arg.text is None:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing name of variable!")

            checkVar(arg.text)
        elif expectedTypes[int(arg.tag[3]) - 1] == "label":
            if arg.attrib["type"] != "label":
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid XML argument type!")

            if arg.text is None:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing name of label!")

            checkLabel(arg.text)
        else:
            if arg.attrib["type"] != "type":
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid XML argument type!")

            if arg.text is None:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "XML argument missing type value!")

            checkType(arg.text)

    return ordOfArgs


if __name__ == "__main__":
    datafile = None
    """
        Checking program arguments
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["help", "source=", "input=", "stats="])
    except:
        print("Use --help to see, how to use this script!")
        errExit(ErrCodes.PAR_ERR, "Invalid parameter!")

    sourceFile = None
    inputFile = None
    statsFiles = []
    statsRecords = []

    for opt, arg in opts:
        if opt == "--help":
            if len(sys.argv) != 2:
                errExit(ErrCodes.PAR_ERR, "Invalid combination of arguments!")
            print("#############################################################################")
            print("Run this script as: 'python3.8 interpret.py' with possible arguments")
            print("Possible arguments:")
            print("--help print information about usage")
            print("--source=file input file with XML representation of source code")
            print("--input=file file with inputs for interpretation of source code")
            print("--stats=file file with statistics")
            print("--insts record number of executed instructions")
            print("--vars record number of initialized variables")
            print("#############################################################################")
            sys.exit(0)

        elif opt == "--input":
            if inputFile:
                errExit(ErrCodes.PAR_ERR, "Multiple input files!")
            else:
                inputFile = arg
        elif opt == "--source":
            if sourceFile:
                errExit(ErrCodes.PAR_ERR, "Multiple source files!")
            else:
                sourceFile = arg
        elif opt == "--stats":
            if arg == sys.argv[0]:
                errExit(ErrCodes.PAR_ERR, "This script does not want to be rewrite!")
            else:
                statsFiles.append(arg)
        elif opt == "--insts":
            statsRecords.append("insts")
        else:
            statsRecords.append("vars")

    if not sourceFile and not inputFile:
        errExit(ErrCodes.PAR_ERR, "Missing source and input, at least one of them have to be there!")

    if len(statsRecords) != 0 and len(statsFiles) == 0:
        errExit(ErrCodes.PAR_ERR, "Missing stats file!")

    if not sourceFile:
        sourceFile = sys.stdin

    """
        Working with XML and controlling it
    """
    try:
        tree = ET.parse(sourceFile)
    except IOError:
        errExit(ErrCodes.IN_FILE_ERR, "Can not open source file!")
    except ET.ParseError:
        errExit(ErrCodes.XML_FORMAT_ERR, "Invalid XML format!")

    root = tree.getroot()

    if root.tag != "program":
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Root tag is not program!")

    if "language" not in root.attrib:
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Language attribute in root is missing!")

    if root.attrib["language"].upper() != "IPPCODE21":
        errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid language attribute!")

    del root.attrib["language"]

    for atrb in root.attrib:
        if atrb not in ["name", "description"]:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid root attribute!")


    orderArray = []
    fncDict = dict()
    labelDict = dict()

    for XMLInstr in root:
        if XMLInstr.tag != "instruction":
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid instruction tag!")

        if len(XMLInstr.attrib) != 2:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Instruction has invalid number of attributes!")

        for attrib in XMLInstr.attrib:
            if attrib not in ["order", "opcode"]:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid instruction attribute!")

        if re.match(r'^\+?\d+$', XMLInstr.attrib["order"]) is None:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Instruction order has to be positive number!")

        order = int(XMLInstr.attrib["order"])

        if order == 0:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Instruction order can not be zero!")

        if order in orderArray:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Instruction order has to be unique!")

        opcode = XMLInstr.attrib["opcode"].upper()

        orderArray.append(order)

        if (opcode in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "CLEARS", "ADDS", "SUBS", "MULS",
                       "IDIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "NOTS", "INT2CHARS", "STRI2INTS"]):
            if len(XMLInstr) != 0:
                errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Invalid number of arguments!")

            fncDict[order] = Instruction(opcode)
        # 1: var
        elif opcode in ["DEFVAR", "POPS"]:
            checkXMLArgs(XMLInstr, 1, ["var"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[0].text)
        # 1: label
        elif opcode in ["CALL", "LABEL", "JUMP", "JUMPIFEQS", "JUMPIFNEQS"]:
            checkXMLArgs(XMLInstr, 1, ["label"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[0].text)

            if opcode == "LABEL":
                labelName = XMLInstr[0].text
                if labelName in labelDict:
                    errExit(ErrCodes.SEMANTIC_ERR, "Label name has to be unique!")
                else:
                    labelDict[labelName] = order
        # 1: symb
        elif opcode in ["PUSHS", "WRITE", "EXIT", "DPRINT"]:
            checkXMLArgs(XMLInstr, 1, ["symb"])
            fncDict[order] = Instruction(opcode)

            if XMLInstr[0].attrib["type"] == "string" and XMLInstr[0].text is None:
                fncDict[order].arg1 = Argument("")
            else:
                fncDict[order].arg1 = Argument(XMLInstr[0].text)

            fncDict[order].arg1.type = XMLInstr[0].attrib["type"]
        # 1: var, 2: symb
        elif opcode in ["MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE"]:
            ordOfArgs = checkXMLArgs(XMLInstr, 2, ["var", "symb"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[ordOfArgs.index("arg1")].text)

            if XMLInstr[ordOfArgs.index("arg2")].attrib["type"] == "string" and \
                    XMLInstr[ordOfArgs.index("arg2")].text is None:
                fncDict[order].arg2 = Argument("")
            else:
                fncDict[order].arg2 = Argument(XMLInstr[ordOfArgs.index("arg2")].text)

            fncDict[order].arg2.type = XMLInstr[ordOfArgs.index("arg2")].attrib["type"]
        # 1: var, 2: type
        elif opcode == "READ":
            ordOfArgs = checkXMLArgs(XMLInstr, 2, ["var", "type"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[ordOfArgs.index("arg1")].text)
            fncDict[order].arg2 = Argument(XMLInstr[ordOfArgs.index("arg2")].text)
        # 1: var, 2,3: symb
        elif (opcode in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR",
                         "SETCHAR"]):
            ordOfArgs = checkXMLArgs(XMLInstr, 3, ["var", "symb", "symb"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[ordOfArgs.index("arg1")].text)

            if XMLInstr[ordOfArgs.index("arg2")].attrib["type"] == "string" and \
                    XMLInstr[ordOfArgs.index("arg2")].text is None:
                fncDict[order].arg2 = Argument("")
            else:
                fncDict[order].arg2 = Argument(XMLInstr[ordOfArgs.index("arg2")].text)

            fncDict[order].arg2.type = XMLInstr[ordOfArgs.index("arg2")].attrib["type"]

            if XMLInstr[ordOfArgs.index("arg3")].attrib["type"] == "string" and \
                    XMLInstr[ordOfArgs.index("arg3")].text is None:
                fncDict[order].arg3 = Argument("")
            else:
                fncDict[order].arg3 = Argument(XMLInstr[ordOfArgs.index("arg3")].text)

            fncDict[order].arg3.type = XMLInstr[ordOfArgs.index("arg3")].attrib["type"]
        # 1: label, 2,3: symb
        elif opcode in ["JUMPIFEQ", "JUMPIFNEQ"]:
            ordOfArgs = checkXMLArgs(XMLInstr, 3, ["label", "symb", "symb"])
            fncDict[order] = Instruction(opcode)
            fncDict[order].arg1 = Argument(XMLInstr[ordOfArgs.index("arg1")].text)

            if XMLInstr[ordOfArgs.index("arg2")].attrib["type"] == "string" and \
                    XMLInstr[ordOfArgs.index("arg2")].text is None:
                fncDict[order].arg2 = Argument("")
            else:
                fncDict[order].arg2 = Argument(XMLInstr[ordOfArgs.index("arg2")].text)

            fncDict[order].arg2.type = XMLInstr[ordOfArgs.index("arg2")].attrib["type"]

            if XMLInstr[ordOfArgs.index("arg3")].attrib["type"] == "string" and \
                    XMLInstr[ordOfArgs.index("arg3")].text is None:
                fncDict[order].arg3 = Argument("")
            else:
                fncDict[order].arg3 = Argument(XMLInstr[ordOfArgs.index("arg3")].text)

            fncDict[order].arg3.type = XMLInstr[ordOfArgs.index("arg3")].attrib["type"]
        else:
            errExit(ErrCodes.XML_STRUCT_LEX_SYNTAX_ERR, "Unknown operation code!")
    """
        Opening file for stats
    """
    if inputFile is not None:
        try:
            datafile = open(inputFile)
        except:
            errExit(ErrCodes.IN_FILE_ERR, "Can not open input file!")
        sys.stdin = datafile

    orderArray.sort()

    numOfExecInstr = 0
    numOfDefVars = 0

    frames = dict()
    frames["GF"] = dict()
    frames["LF"] = None
    frames["TF"] = None

    frameStack = []
    dataStack = []
    callStack = []

    i = 0
    """
        Actual program
    """
    while i < len(orderArray):


        instr = fncDict[orderArray[i]]
        # CREATEFRAME
        if instr.opcode == "CREATEFRAME":
            frames["TF"] = dict()
        # PUSHFRAME
        elif instr.opcode == "PUSHFRAME":
            if frames["TF"] is None:
                errExit(ErrCodes.NONEXISTENT_FRAME, "TF does not exist!")

            frameStack.append(frames["TF"])
            frames["LF"] = frames["TF"]
            frames["TF"] = None
        # POPFRAME
        elif instr.opcode == "POPFRAME":
            if frames["LF"] is None:
                errExit(ErrCodes.NONEXISTENT_FRAME, "Local frame does not exist!")

            frames["TF"] = frames["LF"]
            frameStack.pop()

            if len(frameStack) == 0:
                frames["LF"] = None
            else:
                frames["LF"] = frameStack.pop()
                frameStack.append(frames["LF"])
        # RETURN
        elif instr.opcode == "RETURN":
            if len(callStack) == 0:
                errExit(ErrCodes.MISSING_VALUE, "Call stack is empty!")

            i = callStack.pop()
        # BREAK
        elif instr.opcode == "BREAK":
            line = i + 1

            printToStderr("Instruction number: " + str(line))
            printToStderr("Instruction order: " + str(orderArray[i]))
            printToStderr("number of executed instructions: " + str(numOfExecInstr))
            printToStderr("GF CONTENT(variable|type|value)")
            printToStderr("==========================================")
            printFrameStderr("GF", frames)
            printToStderr("LF CONTENT(variable|type|value)")
            printToStderr("==========================================")
            if frames["LF"] is None:
                printToStderr("LF does not exit.")
            else:
                printFrameStderr("LF", frames)
            printToStderr("TF CONTENT(variable|type|value)")
            printToStderr("==========================================")
            if frames["TF"] is None:
                printToStderr("TF does not exit.")
            else:
                printFrameStderr("TF", frames)
        # CLEARS
        elif instr.opcode == "CLEARS":
            while len(dataStack) > 0:
                dataStack.pop()
        # ADD <var> <symb1> <symb2>
        elif instr.opcode == "ADD":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = int(getArg(instr, frames, "int"))
            value2 = int(getArg(instr, frames, "int", 3))

            result = value1 + value2

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = result
        # ADDS <var> <symb1> <symb2>
        elif instr.opcode == "ADDS":
            val2 = int(getDStackEl(dataStack, "int"))
            val1 = int(getDStackEl(dataStack, "int"))
            result = val1 + val2
            dataStack.append(DataStackEl("int", result))
        # SUB <var> <symb1> <symb2>
        elif instr.opcode == "SUB":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = int(getArg(instr, frames, "int"))
            value2 = int(getArg(instr, frames, "int", 3))

            result = value1 - value2

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = result
        # SUBS <var> <symb1> <symb2>
        elif instr.opcode == "SUBS":
            value2 = int(getDStackEl(dataStack, "int"))
            value1 = int(getDStackEl(dataStack, "int"))
            result = value1 - value2
        # MUL <var> <symb1> <symb2>
        elif instr.opcode == "MUL":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = int(getArg(instr, frames, "int"))
            value2 = int(getArg(instr, frames, "int", 3))

            result = value1 * value2

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = result
        # MULS <var> <symb1> <symb2>
        elif instr.opcode == "MULS":
            value2 = int(getDStackEl(dataStack, "int"))
            value1 = int(getDStackEl(dataStack, "int"))
            result = value1 * value2
            dataStack.append(DataStackEl("int", result))
        # IDIV <var> <symb1> <symb2>
        elif instr.opcode == "IDIV":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = int(getArg(instr, frames, "int"))
            value2 = int(getArg(instr, frames, "int", 3))

            if value2 == 0:
                errExit(ErrCodes.INVALID_OPERAND_VALUE, "Division by zero!")

            result = value1 // value2

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = result
        # IDIVS <var> <symb1> <symb2>
        elif instr.opcode == "IDIVS":
            value2 = int(getDStackEl(dataStack, "int"))
            value1 = int(getDStackEl(dataStack, "int"))

            if value2 == 0:
                errExit(ErrCodes.INVALID_OPERAND_VALUE, "Division by zero!")
            else:
                result = value1 // value2
            dataStack.append(DataStackEl("int", result))
        # LT <var> <symb1> <symb2>
        elif instr.opcode == "LT":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            type1, value1 = getArgWType(instr, frames)

            if type1 == "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

            value2 = getArg(instr, frames, type1, 3)

            if type1 == "int":
                value1 = int(value1)
                value2 = int(value2)
            if type1 == "string":
                value1 = dealWithEscape(value1)
                value2 = dealWithEscape(value2)
            if value1 < value2:
                frames[var[0]][var[1]].value = "true"
            else:
                frames[var[0]][var[1]].value = "false"

            frames[var[0]][var[1]].varType = "bool"
        # LTS <var> <symb1> <symb2>
        elif instr.opcode == "LTS":
            type2, value2 = getDStackElWType(dataStack)

            if type2 == "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

            value1 = getDStackEl(dataStack, type2)

            if type2 == "int":
                value2 = int(value2)
                value1 = int(value1)
            if type2 == "string":
                value1 = dealWithEscape(value1)
                value2 = dealWithEscape(value2)
            if value1 < value2:
                dataStack.append(DataStackEl("bool", "true"))
            else:
                dataStack.append(DataStackEl("bool", "false"))
        # GT <var> <symb1> <symb2>
        elif instr.opcode == "GT":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            type1, value1 = getArgWType(instr, frames)

            if type1 == "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

            value2 = getArg(instr, frames, type1, 3)
            if type1 == "int":
                value1 = int(value1)
                value2 = int(value2)

            if type1 == "string":
                value1 = dealWithEscape(value1)
                value2 = dealWithEscape(value2)
            if value1 > value2:
                frames[var[0]][var[1]].value = "true"
            else:
                frames[var[0]][var[1]].value = "false"

            frames[var[0]][var[1]].varType = "bool"
        # GTS <var> <symb1> <symb2>
        elif instr.opcode == "GTS":
            type2, value2 = getDStackElWType(dataStack)

            if type2 == "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

            value1 = getDStackEl(dataStack, type2)

            if type2 == "int":
                value2 = int(value2)
                value1 = int(value1)
            if type2 == "string":
                value1 = dealWithEscape(value1)
                value2 = dealWithEscape(value2)

            if value1 > value2:
                dataStack.append(DataStackEl("bool", "true"))
            else:
                dataStack.append(DataStackEl("bool", "false"))
        # EQ <var> <symb1> <symb2>
        elif instr.opcode == "EQ":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            type1, value1 = getArgWType(instr, frames)
            type2, value2 = getArgWType(instr, frames, 3)

            frames[var[0]][var[1]].value = "false"

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)
                if value1 == value2:
                    frames[var[0]][var[1]].value = "true"
            elif type1 != "nil" and type2 != "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

            frames[var[0]][var[1]].varType = "bool"
        # EQS <var> <symb1> <symb2>
        elif instr.opcode == "EQS":
            type2, value2 = getDStackElWType(dataStack)
            type1, value1 = getDStackElWType(dataStack)

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)

                if value1 == value2:
                    dataStack.append(DataStackEl("bool", "true"))
                else:
                    dataStack.append(DataStackEl("bool", "false"))
            elif type1 == "nil" or type2 == "nil":
                dataStack.append(DataStackEl("bool", "false"))
            else:
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
        # AND <var> <symb1> <symb2>
        elif instr.opcode == "AND":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = getArg(instr, frames, "bool")
            value2 = getArg(instr, frames, "bool", 3)

            if value1 == "true" and value2 == "true":
                frames[var[0]][var[1]].value = "true"
            else:
                frames[var[0]][var[1]].value = "false"

            frames[var[0]][var[1]].varType = "bool"
        # ANDS <var> <symb1> <symb2>
        elif instr.opcode == "ANDS":
            value2 = getDStackEl(dataStack, "bool")
            value1 = getDStackEl(dataStack, "bool")

            if value1 == value2 == "true":
                dataStack.append(DataStackEl("bool", "true"))
            else:
                dataStack.append(DataStackEl("bool", "false"))
        # OR <var> <symb1> <symb2>
        elif instr.opcode == "OR":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = getArg(instr, frames, "bool")
            value2 = getArg(instr, frames, "bool", 3)

            if value1 == "true" or value2 == "true":
                frames[var[0]][var[1]].value = "true"
            else:
                frames[var[0]][var[1]].value = "false"

            frames[var[0]][var[1]].varType = "bool"
        # ORS <var> <symb1> <symb2>
        elif instr.opcode == "ORS":
            value2 = getDStackEl(dataStack, "bool")
            value1 = getDStackEl(dataStack, "bool")

            if value1 == "true" or value2 == "true":
                dataStack.append(DataStackEl("bool", "true"))
            else:
                dataStack.append(DataStackEl("bool", "false"))
        # NOT <var> <symb1> <symb2>
        elif instr.opcode == "NOT":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value = getArg(instr, frames, "bool")

            if value == "true":
                value = "false"
            else:
                value = "true"

            frames[var[0]][var[1]].varType = "bool"
            frames[var[0]][var[1]].value = value
        # NOTS <var> <symb1> <symb2>
        elif instr.opcode == "NOTS":
            value = getDStackEl(dataStack, "bool")

            if value == "false":
                dataStack.append(DataStackEl("bool", "true"))
            else:
                dataStack.append(DataStackEl("bool", "false"))
        # INT2CHAR <var> <symb>
        elif instr.opcode == "INT2CHAR":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value = int(getArg(instr, frames, "int"))

            try:
                frames[var[0]][var[1]].value = chr(value)
            except:
                errExit(ErrCodes.STRING_ERR, "Invalid ordinal value of character in UNICODE!")

            frames[var[0]][var[1]].varType = "string"
        # INT2CHARS <var> <symb>
        elif instr.opcode == "INT2CHARS":
            value = int(getDStackEl(dataStack, "int"))
            try:
                dataStack.append(DataStackEl("string", chr(value)))
            except:
                errExit(ErrCodes.STRING_ERR, "Invalid ordinal value of character in UNICODE!")
        # STRI2INT <var> <symb1> <symb2>
        elif instr.opcode == "STRI2INT":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = dealWithEscape(getArg(instr, frames, "string"))
            value2 = int(getArg(instr, frames, "int", 3))

            if value2 < 0 or value2 >= len(value1):
                errExit(ErrCodes.STRING_ERR, "Index out of range!")

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = ord(value1[value2])
        # STRI2INTS <var> <symb1> <symb2>
        elif instr.opcode == "STRI2INTS":
            value2 = int(getDStackEl(dataStack, "int"))
            value1 = dealWithEscape(getDStackEl(dataStack, "string"))

            if value2 < 0 or value2 >= len(value1):
                errExit(ErrCodes.STRING_ERR, "Index out of range!")

            dataStack.append(DataStackEl("int", ord(value1[value2])))
        # DEFVAR <var>
        elif instr.opcode == "DEFVAR":
            var = instr.arg1.value.split('@')

            if not frameExist(var[0], frames):
                errExit(ErrCodes.NONEXISTENT_FRAME, "Frame does not exist!")
            elif varInFrame(var[1], var[0], frames):
                errExit(ErrCodes.SEMANTIC_ERR, "Redefinition of variable!")
            else:
                frames[var[0]][var[1]] = Variable(var[1], None, None)

            numOfDefVars += 1
        # PUSHS <symb>
        elif instr.opcode == "PUSHS":
            if instr.arg1.type == "var":
                var = instr.arg1.value.split('@')
                checkVarExistance(var[1], var[0], frames)
                checkVarInit(var[1], var[0], frames)
                dataStack.append(DataStackEl(frames[var[0]][var[1]].varType, frames[var[0]][var[1]].value))
            else:
                dataStack.append(DataStackEl(instr.arg1.type, instr.arg1.value))
        # POPS <var>
        elif instr.opcode == "POPS":
            if len(dataStack) == 0:
                errExit(ErrCodes.MISSING_VALUE, "Data stack is empty!")
            else:
                var = instr.arg1.value.split('@')
                checkVarExistance(var[1], var[0], frames)
                dataEl = dataStack.pop()
                frames[var[0]][var[1]].varType = dataEl.elType
                frames[var[0]][var[1]].value = dataEl.value
        # CALL <label>
        elif instr.opcode == "CALL":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")
            callStack.append(i)
            i = orderArray.index(labelDict[instr.arg1.value]) - 1
        # LABEL <label>
        elif instr.opcode == "LABEL":
            pass
        # JUMP <label>
        elif instr.opcode == "JUMP":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")
            i = orderArray.index(labelDict[instr.arg1.value]) - 1
        # JUMPIFEQ <var> <symb1> <symb2>
        elif instr.opcode == "JUMPIFEQ":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")

            type1, value1 = getArgWType(instr, frames)
            type2, value2 = getArgWType(instr, frames, 3)

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)
                if value1 == value2:
                    i = orderArray.index(labelDict[instr.arg1.value]) - 1
            elif type1 != "nil" and type2 != "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
        # JUMPIFEQS <var> <symb1> <symb2>
        elif instr.opcode == "JUMPIFEQS":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")

            type2, value2 = getDStackElWType(dataStack)
            type1, value1 = getDStackElWType(dataStack)

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)

                if value1 == value2:
                    i = orderArray.index(labelDict[instr.arg1.value]) - 1
            elif "nil" == type1 or type2:
                i = orderArray.index(labelDict[instr.arg1.value]) - 1

            else:
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
        # JUMPIFNEQ <var> <symb1> <symb2>
        elif instr.opcode == "JUMPIFNEQ":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")

            type1, value1 = getArgWType(instr, frames)
            type2, value2 = getArgWType(instr, frames, 3)

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)

                if value1 != value2:
                    i = orderArray.index(labelDict[instr.arg1.value]) - 1
            elif type1 != "nil" and type2 != "nil":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
            else:
                i = orderArray.index(labelDict[instr.arg1.value]) - 1
        # JUMPIFNEQS <var> <symb1> <symb2>
        elif instr.opcode == "JUMPIFNEQS":
            if instr.arg1.value not in labelDict:
                errExit(ErrCodes.SEMANTIC_ERR, "Undefined label!")

            type2, value2 = getDStackElWType(dataStack)
            type1, value1 = getDStackElWType(dataStack)

            if type1 == type2:
                if type1 == "int":
                    value1 = int(value1)
                    value2 = int(value2)
                if type1 == "string":
                    value1 = dealWithEscape(value1)
                    value2 = dealWithEscape(value2)
                if value1 != value2:
                    i = orderArray.index(labelDict[instr.arg1.value]) - 1
            elif "nil" == type1 or type2:
                i = orderArray.index(labelDict[instr.arg1.value]) - 1

            else:
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
        # EXIT <symb>
        elif instr.opcode == "EXIT":
            if instr.arg1.type == "var":
                var = instr.arg1.value.split('@')
                checkVarExistance(var[1], var[0], frames)
                checkVarInit(var[1], var[0], frames)
                if frames[var[0]][var[1]].varType != "int":
                    errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

                value = int(frames[var[0]][var[1]].value)
            else:
                if instr.arg1.type != "int":
                    errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")

                value = int(instr.arg1.value)

            if value < 0 or value > 49:
                errExit(ErrCodes.INVALID_OPERAND_VALUE, "Invalid operand value!")

            if len(statsFiles) != 0:
                writeStats(statsFiles, statsRecords, numOfExecInstr + 1, numOfDefVars)

            closeFile()
            sys.exit(value)
        # DPRINT <symb>
        elif instr.opcode == "DPRINT":
            if instr.arg1.type == "var":
                var = instr.arg1.value.split('@')
                checkVarExistance(var[1], var[0], frames)
                checkVarInit(var[1], var[0], frames)

                dataType = frames[var[0]][var[1]].varType
                value = frames[var[0]][var[1]].value
            else:
                dataType = instr.arg1.type
                value = instr.arg1.value

            if dataType == "int":
                print(int(value), end='', file=sys.stderr)
            elif dataType == "bool":
                print(value, end='', file=sys.stderr)
            elif dataType == "string":
                print(dealWithEscape(value), end='', file=sys.stderr)
            else:
                print("", end='', file=sys.stderr)
        # MOVE <var> <symb>
        elif instr.opcode == "MOVE":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            dataType, value = getArgWType(instr, frames)

            frames[var[0]][var[1]].varType = dataType
            frames[var[0]][var[1]].value = value
        # STRLEN <var> <symb>
        elif instr.opcode == "STRLEN":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value = getArg(instr, frames, "string")
            strLen = len(dealWithEscape(value))

            frames[var[0]][var[1]].varType = "int"
            frames[var[0]][var[1]].value = strLen
        # TYPE <var> <symb>
        elif instr.opcode == "TYPE":
            var1 = instr.arg1.value.split('@')
            checkVarExistance(var1[1], var1[0], frames)

            if instr.arg2.type == "var":
                var2 = instr.arg2.value.split('@')
                checkVarExistance(var2[1], var2[0], frames)

                if frames[var2[0]][var2[1]].varType is None:
                    value = ""
                else:
                    value = frames[var2[0]][var2[1]].varType
            else:
                value = instr.arg2.type

            frames[var1[0]][var1[1]].varType = "string"
            frames[var1[0]][var1[1]].value = value
        # WRITE <symb>
        elif instr.opcode == "WRITE":
            if (instr.arg1.type == "var"):
                var = instr.arg1.value.split('@')
                checkVarExistance(var[1], var[0], frames)
                checkVarInit(var[1], var[0], frames)
                dataType = frames[var[0]][var[1]].varType
                value = frames[var[0]][var[1]].value
            else:
                dataType = instr.arg1.type
                value = instr.arg1.value
            if dataType == "int":
                print(value, end='')
            elif dataType == "bool":
                print(value, end='')
            elif dataType == "string":
                print(dealWithEscape(value), end='')
            else:
                print("", end='')
        # READ <var> <type>
        elif instr.opcode == "READ":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            dataType = instr.arg2.value

            try:
                value = input()
            except:
                dataType = "nil"

            if dataType == "int":
                try:
                    value = int(value)
                except:
                    dataType = "nil"
            elif dataType == "bool":
                value = value.lower()
                if value != "true":
                    value = "false"
            if dataType == "nil":
                value = "nil"

            frames[var[0]][var[1]].varType = dataType
            frames[var[0]][var[1]].value = value
        # CONCAT <var> <symb1> <symb2>
        elif instr.opcode == "CONCAT":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)

            value1 = getArg(instr, frames, "string")
            value2 = getArg(instr, frames, "string", 3)

            result = value1 + value2

            frames[var[0]][var[1]].varType = "string"
            frames[var[0]][var[1]].value = result
        # GETCHAR <var> <symb1> <symb2>
        elif instr.opcode == "GETCHAR":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)
            value1 = dealWithEscape(getArg(instr, frames, "string"))
            value2 = int(getArg(instr, frames, "int", 3))

            if value2 < 0 or value2 >= len(value1):
                errExit(ErrCodes.STRING_ERR, "Index out of range!")

            frames[var[0]][var[1]].varType = "string"
            frames[var[0]][var[1]].value = value1[value2]
        # SETCHAR <var> <symb1> <symb2>
        elif instr.opcode == "SETCHAR":
            var = instr.arg1.value.split('@')
            checkVarExistance(var[1], var[0], frames)
            checkVarInit(var[1], var[0], frames)
            if frames[var[0]][var[1]].varType != "string":
                errExit(ErrCodes.INVALID_OPERAND_TYPE, "Incorrect operand type!")
            editStr = dealWithEscape(frames[var[0]][var[1]].value)
            value1 = int(getArg(instr, frames, "int"))
            value2 = dealWithEscape(getArg(instr, frames, "string", 3))

            if len(value2) == 0:
                errExit(ErrCodes.STRING_ERR, "Replacement is empty!")

            if value1 < 0 or value1 >= len(editStr):
                errExit(ErrCodes.STRING_ERR, "Index out of range!")
            editStr = editStr[:value1] + value2[0] + editStr[value1+1:]
            frames[var[0]][var[1]].value = editStr

        numOfExecInstr += 1
        i += 1

    closeFile()

    """
        Print stats to file
    """
    if len(statsFiles) != 0:
        writeStats(statsFiles, statsRecords, numOfExecInstr, numOfDefVars)

    sys.exit(0)
