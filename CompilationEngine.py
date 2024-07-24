import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape, unescape
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
        if self.__tokenIdx != (len(self.__tokenList) - 1):
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
        writeString = writeString + "<" + self.currentToken["tag"] + "> " + escape(self.currentToken["text"]) + " </" + self.currentToken["tag"] + ">" + os.linesep
        self.compiledFile.write(writeString)
        self.__advanceToken()
   
    def __isClassVarDecKeyword(token):
        if token["tag"] == "keyword":
            if token["text"] == "field":
                return True
            elif token["text"] == "static":
                return True
            else:
                return False
        else:
            return False

    def __isSubroutineKeyword(token):
        if token["tag"] == "keyword":
            if token["text"] == "constructor":
                return True
            elif token["text"] == "method":
                return True
            elif token["text"] == "function":
                return True
            else:
                return False
        else:
            return False

    def __isStatementKeyword(token):
        if token["tag"] == "keyword":
            if token["text"] == "let":
                return True
            elif token["text"] == "do":
                return True
            elif token["text"] == "if":
                return True
            elif token["text"] == "while":
                return True
            elif token["text"] == "return":
                return True
            else:
                return False
        else:
            return False
        
    
    def compileClass(self):
        finishedClassCompile = False
        self.__advanceToken()

        self.compiledFile.write("<class>" + os.linesep)
        self.__indentLevel += 1
        self.__writeTerminalElement() # class
        self.__writeTerminalElement() # className
        self.__writeTerminalElement() # {
        
        while not finishedClassCompile:

            if self.__isClassVarDecKeyword(self.currentToken):
                self.compileClassVarDec()
            elif self.__isSubroutineKeyword(self.currentToken):
                self.compileSubroutine() #TODO
            if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "}": # THE LAST TOKEN IN A JACK FILE
                self.__writeTerminalElement() # }
                finishedClassCompile = True
            else:
                sys.exit("ERROR: Invalid token '" + self.currentToken["text"] + "' in " + self.tokenFile.name())


        self.compiledFile.write("</class>" + os.linesep)


    def compileClassVarDec(self):
        self.__writeTerminalElement() # 'static' | 'field'
        self.__writeTerminalElement() # type
        self.__writeTerminalElement() # varName
        
        # (',' varName)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            while self.currentToken["text"] != ";":
                self.__writeTerminalElement() # ,
                self.__writeTerminalElement() # varName
        
        self.__writeTerminalElement() # ;


    def compileSubroutine(self):
        self.__writeTerminalElement() # 'constructor' | 'function' | 'method'
        self.__writeTerminalElement() # 'void' | type
        self.__writeTerminalElement() # subroutineName
        self.__writeTerminalElement() # (
        self.compileParameterList()
        
        self.__writeTerminalElement() # {

        # varDec* 
        if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "var":
            self.compileVarDec() #TODO
        # statements
        elif self.__isStatementKeyword(self.currentToken):
            self.compileStatements() #TODO


    def compileParameterList(self):

        # ((type varName) (',' type varName)*)?
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
            self.__writeTerminalElement() # )
        else:
            self.__writeTerminalElement() # type
            self.__writeTerminalElement() # varName

            while self.currentToken["tag"] != "symbol" and self.currentToken["text"] != ")":
                self.__writeTerminalElement() # ,
                self.__writeTerminalElement() # type
                self.__writeTerminalElement() # varName

            self.__writeTerminalElement() # )


    def compileStatements(self):
        if self.currentToken["tag"] != "keyword":
            sys.exit("ERROR: Statement must begin with keyword")

        if self.currentToken["text"] == "let":
            self.compileLet() #TODO
        elif self.currentToken["text"] == "if":
            self.compileIf() #TODO
        elif self.currentToken["text"] == "while":
            self.compileWhile() #TODO
        elif self.currentToken["text"] == "do":
            self.compileDo() #TODO
        elif self.currentToken["text"] == "return":
            self.compileReturn() #TODO
        else:
            sys.exit("ERROR: Invalid keyword '" + self.currentToken["text"] + "' for statement beginning")
    
    
        

