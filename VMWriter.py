class VMWriter:
    
    # Creates a new VM file and prepares it for writing
    def __init__(self, outFile):
        self.outFile = outFile
        print("construct VMWriter")

    # Writes a VM Push command
    # segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
    # index: int
    def writePush(self, segment, index):
        print("implement writePush")

    # Writes a VM Pop command
    # segment: (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)
    # index: int
    def writePop(self, segment, index):
        print("implement writePop")

    # Writes a VM Arithmetic command
    # command: (ADD, SUB, NEG, EQ, GT, LR, AND, OR, NOT)
    def writeArithmetic(self, command):
        print("implement writeArithmetic")

    # Writes a VM label command
    # label: String
    def writeLabel(self, label):
        print("implement writeLabel")

    # Writes a VM goto command
    # label: String
    def writeGoto(self, label):
        print("implement writeGoto")

    # Writes a VM if-goto command
    # label: String
    def writeIf(self, label):
        print("implement writeIf")

    # Writes a vm call command
    # name: String
    # nArgs: int
    def writeCall(self, name, nArgs):
        print("implement writeCall")

    # Writes a vm call command
    # name: String
    # nLocals: int
    # Writes a vm function command
    def writeFunction(self, name, nLocals):
        print("implement writeFunction")

    # Writes a vm return command
    def writeReturn(self):
        print("implement writeReturn")

    # closes output file
    def close(self):
        print("implement close")