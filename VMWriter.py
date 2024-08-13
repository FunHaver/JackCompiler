import os, sys

class VMWriter:
    
    # Creates a new VM file and prepares it for writing
    def __init__(self, outFilePath):
        self.outFile = open(outFilePath,"w",encoding="utf-8")


    def __segmentDecoder(self, segment):
        segment = segment.upper()
        if segment == "CONST":
            return "constant"
        elif segment == "ARG":
            return "argument"
        elif segment == "LOCAL" or segment == "VAR":
            return "local"
        elif segment == "STATIC":
            return "static"
        elif segment == "FIELD":
            return "this"
        elif segment == "THAT":
            return "that"
        elif segment == "POINTER":
            return "pointer"
        elif segment == "TEMP":
            return "temp"
        else:
            sys.exit("ERROR: Unknown segment " + segment)
        
    # Writes a VM Push command
    # segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
    # index: int
    def writePush(self, segment, index):
        self.outFile.write("push " + self.__segmentDecoder(segment) + " " + str(index) + os.linesep)

    # Writes a VM Pop command
    # segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
    # index: int
    def writePop(self, segment, index):
        self.outFile.write("pop " + self.__segmentDecoder(segment) + " " + str(index) + os.linesep)

    # Writes a VM Arithmetic command
    # command: (ADD, SUB, NEG, EQ, GT, LR, AND, OR, NOT)
    def writeArithmetic(self, command):
        command = command.upper()
        if command == "ADD":
            self.outFile.write("add" + os.linesep)
        elif command == "LT":
            self.outFile.write("lt" + os.linesep)
        elif command == "GT":
            self.outFile.write("gt" + os.linesep)
        elif command == "AND":
            self.outFile.write("and" + os.linesep)
        elif command == "NEG":
            self.outFile.write("neg" + os.linesep)
        elif command == "SUB":
            self.outFile.write("sub" + os.linesep)
        elif command == "NOT":
            self.outFile.write("not" + os.linesep)
        elif command == "EQ":
            self.outFile.write("eq" + os.linesep)
        else:
            print("implement writeArithmetic for " + command)

    # Writes a VM label command
    # label: String
    def writeLabel(self, label):
        self.outFile.write("label " + label.upper() + os.linesep)

    # Writes a VM goto command
    # label: String
    def writeGoto(self, label):
        self.outFile.write("goto " + label.upper() + os.linesep)

    # Writes a VM if-goto command
    # label: String
    def writeIf(self, label):
        self.outFile.write("if-goto " + label.upper() + os.linesep)

    # Writes a vm call command
    # name: String
    # nArgs: int
    def writeCall(self, name, nArgs):
        self.outFile.write("call " + name + " " + str(nArgs) + os.linesep)

    # Writes a vm call command
    # name: String
    # nLocals: int
    # Writes a vm function command
    def writeFunction(self, name, nLocals):
        self.outFile.write("function " + name + " " + str(nLocals) + os.linesep)

    # Writes a vm return command
    def writeReturn(self):
        self.outFile.write("return" + os.linesep)

    # closes output file
    def close(self):
        self.outFile.close()