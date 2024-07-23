import sys, os, re
import JackTokenizer
def main():

    # Initialize environment
    if len(sys.argv) < 2:
        sys.exit("ERROR: No Jack file specified")

    workingDirectory = os.getcwd()
    filePath = sys.argv[1]
    jackFiles = []
    # Get jack files
    if os.path.isdir(filePath):
        dirContents = os.listdir(filePath)
        for file in dirContents:
            if file.endswith(".jack"):
                jackFiles.append(os.path.join(workingDirectory, filePath, file))
        
    else:
        jackFiles.append(os.path.join(workingDirectory, filePath))
    
    

    for item in jackFiles:
        file = open(item, 'r', encoding="utf-8")
        outFilePath = re.sub('.jack$','.xml', item)
        outFile = open(outFilePath, 'w', encoding="utf-8")
        tokenizer = JackTokenizer.JackTokenizer(file)

        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            if tokenizer.tokenType() == "SYMBOL":
                outFile.write("<symbol>" + tokenizer.symbol() + "</symbol>" + os.linesep)
            elif tokenizer.tokenType() == "STRING_CONST":
                outFile.write("<stringConstant>" + tokenizer.stringVal() + "</stringConstant>" + os.linesep)
            elif tokenizer.tokenType() == "INT_CONST":
                outFile.write("<integerConstant>" + str(tokenizer.intVal()) + "</integerConstant>" + os.linesep)
            elif tokenizer.tokenType() == "KEYWORD":
                outFile.write("<keyword>" + tokenizer.keyword() + "</keyword>" + os.linesep)
            elif tokenizer.tokenType() == "IDENTIFIER":
                outFile.write("<identifier>" + tokenizer.identifier() + "</identifier>" + os.linesep)
            elif tokenizer.tokenType() == "EOF":
                continue
            else:
                sys.exit("ERROR: unknown token type " + tokenizer.tokenType())
        file.close()
        outFile.close()


main()
