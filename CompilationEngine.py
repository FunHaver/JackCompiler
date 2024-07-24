import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import unescape
import os, sys
class CompilationEngine:
    def __init__(self, tokenFile, compiledFile):
        self.tokenFile = tokenFile
        self.compiledFile = compiledFile
        self.__tokenList = []
        # The token xml file is flat. There is no recursion needed to get the information
        for child in ElementTree.parse(self.tokenFile).getroot():
            self.__tokenList.append({"tag": child.tag, "text": unescape("".join(child.text.split()))})
        self.currentToken = None
        self.__tokenIdx = -1
        self.__indentLevel = 0

        
    def __advanceToken(self):
        self.__tokenIdx = self.__tokenIdx + 1
        self.currentToken = self.__tokenList[self.__tokenIdx]

    def __regressToken(self):
        if self.__tokenIdx > 0:
            self.__tokenIdx = self.__tokenIdx - 1
            self.currentToken = self.__tokenList[self.__tokenIdx]
        else:
            sys.exit("ERROR: cannot get token with index "  + str((self.__tokenIdx - 1)))
        
    def __writeTerminalElement(self):
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "
        writeString = writeString + "<" + self.currentToken["tag"] + "> " + self.currentToken["text"] + " </" + self.currentToken["tag"] + ">" + os.linesep
        self.compiledFile.write(writeString)
   

    def compileClass(self):
        finishedClassCompile = False
        self.__advanceToken()

        self.compiledFile.write("<class>" + os.linesep)
        self.__indentLevel += 1
        self.__writeTerminalElement()
        self.__advanceToken()
        self.__writeTerminalElement()
        self.__advanceToken()
        self.__writeTerminalElement()
        
        self.__advanceToken()

        while not finishedClassCompile:
            if self.currentToken["tag"] == "keyword":
                if self.currentToken["text"] == "static" or self.currentToken["text"] == "field":
                    self.compileClassVarDec() #TODO
                    self.__advanceToken()
                elif self.currentToken["text"] == "constructor" or self.currentToken["text"] == "function" or self.currentToken["text"] == "method":
                    self.compileSubroutine() #TODO
                    self.__advanceToken()
                else:
                    sys.exit("ERROR: Invalid keyword " + self.currentToken["text"] + " for class variable or subroutine declaration")
            elif self.currentToken["tag"] == "symbol":
                if self.currentToken["text"] == "}": # THE LAST TOKEN IN A JACK FILE
                    self.__writeTerminalElement()
                    finishedClassCompile = True
                else:
                    sys.exit("ERROR: Invalid symbol " + self.currentToken["text"] + " in class definition")
            else:
                sys.exit("ERROR: Invalid token in class " + self.currentToken["text"])


        self.compiledFile.write("</class>" + os.linesep)


    