import os, sys, re

class JackTokenizer:
    def __init__(self, file):
        self.file = file
        self.__keywords = set(["class","constructor","function","method","field","static","var","int","char","boolean","void","true","false","null","this","let","do","if","else","while","return"])
        self.__symbols = set(["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~"])
        self.__integerRegex = re.compile('[0-9]')
        self.__identifierRegex = re.compile('[0-9A-Za-z_]')
        self.__keywordRegex = re.compile('[a-z]')
        self.__firstChar = ""
        self.__restChars = ""

        self.__symbol = None
        self.__stringVal = None
        self.__intVal = None
        self.__keyword = None
        self.__identifier = None
        self.__tokenType = ""

        self.advance()
        self.advance()
        self.advance()
        self.advance()
        self.advance()
        self.advance()
        self.advance()
        self.advance()

    def __isSymbol(self):
        if self.__firstChar in self.__symbols:
            return True

    def __isStringConstant(self):
        if self.__firstChar == "\"":
            return True
        
    def __isIntConstant(self):
        return self.__integerRegex.match(self.__firstChar)
    
    def __isKeyword(self):
        keywordFound = False
        if len(self.__restChars) == 0:
            self.__restChars = self.file.read(1)
        
        keyword = self.__firstChar + self.__restChars

        # 11 is length of longest keyword
        while len(keyword) < 12:
            next = self.file.read(1)
            if keyword in self.__keywords:
                keywordFound = True
                break
            elif self.__keywordRegex.match(next):
                self.__restChars = self.__restChars + next
                keyword = keyword + next
            else:
                self.file.seek(self.file.tell() - 1,0)
                break

        return keywordFound

    def __isIdentifier(self):
        if self.__integerRegex.match(self.__firstChar):
            return False
        elif self.__identifierRegex.match(self.__firstChar): # Will return true only for [a-zA-Z_]
            return True


    def __getStringFromFile(self):
        stringLiteral = self.__firstChar
        for char in self.__restChars:
            if char == "\"" or char == os.linesep:
                return stringLiteral
            else:
                stringLiteral = stringLiteral + char
        
        next = self.file.read(1)
        self.__restChars = self.__restChars + next
        while next != "\"" and next != os.linesep:
            stringLiteral = stringLiteral + next
            next = self.file.read(1)
            self.__restChars = self.__restChars + next

        return stringLiteral

    def __getIntFromFile(self):
        numberLiteral = self.__firstChar
        for char in self.__restChars:
            if not self.__integerRegex.match(char):
                return int(numberLiteral)
            else:
                numberLiteral = numberLiteral + char

        next = self.file.read(1)
        while self.__integerRegex.match(next):
            numberLiteral = numberLiteral + next
            next = self.file.read(1)
            self.__restChars = self.__restChars + next

        if int(numberLiteral) > 32767:
            sys.exit("ERROR: " + numberLiteral + " outside bounds of acceptable integer values.")
        else:
            return int(numberLiteral)
        
    def __getIdentifierFromFile(self):
        identifier = self.__firstChar + self.__restChars
        
        next = self.file.read(1)
        while self.__identifierRegex.match(next):
            identifier = identifier + next
            self.__restChars = self.__restChars + next
            next = self.file.read(1)
        self.file.seek(self.file.tell() - 1,0) # Go back one
        return identifier


    def __setCurrentToken(self):
        self.__tokenType = ""
        if self.__isSymbol():
            self.__symbol = self.__firstChar
            self.__tokenType = "SYMBOL"
        elif self.__isStringConstant():
            self.__stringVal = self.__getStringFromFile()
            self.__tokenType = "STRING_CONST"
        elif self.__isIntConstant():
            self.__intVal = self.__getIntFromFile()
            self.__tokenType = "INT_CONST"
        elif self.__isKeyword():
            self.__keyword = self.__firstChar + self.__restChars
            self.__tokenType = "KEYWORD"
        elif self.__isIdentifier():
            self.__identifier = self.__getIdentifierFromFile()
            self.__tokenType = "IDENTIFIER"
        else:
            self.__tokenType = "UNKNOWN"
            sys.exit("ERROR: Unknown token type: " + self.__firstChar + self.__restChars)

    def __isComment(self):
        if self.__firstChar == "/":
            if len(self.__restChars) == 0:
                self.__restChars = self.file.read(1)
            
            if self.__restChars[0] == "/":
                return True
            elif self.__restChars[0] == "*":
                return True
            else:
                return False
        else:
            return False
        
    def __seekPastComment(self):
        commentBeginning = self.__firstChar + self.__restChars
        if commentBeginning == "//":
            next = self.file.read(1)
            while next != os.linesep:
                next = self.file.read(1)
        else:
            nextOne = self.file.read(1)
            nextTwo = self.file.read(1)
            endComment = False
            while not endComment:
                if nextOne == "*" and nextTwo == "/":
                    endComment = True
                if nextOne == "":
                    endComment = True # EOF condition
                else:
                    nextOne = nextTwo
                    nextTwo = self.file.read(1)
        


    def advance(self):
        self.__firstChar = self.file.read(1)
        self.__restChars = ""

        if self.__isComment():
            self.__seekPastComment()
            return self.advance()
  
        if self.__firstChar.isspace():
            return self.advance()

        self.__setCurrentToken()
        print(self.__tokenType)

        for x in  [self.__symbol, self.__stringVal, self.__intVal, self.__keyword, self.__identifier]:
            if x is not None:
                print(x)
        self.__symbol = None
        self.__stringVal = None
        self.__intVal = None
        self.__keyword = None
        self.__identifier = None