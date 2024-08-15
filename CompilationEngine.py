import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import escape, unescape
import copy
import SymbolTable, VMWriter
import os, sys

class CompilationEngine:
    def __init__(self, tokenFile, compiledFilePath):
        self.tokenFile = tokenFile
        self.compiledFile = compiledFilePath
        self.vmWriter = VMWriter.VMWriter(compiledFilePath)
        self.__tokenList = []
        # The token xml file is flat. There is no recursion needed to get the information
        for child in ElementTree.parse(self.tokenFile).getroot():
            self.__tokenList.append({"tag": child.tag, "text": unescape(child.text[1:-1])})
        self.currentToken = None
        self.__classSymbolTable = SymbolTable.SymbolTable()
        self.__subroutineSymbolTable = SymbolTable.SymbolTable()
        self.__tokenIdx = -1
        self.__indentLevel = 0
        self.__className = ""
        self.__subroutineName = ""
        self.__labelCounter = 0
        self.__classVarDecKeywords = set(["field", "static"])
        self.__subroutineKeywords = set(["constructor", "method", "function"])
        self.__statementKeywords = set(["let","do","if","while","return"])
        self.__typeKeywords = set(["boolean","int","char"])
        self.__tagConstants = set(["integerConstant", "stringConstant"])
        self.__keywordConstants = set(["true", "false", "null", "this"])
        self.__lookAheadSymbols = set(["[","(","."])
        self.__unaryOps = set(["-","~"])
        self.__opSymbols = set(["+","-","*","/","&","|","<",">","="])
        self.__osOperators = set(["*","/"])
        self.__primitiveOperators = set(["+","-","~","=",">","<","&","|"])


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
        return
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
        return
        writeString = ""
        for x in range(self.__indentLevel):
            writeString += "  "
        writeString = writeString + "<" + tagName + ">" + os.linesep
        self.compiledFile.write(writeString)
        self.__indentLevel += 1

    def __writeNonterminalElementClose(self, tagName):
        return
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
            if token["text"] == "(" or token["text"] == "[":
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
        return category in self.__classVarDecKeywords

    def __writeType(self):
        if self.currentToken["text"] in self.__typeKeywords or self.currentToken["text"] == "void":
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

    #searches all symbol tables, starting with subroutine
    #Returns index int if found, -1 if not found in either table 
    def __findSymbolIdx(self, name):
        if self.__subroutineSymbolTable.indexOf(name) != -1:
            return self.__subroutineSymbolTable.indexOf(name)
        elif self.__classSymbolTable.indexOf(name) != -1:
            return self.__classSymbolTable.indexOf(name)
        else:
            return -1
    #searches all symbol tables, starting with subroutine
    #Returns type as string if found, None if not found in either table 
    def __findSymbolType(self, name):
        if self.__subroutineSymbolTable.typeOf(name) != None:
            return self.__subroutineSymbolTable.typeOf(name)
        elif self.__classSymbolTable.typeOf(name) != None:
            return self.__classSymbolTable.typeOf(name)
        else:
            return None
    
    # converts op symbol to binary arithmetic (takes two off stack, returns one) VM command
    def __convertToArithVmCommand(self, opSymbol):
        if opSymbol == "+":
            return "ADD"
        elif opSymbol == "<":
            return "LT"
        elif opSymbol == ">":
            return "GT"
        elif opSymbol == "&":
            return "AND"
        elif opSymbol == "-":
            return "SUB"
        elif opSymbol == "=":
            return "EQ"
        elif opSymbol == "|":
            return "OR"
        else:
            sys.exit("Cannot convert symbol to arithmetic operation: " + opSymbol)
   
    # converts op symbol to unary arithmetic (takes one off stack, returns one) VM command
    def __convertToUnaryVmCommand(self, opSymbol):
        if opSymbol == "-":
            return "NEG"
        elif opSymbol == "~":
            return "NOT"
        else:
            sys.exit("Cannot convert symbol to unary operation: " + opSymbol)

    # writes a call to an OS-defined operation function into the VM
    def __callOsMath(self, symbol):
        if symbol == "*":
            self.vmWriter.writeCall("Math.multiply", 2)
        elif symbol == "/":
            self.vmWriter.writeCall("Math.divide", 2)
        else:
            sys.exit("ERROR: unknown symbol " + symbol)

    def __addToSymbolTable(self):
        segment = self.currentToken["text"]
        if segment == "var":
            varDecType = "varDec"
        else:
            varDecType = "classVarDec"
        
        self.__writeNonterminalElementOpen(varDecType)
        self.__writeTerminalToken() # var | field | static

        varType = self.__writeType() # type
        self.__writeIdentifier(self.currentToken["text"],segment,varType["text"]) # identifier


        # (',' identifier)* zero or more consecutive varNames, comma delimited
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ",":
            while self.currentToken["text"] != ";":
                self.__writeTerminalToken() # ,
                self.__writeIdentifier(self.currentToken["text"],segment,varType["text"]) # identifier
        
        self.__writeTerminalToken() # ;        
        self.__writeNonterminalElementClose(varDecType)

    #sets THAT 0 to address of array item (array pointer + index)
    def __setThatToArrayItem(self,variable):
        self.__writeTerminalToken() # [
        self.compileExpression() 
        self.__writeTerminalToken() # ]
        # push arr pointer to stack
        self.vmWriter.writePush(self.__findSymbolKind(variable),self.__findSymbolIdx(variable))
        self.vmWriter.writeArithmetic("ADD") # add base address + pointer
        # pop to pointer 1 segment, our special array buddy
        self.vmWriter.writePop("POINTER",1)

    def compileClass(self):
        finishedClassCompile = False
        self.__advanceToken()

        self.__writeNonterminalElementOpen("class")
        self.__writeTerminalToken() # class
        self.__className = self.currentToken["text"] # class
        self.__writeIdentifier(self.currentToken["text"], "class") # className
        self.__writeTerminalToken() # {
        while self.currentToken["tag"] == "keyword" and (self.currentToken["text"] == "static" or self.currentToken["text"] == "field"):
            self.__addToSymbolTable()

        self.compileClassVarDec()
        while not finishedClassCompile:
            if self.__isSubroutineDecKeyword(self.currentToken):
                self.compileSubroutine() 
            elif self.__isCloseCurlyBrace(self.currentToken): # THE LAST TOKEN IN A JACK FILE
                self.__writeTerminalToken() # }
                finishedClassCompile = True
            else:
                self.__exitError()


        self.__writeNonterminalElementClose("class")
        self.vmWriter.close()


    def compileClassVarDec(self):
        for x in range(self.__classSymbolTable.varCount("STATIC")): 
            self.vmWriter.writePush("CONST", "0")
            self.vmWriter.writePop("STATIC",x)
  

    def __allocateObjectMemory(self):
        self.vmWriter.writePush("CONST", self.__classSymbolTable.varCount("FIELD"))
        self.vmWriter.writeCall("Memory.alloc", "1")
        self.vmWriter.writePop("POINTER",0)
        for x in range(self.__classSymbolTable.varCount("FIELD")): 
            self.vmWriter.writePush("CONST","0")
            self.vmWriter.writePop("FIELD",x)

    def compileSubroutine(self):
        self.__subroutineSymbolTable.startSubroutine()
        self.__writeNonterminalElementOpen("subroutineDec")
        subroutineKind = self.currentToken["text"]
        self.__writeTerminalToken() # 'constructor' | 'function' | 'method'
        
        subroutineReturnType = self.__writeType() # 'void' | type
        self.__subroutineName = self.currentToken["text"]
        self.__writeIdentifier(self.currentToken["text"],"subroutine",subroutineReturnType["text"]) # subroutineName
        self.__writeTerminalToken() # (
        self.compileParameterList(subroutineKind == "method")
        self.__writeTerminalToken() # )
        
        self.__writeNonterminalElementOpen("subroutineBody")
        self.__writeTerminalToken() # {
        
        # varDec* 
        while self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "var":
            self.__addToSymbolTable()

        # So we know the number of vars in the fn defition signature
        self.vmWriter.writeFunction(self.__className + "." + self.__subroutineName, str(self.__subroutineSymbolTable.varCount("VAR")))
        if subroutineKind == "constructor":
            self.__allocateObjectMemory()
        elif subroutineKind == "method":
        # methods have an "invisible" argument 0 of the base address of the object
            self.vmWriter.writePush("ARG",0)
            self.vmWriter.writePop("POINTER",0)
        
        self.compileVarDec()            
        
        # statements
        if self.__isStatementKeyword(self.currentToken):
            self.compileStatements()

        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "}":
            self.__writeTerminalToken() # }
            self.__writeNonterminalElementClose("subroutineBody")
            self.__writeNonterminalElementClose("subroutineDec")
        else:
            print("ERROR: subroutines must be defined as variable declarations followed by statements followed by a } symbol.")
            self.__exitError()

    def compileVarDec(self):
        for x in range(self.__subroutineSymbolTable.varCount("VAR")): 
            self.vmWriter.writePush("CONST", "0")
            self.vmWriter.writePop("LOCAL",x)


    def compileParameterList(self,method=False):
        self.__writeNonterminalElementOpen("parameterList")
        if method:
            self.__subroutineSymbolTable.define("that", "pointer", "ARG")
        # ((type varName) (',' type varName)*)?
        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
            self.__writeNonterminalElementClose("parameterList")
        else:
            argType = self.__writeType() # type
            self.__writeIdentifier(self.currentToken["text"],"ARG",argType["text"]) # varName
            nLocals = 1
            loopCount = 0

            while not(self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")"):
                nLocals += 1
                self.__writeTerminalToken() # ,
                argType = self.__writeType() # type
                self.__writeIdentifier(self.currentToken["text"],"ARG",argType["text"]) # varName
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
        variable = self.currentToken["text"]
        self.__writeIdentifier(self.currentToken["text"], self.__findSymbolKind(self.currentToken["text"])) # identifier

        if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == "[":
            
            self.__setThatToArrayItem(variable) 
            self.vmWriter.writePush("POINTER",1)
            self.vmWriter.writePop("TEMP",1) # temporarily store the THAT pointer for variable assignment in TEMP
            self.__writeTerminalToken() # =
            self.compileExpression()
            self.vmWriter.writePush("TEMP",1) # retrieve destination var's pointer from TEMP
            self.vmWriter.writePop("POINTER",1)
            self.vmWriter.writePop("THAT",0)

        else:
            self.__writeTerminalToken() # =
            self.compileExpression()
            self.vmWriter.writePop(self.__findSymbolKind(variable),self.__findSymbolIdx(variable))
        self.__writeTerminalToken() # ;
        self.__writeNonterminalElementClose("letStatement")

    def compileIf(self):
        self.__writeNonterminalElementOpen("ifStatement")
        elseLabel = self.__className + "_" + self.__subroutineName + "_" + "else_" + str(self.__labelCounter)
        endIfLabel = self.__className + "_" + self.__subroutineName + "_" + "endIf_" + str(self.__labelCounter)
        self.__labelCounter += 1
        self.__writeTerminalToken() # if
        self.__writeTerminalToken() # (
        self.compileExpression() 
        self.__writeTerminalToken() # )
        self.vmWriter.writeArithmetic("NOT")
        self.vmWriter.writeIf(elseLabel)
        self.__writeTerminalToken() # {
        self.compileStatements()
        self.vmWriter.writeGoto(endIfLabel)
        self.__writeTerminalToken() # }
        self.vmWriter.writeLabel(elseLabel)
        if self.currentToken["tag"] == "keyword" and self.currentToken["text"] == "else":
            self.__writeTerminalToken() # else
            self.__writeTerminalToken() # {
            self.compileStatements()
            self.__writeTerminalToken() # }
        self.vmWriter.writeLabel(endIfLabel)
        self.__writeNonterminalElementClose("ifStatement")

    def compileWhile(self):
        self.__writeNonterminalElementOpen("whileStatement")
        startLabel = self.__className + "_" + self.__subroutineName + "_" + "while_" + str(self.__labelCounter)
        endLabel = startLabel + "_end"
        self.__labelCounter += 1
        self.__writeTerminalToken() # while
        self.vmWriter.writeLabel(startLabel)
        self.__writeTerminalToken() # (
        self.compileExpression() 
        self.__writeTerminalToken() # )
        self.vmWriter.writeArithmetic("NOT")
        self.vmWriter.writeIf(endLabel)
        self.__writeTerminalToken() # {
        self.compileStatements()
        self.__writeTerminalToken() # }
        self.vmWriter.writeGoto(startLabel)
        self.vmWriter.writeLabel(endLabel)

        self.__writeNonterminalElementClose("whileStatement")

    #Do statements are always used with void return functions
    def compileDo(self):
        self.__writeNonterminalElementOpen("doStatement")
        
        self.__writeTerminalToken() # do
        self.__compileSubroutineCall()
        self.vmWriter.writePop("TEMP", "0") # ignore VOID return value
        self.__writeTerminalToken() # ;

        self.__writeNonterminalElementClose("doStatement")

    def compileReturn(self):
        self.__writeNonterminalElementOpen("returnStatement")

        self.__writeTerminalToken() # return

        if self.currentToken["tag"] != "symbol" and self.currentToken["text"] != ";":
            self.compileExpression()
        else:
            self.vmWriter.writePush("CONST","0")

        self.vmWriter.writeReturn()
        self.__writeTerminalToken() # ;

        self.__writeNonterminalElementClose("returnStatement")

    def compileExpression(self):
        self.__writeNonterminalElementOpen("expression")
        while self.__isTerm(self.currentToken):
            self.compileTerm()

            if self.__isOp(self.currentToken):
                arithmeticOperator = self.currentToken["text"]
                self.__advanceToken()
                self.compileTerm()
                if arithmeticOperator in self.__osOperators:
                    self.__callOsMath(arithmeticOperator)
                elif arithmeticOperator in self.__primitiveOperators:
                    self.vmWriter.writeArithmetic(self.__convertToArithVmCommand(arithmeticOperator))
                else:
                    print("Unknown operator " + arithmeticOperator)
        self.__writeNonterminalElementClose("expression")

    def compileExpressionList(self):
        self.__writeNonterminalElementOpen("expressionList")
        argCount = 0
        while self.__isTerm(self.currentToken):
            self.compileExpression()
            argCount += 1
            if self.currentToken["tag"] == "symbol" and self.currentToken["text"] == ")":
                break
            self.__writeTerminalToken() # ,
            if argCount > 25:
                print("Stuck in infinite loop, improperly formed expression list")
                self.__exitError()
        self.__writeNonterminalElementClose("expressionList")
        return argCount

    def __stringConstantAssignment(self, value):
        self.vmWriter.writePush("CONST", str(len(value))) # get len of str
        self.vmWriter.writeCall("String.new", 1) # construct String obj
        self.vmWriter.writePop("TEMP", 0) # Save new string pointer
        for char in value.encode("ascii"):
            self.vmWriter.writePush("TEMP", 0) # Push new string pointer onto stack (THIS)
            self.vmWriter.writePush("CONST",char) # Push char code onto stack
            self.vmWriter.writeCall("String.appendChar", 2) # appendChar
        
        




    # compiles constant to VM language equivalent
    def __compileConstant(self, constantTag, constantValue):
        if constantTag == "stringConstant":
            self.__stringConstantAssignment(constantValue)
        elif constantTag == "integerConstant":
            self.vmWriter.writePush("CONST", constantValue)
        elif constantValue == "true":
            self.vmWriter.writePush("CONST","1")
            self.vmWriter.writeArithmetic("NEG")
        elif constantValue == "false" or constantValue == "null":
            self.vmWriter.writePush("CONST","0")
        elif constantValue == "this":
            self.vmWriter.writePush("POINTER","0")
        else:
            sys.exit("ERROR: Unknown constant '" + constantValue + "' of type " + constantTag)

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
                    sys.exit("ERROR: could not find symbol kind for identifier " + self.currentToken)
                
                varName = self.currentToken["text"]
                self.__writeIdentifier(self.currentToken["text"], symbolKind) # varName
                self.__setThatToArrayItem(varName)
                self.vmWriter.writePush("THAT",0)
        else:   
            self.__regressToken() # backtrack after looking forward
            if self.__isConstant(self.currentToken):
                constantTag = self.currentToken["tag"]
                constantValue = self.currentToken["text"]
                self.__writeTerminalToken() 
                self.__compileConstant(constantTag, constantValue) # integerConstant | stringConstant | keywordConstant
                 
            elif self.currentToken["tag"] == "identifier":
                currentIdentifier = self.currentToken["text"]
                symbolKind = self.__findSymbolKind(currentIdentifier)
                if symbolKind == None:
                    symbolKind = "class"
                    self.__writeIdentifier(currentIdentifier, symbolKind)
                else:
                    self.__writeIdentifier(currentIdentifier, symbolKind) # varName | className
                    self.vmWriter.writePush(symbolKind,self.__findSymbolIdx(currentIdentifier))
            elif self.__isUnaryOp(self.currentToken):
                unaryOp = self.currentToken["text"]
                self.__writeTerminalToken() # unaryOp
                self.compileTerm()
                self.vmWriter.writeArithmetic(self.__convertToUnaryVmCommand(unaryOp))

            
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
            # method
            if self.currentToken["text"] == "(":
                self.__regressToken() # ok go back
                routineName = self.__className + "." + self.currentToken["text"]
                self.__writeIdentifier(self.currentToken["text"], "subroutine") # subroutineName
                self.__writeTerminalToken() # (
                self.vmWriter.writePush("POINTER",0)
                nArgs = self.compileExpressionList()
                self.__writeTerminalToken() # )
                self.vmWriter.writeCall(routineName, nArgs + 1)
            elif self.currentToken["text"] == ".":
                self.__regressToken() # ok go back
                symbolKind = self.__findSymbolKind(self.currentToken["text"])
                nArgs = 0
                methodMemberClass = None
                if symbolKind == None:
                    symbolKind = "class"

                # if symbolKind == class => function, else it is a method (I THINK)
                # routineName = self.currentToken["text"]
                if symbolKind != "class":
                    nArgs = 1
                    self.vmWriter.writePush(self.__findSymbolKind(self.currentToken["text"]), self.__findSymbolIdx(self.currentToken["text"]))
                    methodMemberClass = self.__findSymbolType(self.currentToken["text"])
                    if methodMemberClass == None:
                        sys.exit("ERROR: cannot find object for type " + self.currentToken["text"])
                    self.__writeIdentifier(self.currentToken["text"], symbolKind) # varName
                    self.__writeTerminalToken() # .
                    routineName = methodMemberClass + "." + self.currentToken["text"]

                else:
                    routineName = self.currentToken["text"]
                    self.__writeIdentifier(self.currentToken["text"], symbolKind) # className 
                    self.__writeTerminalToken() # .
                    routineName = routineName + "." + self.currentToken["text"]

                self.__writeIdentifier(self.currentToken["text"], "subroutine") # subRoutineName
                self.__writeTerminalToken() # (
                nArgs += self.compileExpressionList()
                self.__writeTerminalToken() # )
                self.vmWriter.writeCall(routineName, nArgs)
