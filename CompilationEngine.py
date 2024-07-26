import xml.etree.ElementTree as ElementTree
import copy
from xml.sax.saxutils import escape, unescape
import os, sys
class CompilationEngine:
    def __init__(self, tokenFile, compiledFile):
        self.tokenFile = tokenFile
        self.compiledFile = compiledFile
        self.__tokenList = []
        # The token xml file is flat. There is no recursion needed to get the information
        for child in ElementTree.parse(self.tokenFile).getroot():
            self.__tokenList.append({"tag": child.tag, "text": unescape(child.text[1:-1])})
        self.currentToken = None
        self.__tokenIdx = -1
        self.__indentLevel = 0

        self.__classVarDecKeywords = set(["field", "static"])
        self.__subroutineKeywords = set(["constructor", "method", "function"])
        self.__statementKeywords = set(["let","do","if","while","return"])
        self.__tagConstants = set(["integerConstant", "stringConstant"])
        self.__keywordConstants = set(["true", "false", "null", "this"])
        self.__lookAheadSymbols = set(["[","(","."])
        self.__unaryOps = set(["-","~"])
        self.__opSymbols = set(["+","-","*","/","&","|","<",">","="])


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
        
    def __exitError(self):
        sys.exit("ERROR: Token " + str(self.__tokenIdx + 1) + " Invalid token '" + self.currentToken["text"] + "' in " + self.tokenFile.name)
    
    def __writeTerminalElement(self):
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "
        writeString = writeString + "<" + self.currentToken["tag"] + "> " + escape(self.currentToken["text"]) + " </" + self.currentToken["tag"] + ">" + os.linesep
        self.compiledFile.write(writeString)
        self.__advanceToken()

    def __writeNonterminalElementOpen(self, tagName):
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "
        writeString = writeString + "<" + tagName + ">" + os.linesep
        self.compiledFile.write(writeString)
        self.__indentLevel += 1

    def __writeNonterminalElementClose(self, tagName):
        self.__indentLevel += -1
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "
        writeString = writeString + "</" + tagName + ">" + os.linesep
        self.compiledFile.write(writeString)
   
    def __isClassVarDecKeyword(self, token):
        if token["tag"] == "keyword":
            if token["text"] in self.__classVarDecKeywords:
                return True
            else:
                return False
        else:
            return False

    def __isSubroutineKeyword(self, token):
        if token["tag"] == "keyword":
            if token["text"] in self.__subroutineKeywords:
                return True
            else:
                return False
        else:
            return False

    def __isStatementKeyword(self, token):
        if token["tag"] == "keyword":
            if token["text"] in self.__statementKeywords:
                return True
            else:
                return False
        else:
            return False
        
    def __isConstant(self, token):
        if token["tag"] in self.__tagConstants:
            return True
        elif token["tag"] == "keyword":
            if token["text"] in self.__keywordConstants:
                return True
            else:
                return False  
        else:
            return False

    def __isLookAheadExpression(self, tokenOne, tokenTwo):
        if tokenOne["tag"] == "identifier":
            if tokenTwo["tag"] == "symbol":
                if tokenTwo["text"] in self.__lookAheadSymbols:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
                
    def __isTerm(self,token):
        if self.__isConstant(token):
            return True
        elif token["tag"] == "identifier":
            return True
        elif token["tag"] == "symbol":
            if token["text"] == "(":
                return True
            elif self.__isUnaryOp(token):
                return True
            else:
                return False
        else:
            return False
            
    def __isUnaryOp(self, token):
        if token["tag"] == "symbol":
            if token["text"] in self.__unaryOps:
                return True
            else:
                return False
        else:
            return False
        
    def __isOp(self, token):
        if token["tag"] == "symbol":
            if token["text"] in self.__opSymbols:
                return True
            else: 
                return False
        else:
            return False
    
    def __isCloseCurlyBrace(self,token):
        return token["tag"] == "symbol" and token["text"] == "}"
    
    def compileClass(self):
        finishedClassCompile = False
        self.__advanceToken()

        self.__writeNonterminalElementOpen("class")
        self.__writeTerminalElement() # class
        self.__writeTerminalElement() # className
        self.__writeTerminalElement() # {
        
        while not finishedClassCompile:

            if self.__isClassVarDecKeyword(self.currentToken):
                self.compileClassVarDec()
            elif self.__isSubroutineKeyword(self.currentToken):
                self.compileSubroutine() 
            elif self.__isCloseCurlyBrace(self.currentToken): # THE LAST TOKEN IN A JACK FILE
                self.__writeTerminalElement() # }
                finishedClassCompile = True
            else:
                self.__exitError()


        self.__writeNonterminalElementClose("class")


    def compileClassVarDec(self):
        self.__writeNonterminalElementOpen("classVarDec")
        self.__writeTerminalElement() # 'static' | 'field'
        self.__writeTerminalElement() # type
        self.__writeTerminalElement() # varName
        
        # (',' varName)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            loopCount = 0
            while self.currentToken["text"] != ";":
                self.__writeTerminalElement() # ,
                self.__writeTerminalElement() # varName
                loopCount += 1

                if loopCount > 25:
                    print("ERROR: Stuck in loop writing var defs, did you forget a ';' ?")
                    self.__exitError()
        
        self.__writeTerminalElement() # ;
        self.__writeNonterminalElementClose("classVarDec")


    def compileSubroutine(self):
        self.__writeNonterminalElementOpen("subroutineDec")
        self.__writeTerminalElement() # 'constructor' | 'function' | 'method'
        self.__writeTerminalElement() # 'void' | type
        self.__writeTerminalElement() # subroutineName
        self.__writeTerminalElement() # (
        self.compileParameterList()
        self.__writeTerminalElement() # )
        self.__writeNonterminalElementOpen("subroutineBody")
        self.__writeTerminalElement() # {

        while self.currentToken["tag"] != "symbol" and self.currentToken["text"] != "}":
            # varDec* 
            if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "var":
                self.compileVarDec() 
            # statements
            elif self.__isStatementKeyword(self.currentToken):
                self.compileStatements()
            else:
                self.__exitError()
        
        self.__writeTerminalElement() # }
        self.__writeNonterminalElementClose("subroutineBody")
        self.__writeNonterminalElementClose("subroutineDec")

    def compileVarDec(self):
        self.__writeNonterminalElementOpen("varDec")
        self.__writeTerminalElement() # var
        self.__writeTerminalElement() # 'void' | type
        self.__writeTerminalElement() # varName

        # (',' varName)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            while self.currentToken["text"] != ";":
                self.__writeTerminalElement() # ,
                self.__writeTerminalElement() # varName
        
        self.__writeTerminalElement() # ;        
        self.__writeNonterminalElementClose("varDec")

    def compileParameterList(self):
        self.__writeNonterminalElementOpen("parameterList")
        # ((type varName) (',' type varName)*)?
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
            self.__writeNonterminalElementClose("parameterList")
        else:
            self.__writeTerminalElement() # type
            self.__writeTerminalElement() # varName
            loopCount = 0

            while not(self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")"):
                self.__writeTerminalElement() # ,
                self.__writeTerminalElement() # type
                self.__writeTerminalElement() # varName
                loopCount += 1
                if loopCount > 25:
                    print("Stuck in infinite loop, improperly formed parameter list")
                    self.__exitError()

            
            self.__writeNonterminalElementClose("parameterList")


    def compileStatements(self):
        self.__writeNonterminalElementOpen("statements")

        if self.currentToken["tag"] != "keyword" and not(self.__isCloseCurlyBrace(self.currentToken)):
            sys.exit("ERROR: Statement must begin with keyword")
        while self.__isStatementKeyword(self.currentToken):

            if self.currentToken["text"] == "let":
                self.compileLet() 
            elif self.currentToken["text"] == "if":
                self.compileIf() 
            elif self.currentToken["text"] == "while":
                self.compileWhile() 
            elif self.currentToken["text"] == "do":
                self.compileDo() 
            elif self.currentToken["text"] == "return":
                self.compileReturn() 
            else:
                self.__exitError()
            
        self.__writeNonterminalElementClose("statements")

    def compileLet(self):
        self.__writeNonterminalElementOpen("letStatement")

        self.__writeTerminalElement() # let
        self.__writeTerminalElement() # varName

        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "[":
            self.__writeTerminalElement() # [
            self.compileExpression() 
            self.__writeTerminalElement() # ]

        self.__writeTerminalElement() # =
        self.compileExpression() 
        self.__writeTerminalElement() # ;
        self.__writeNonterminalElementClose("letStatement")

    def compileIf(self):
        self.__writeNonterminalElementOpen("ifStatement")

        self.__writeTerminalElement() # if
        self.__writeTerminalElement() # (
        self.compileExpression() 
        self.__writeTerminalElement() # )

        self.__writeTerminalElement() # {
        self.compileStatements()
        self.__writeTerminalElement() # }

        if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "else":
            self.__writeTerminalElement() # else
            self.__writeTerminalElement() # {
            self.compileStatements()
            self.__writeTerminalElement() # }

        self.__writeNonterminalElementClose("ifStatement")

    def compileWhile(self):
        self.__writeNonterminalElementOpen("whileStatement")

        self.__writeTerminalElement() # while
        self.__writeTerminalElement() # (
        self.compileExpression() 
        self.__writeTerminalElement() # )
        
        self.__writeTerminalElement() # {
        self.compileStatements()
        self.__writeTerminalElement() # }

        self.__writeNonterminalElementClose("whileStatement")

    def compileDo(self):
        self.__writeNonterminalElementOpen("doStatement")
        
        self.__writeTerminalElement() # do
        self.__compileSubroutine()
        self.__writeTerminalElement() # ;

        self.__writeNonterminalElementClose("doStatement")

    def compileReturn(self):
        self.__writeNonterminalElementOpen("returnStatement")

        self.__writeTerminalElement() # return

        if self.currentToken["tag"] != "symbol" and self.currentToken["text"] != ";":
            self.compileExpression()

        self.__writeTerminalElement() # ;

        self.__writeNonterminalElementClose("returnStatement")

    def compileExpression(self):
        self.__writeNonterminalElementOpen("expression")
        while self.__isTerm(self.currentToken):
            self.compileTerm()

            if self.__isOp(self.currentToken):
                self.__writeTerminalElement() # op
        self.__writeNonterminalElementClose("expression")

    def compileExpressionList(self):
        self.__writeNonterminalElementOpen("expressionList")
        loopCount = 0
        while self.__isTerm(self.currentToken):
            self.compileExpression()
            if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
                break
            self.__writeTerminalElement() # ,
            loopCount += 1
            if loopCount > 25:
                print("Stuck in infinite loop, improperly formed expression list")
                self.__exitError()
        self.__writeNonterminalElementClose("expressionList")

    def compileTerm(self):
        self.__writeNonterminalElementOpen("term")
        previousToken = copy.deepcopy(self.currentToken)
        self.__advanceToken()
        
        if self.__isLookAheadExpression(previousToken, self.currentToken):
            if self.currentToken["text"] == "(" or self.currentToken["text"] == ".":
                self.__regressToken()
                self.__compileSubroutine()
            elif self.currentToken["text"] == "[" :
                self.__regressToken()
                self.__writeTerminalElement() # varName
                self.__writeTerminalElement() # [
                self.compileExpression()
                self.__writeTerminalElement() # ]
            else: 
                sys.exit("ERROR: array and advanced expressions not implemented")
        else:   
            self.__regressToken() # backtrack after looking forward
            if self.__isConstant(self.currentToken) or self.currentToken["tag"] == "identifier":
                self.__writeTerminalElement() # integerConstant | stringConstant | keywordConstant | varName

            elif self.__isUnaryOp(self.currentToken):
                self.__writeTerminalElement() # unaryOp
                self.compileTerm()
            
            elif self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "(":
                self.__writeTerminalElement() # (
                self.compileExpression()
                self.__writeTerminalElement() # )

            elif self.__isTerm(self.currentToken):
                self.compileTerm()

        self.__writeNonterminalElementClose("term")

    def __compileSubroutine(self):
        self.__writeTerminalElement() # subRoutineName | (className | varName)
        if self.currentToken["tag"] == "symbol":
            if self.currentToken["text"] == "(":
                self.__writeTerminalElement() # (
                self.compileExpressionList()
                self.__writeTerminalElement() # )
            elif self.currentToken["text"] == ".":
                self.__writeTerminalElement() # .
                self.__writeTerminalElement() # subRoutineName
                self.__writeTerminalElement() # (
                self.compileExpressionList()
                self.__writeTerminalElement() # )