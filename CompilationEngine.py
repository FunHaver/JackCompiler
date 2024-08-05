import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape, unescape
import copy
import SymbolTable
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
        self.__classSymbolTable = SymbolTable.SymbolTable()
        self.__subroutineSymbolTable = SymbolTable.SymbolTable()
        self.__tokenIdx = -1
        self.__indentLevel = 0

        self.__classVarDecKeywords = set(["field", "static"])
        self.__classDecKeywords = set(["class"])
        self.__subroutineKeywords = set(["constructor", "method", "function"])
        self.__statementKeywords = set(["let","do","if","while","return"])
        self.__typeKeywords = set(["boolean","int","char"])
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

    def __writeTerminalElement(self, tag, text):
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "

        writeString = writeString + "<" + tag + "> " + escape(str(text)) + " </" + tag + ">" + os.linesep
        self.compiledFile.write(writeString)
        
    # returns the token that was written
    def __writeTerminalToken(self):
        self.__writeTerminalElement(self.currentToken["tag"], self.currentToken["text"])
        writtenToken = copy.deepcopy(self.currentToken)
        self.__advanceToken()
        return writtenToken

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

    def __isSubroutineDecKeyword(self, token):
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


    def __isClassScope(self, category):
        return category in self.__classDecKeywords or category in self.__subroutineKeywords

    def __writeType(self):
        if self.currentToken["text"] in self.__typeKeywords:
            return self.__writeTerminalToken()
        else:
            userDefinedType = self.currentToken
            self.__writeIdentifier(self.currentToken["text"], "class")
            return userDefinedType

    def __writeIdentifier(self, name, category, varType=None):
        symbolState = "used"
        currentTable = None
        recordSymbol = False
        if category != "class" and category != "subroutine":
            recordSymbol = True
        if self.__isClassScope(category):
            currentTable = self.__classSymbolTable
        else:
            currentTable = self.__subroutineSymbolTable

        if varType is not None:
            symbolState = "defined"
            if recordSymbol:
                currentTable.define(name, varType, category.upper())
        self.__writeNonterminalElementOpen("identifier") # identifier
        self.__writeTerminalElement("name", name)
        self.__writeTerminalElement("category", category)
        if currentTable is not None:
            self.__writeTerminalElement("state", symbolState)
        if recordSymbol:
            self.__writeTerminalElement("runningIndex", currentTable.indexOf(name))


        self.__writeNonterminalElementClose("identifier")
        self.__advanceToken()

    #searches all symbol tables, starting with subroutine
    #Returns Kind if found, None if not found in either table
    def __findSymbolKind(self, name):
        if self.__subroutineSymbolTable.kindOf(name) != None:
            return self.__subroutineSymbolTable.kindOf(name)
        elif self.__classSymbolTable.kindOf(name) != None:
            return self.__classSymbolTable.kindOf(name)
        else:
            return None

    def compileClass(self):
        finishedClassCompile = False
        self.__advanceToken()

        self.__writeNonterminalElementOpen("class")
        self.__writeTerminalToken() # class
        self.__writeIdentifier(self.currentToken["text"], "class", True) # className
        self.__writeTerminalToken() # {
        
        while not finishedClassCompile:

            if self.__isClassVarDecKeyword(self.currentToken):
                self.compileClassVarDec()
            elif self.__isSubroutineDecKeyword(self.currentToken):
                self.compileSubroutine() 
            elif self.__isCloseCurlyBrace(self.currentToken): # THE LAST TOKEN IN A JACK FILE
                self.__writeTerminalToken() # }
                finishedClassCompile = True
            else:
                self.__exitError()


        self.__writeNonterminalElementClose("class")


    def compileClassVarDec(self):
        self.__writeNonterminalElementOpen("classVarDec")
        self.__writeTerminalToken() # 'static' | 'field'
        self.__writeType() # type
        self.__writeTerminalToken() # varName
        
        # (',' varName)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            loopCount = 0
            while self.currentToken["text"] != ";":
                self.__writeTerminalToken() # ,
                self.__writeTerminalToken() # varName
                loopCount += 1

                if loopCount > 25:
                    print("ERROR: Stuck in loop writing var defs, did you forget a ';' ?")
                    self.__exitError()
        
        self.__writeTerminalToken() # ;
        self.__writeNonterminalElementClose("classVarDec")


    def compileSubroutine(self):
        self.__writeNonterminalElementOpen("subroutineDec")
        self.__writeTerminalToken() # 'constructor' | 'function' | 'method'
        subroutineReturnType = self.__writeTerminalToken() # 'void' | type
        self.__writeIdentifier(self.currentToken["text"],"subroutine",subroutineReturnType["text"]) # subroutineName
        self.__writeTerminalToken() # (
        self.compileParameterList()
        self.__writeTerminalToken() # )
        self.__writeNonterminalElementOpen("subroutineBody")
        self.__writeTerminalToken() # {

        while self.currentToken["tag"] != "symbol" and self.currentToken["text"] != "}":
            # varDec* 
            if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "var":
                self.compileVarDec() 
            # statements
            elif self.__isStatementKeyword(self.currentToken):
                self.compileStatements()
            else:
                self.__exitError()
        
        self.__writeTerminalToken() # }
        self.__writeNonterminalElementClose("subroutineBody")
        self.__writeNonterminalElementClose("subroutineDec")

    def compileVarDec(self):
        self.__writeNonterminalElementOpen("varDec")
        self.__writeTerminalToken() # var

        varType = self.__writeType() # type
        self.__writeIdentifier(self.currentToken["text"],"VAR",varType["text"]) # varName


        # (',' varName)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            while self.currentToken["text"] != ";":
                self.__writeTerminalToken() # ,
                self.__writeIdentifier(self.currentToken["text"],"VAR",varType["text"]) # varName
        
        self.__writeTerminalToken() # ;        
        self.__writeNonterminalElementClose("varDec")

    def compileParameterList(self):
        self.__writeNonterminalElementOpen("parameterList")
        # ((type varName) (',' type varName)*)?
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
            self.__writeNonterminalElementClose("parameterList")
        else:
            self.__writeType() # type
            self.__writeTerminalToken() # varName
            loopCount = 0

            while not(self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")"):
                self.__writeTerminalToken() # ,
                self.__writeType() # type
                self.__writeTerminalToken() # varName
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

        self.__writeTerminalToken() # let
        self.__writeIdentifier(self.currentToken["text"], "VAR")

        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "[":
            self.__writeTerminalToken() # [
            self.compileExpression() 
            self.__writeTerminalToken() # ]

        self.__writeTerminalToken() # =
        self.compileExpression() 
        self.__writeTerminalToken() # ;
        self.__writeNonterminalElementClose("letStatement")

    def compileIf(self):
        self.__writeNonterminalElementOpen("ifStatement")

        self.__writeTerminalToken() # if
        self.__writeTerminalToken() # (
        self.compileExpression() 
        self.__writeTerminalToken() # )

        self.__writeTerminalToken() # {
        self.compileStatements()
        self.__writeTerminalToken() # }

        if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "else":
            self.__writeTerminalToken() # else
            self.__writeTerminalToken() # {
            self.compileStatements()
            self.__writeTerminalToken() # }

        self.__writeNonterminalElementClose("ifStatement")

    def compileWhile(self):
        self.__writeNonterminalElementOpen("whileStatement")

        self.__writeTerminalToken() # while
        self.__writeTerminalToken() # (
        self.compileExpression() 
        self.__writeTerminalToken() # )
        
        self.__writeTerminalToken() # {
        self.compileStatements()
        self.__writeTerminalToken() # }

        self.__writeNonterminalElementClose("whileStatement")

    def compileDo(self):
        self.__writeNonterminalElementOpen("doStatement")
        
        self.__writeTerminalToken() # do
        self.__compileSubroutineCall()
        self.__writeTerminalToken() # ;

        self.__writeNonterminalElementClose("doStatement")

    def compileReturn(self):
        self.__writeNonterminalElementOpen("returnStatement")

        self.__writeTerminalToken() # return

        if self.currentToken["tag"] != "symbol" and self.currentToken["text"] != ";":
            self.compileExpression()

        self.__writeTerminalToken() # ;

        self.__writeNonterminalElementClose("returnStatement")

    def compileExpression(self):
        self.__writeNonterminalElementOpen("expression")
        while self.__isTerm(self.currentToken):
            self.compileTerm()

            if self.__isOp(self.currentToken):
                self.__writeTerminalToken() # op
        self.__writeNonterminalElementClose("expression")

    def compileExpressionList(self):
        self.__writeNonterminalElementOpen("expressionList")
        loopCount = 0
        while self.__isTerm(self.currentToken):
            self.compileExpression()
            if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
                break
            self.__writeTerminalToken() # ,
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
                self.__compileSubroutineCall()
            elif self.currentToken["text"] == "[" :
                self.__regressToken()
                symbolKind = self.__findSymbolKind(self.currentToken["text"])
                if symbolKind == None:
                    symbolKind = "class"
                
                self.__writeIdentifier(self.currentToken["text"], symbolKind) # className | varName
                self.__writeTerminalToken() # [
                self.compileExpression()
                self.__writeTerminalToken() # ]
            else: 
                sys.exit("ERROR: array and advanced expressions not implemented")
        else:   
            self.__regressToken() # backtrack after looking forward
            if self.__isConstant(self.currentToken):
                self.__writeTerminalToken() # integerConstant | stringConstant | keywordConstant | varName
            elif self.currentToken["tag"] == "identifier":
                symbolKind = self.__findSymbolKind(self.currentToken["text"])
                if symbolKind == None:
                    symbolKind = "class"
                self.__writeIdentifier(self.currentToken["text"], symbolKind) # varName | className
            elif self.__isUnaryOp(self.currentToken):
                self.__writeTerminalToken() # unaryOp
                self.compileTerm()
            
            elif self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "(":
                self.__writeTerminalToken() # (
                self.compileExpression()
                self.__writeTerminalToken() # )

            elif self.__isTerm(self.currentToken):
                self.compileTerm()

        self.__writeNonterminalElementClose("term")

    def __compileSubroutineCall(self):
        self.__advanceToken() # lookahead for dot or open paren
        if self.currentToken["tag"] == "symbol":
            if self.currentToken["text"] == "(":
                self.__regressToken() # ok go back
                self.__writeIdentifier(self.currentToken["text"], "subroutine") # subroutineName
                self.__writeTerminalToken() # (
                self.compileExpressionList()
                self.__writeTerminalToken() # )
            elif self.currentToken["text"] == ".":
                self.__regressToken() # ok go back
                symbolKind = self.__findSymbolKind(self.currentToken["text"])
                if symbolKind == None:
                    symbolKind = "class"
                
                self.__writeIdentifier(self.currentToken["text"], symbolKind) # className | varName
                self.__writeTerminalToken() # .
                self.__writeIdentifier(self.currentToken["text"], "subroutine") # subRoutineName
                self.__writeTerminalToken() # (
                self.compileExpressionList()
                self.__writeTerminalToken() # )