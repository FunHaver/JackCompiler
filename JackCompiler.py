import sys, os, re
import JackTokenizer, CompilationEngine
from xml.sax.saxutils import escape

def main():

    # Initialize environment
    if len(sys.argv) < 2:
        sys.exit("ERROR: No Jack file specified")

    workingDirectory = os.getcwd()
    filePath = sys.argv[1]
    jackFiles = []
    symbolFiles = []
    # Get jack files
    if os.path.isdir(filePath):
        dirContents = os.listdir(filePath)
        for file in dirContents:
            if file.endswith(".jack"):
                jackFiles.append(os.path.join(workingDirectory, filePath, file))
        
    else:
        jackFiles.append(os.path.join(workingDirectory, filePath))
    
    
    # Tokenize
    for item in jackFiles:
        file = open(item, 'r', encoding="utf-8")
        symbolFilePath = re.sub('.jack$','T.xml', item)
        symbolFile = open(symbolFilePath, 'w', encoding="utf-8")
        symbolFiles.append(symbolFilePath)
        symbolFile.write("<tokens>" + os.linesep)
        tokenizer = JackTokenizer.JackTokenizer(file)
        symbolFilePath.split(os.pathsep)
        while tokenizer.hasMoreTokens():
            tag = ""
            value = ""
            tokenizer.advance()
            if tokenizer.tokenType() == "SYMBOL":
                tag = "symbol"
                value = tokenizer.symbol()
            elif tokenizer.tokenType() == "STRING_CONST":
                tag = "stringConstant"
                value = tokenizer.stringVal()
            elif tokenizer.tokenType() == "INT_CONST":
                tag = "integerConstant"
                value = str(tokenizer.intVal())
            elif tokenizer.tokenType() == "KEYWORD":
                tag = "keyword"
                value = tokenizer.keyword()
            elif tokenizer.tokenType() == "IDENTIFIER":
                tag = "identifier"
                value = tokenizer.identifier()
            elif tokenizer.tokenType() == "EOF":
                continue
            else:
                sys.exit("ERROR: unknown token type " + tokenizer.tokenType())

            symbolFile.write("<" + tag + "> " + escape(value) + " </" + tag + ">" + os.linesep)
        file.close()
        symbolFile.write("</tokens>" + os.linesep)
        symbolFile.close()

    #compile
    for tempFile in symbolFiles:
        tokenFile = open(tempFile, 'r', encoding="utf-8")
        compiledFilePath = re.sub('T.xml$', '.vm', tempFile)
        compiledFile = open(compiledFilePath, 'w', encoding="utf-8")
        compilationEngine = CompilationEngine.CompilationEngine(tokenFile, compiledFile)
        compilationEngine.compileClass()




        file.close()
        compiledFile.close()

main()
