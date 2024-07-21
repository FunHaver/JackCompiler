import sys, os
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
    
    

    for filePath in jackFiles:
        file = open(filePath, 'r', encoding="utf-8")
        tokenizer = JackTokenizer.JackTokenizer(file)


        file.close()


main()
