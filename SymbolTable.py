import sys
class SymbolTable :
    def __init__(self):
        self.__table = {}
        self.__varCounts = {            
            "STATIC": 0,
            "FIELD": 0,
            "VAR": 0,
            "ARG": 0
        }
    def startSubroutine(self):
        del self.__table
        self.__table = {}
        self.__varCounts = {
            "STATIC": 0,
            "FIELD": 0,
            "VAR": 0,
            "ARG": 0
        }

    # Add a symbol to symbol table
    # Name: name of symbol
    # type: data type (e.g. String, char, int, $className)
    # kind: scope of symbol (e.g. STATIC, FIELD, ARG, VAR)
    def define(self, name, type, kind):
        self.__table[name] = {
            "type": type,
            "kind": kind,
            "index": self.__incCount(kind)
        }

    # Increments count for kind of var, returns incremented number
    def __incCount(self, kind):
        count = self.__varCounts[kind]
        self.__varCounts[kind] += 1
        return count

    # Gets the count of the kind of variables in table
    def varCount(self, kind):
        return self.__varCounts[kind]
    
    def kindOf(self, name):
        if name in self.__table:
            return self.__table[name]["kind"]
        else:
            return "NONE"
    
    def typeOf(self, name):
        if name in self.__table:
            return self.__table[name]["type"]
        else:
            sys.exit("ERROR: symbol " + name + " is not defined in current scope.")

    # Gets the index of the variable, indexes are separated by kind.
    # Returns -1 if symbol is not found
    def indexOf(self, name):
        if name in self.__table:
            return self.__table[name]["index"]
        else:
            return -1
