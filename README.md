# JackCompiler

A Python implementation of the JACK Compiler for the JACK programming language. Specified in NAND2TETRIS projects 10 and 11.

This program reads files containing Jack code specified in Part 2 of the NAND2TETRIS course and outputs a VM "bytecode" file for each Jack file. The VM language is specified in NAND2TETRIS Part 2.

## Usage
**System Requirements**
 * Python 3.x
 * git

To use this compiler, first you must have a file or files written in the Jack programming language specified in the nand2tetris book.

Some example files are provided in the test_jack_files directory.

First, clone this repository
```bash
git clone https://github.com/FunHaver/JackCompiler
```

Then, execute the JackCompiler.py file found in the repository's root directory. This program takes one argument, either:
1. The location of the Jack file to be translated.
2. The location of the directory containing multiple Jack files to be translated. (Note: this program does not support sub-directories)

Example execution
```bash
cd JackCompiler
python3 JackCompiler.py test_jack_files/Project11/Pong
```

The resulting .vm files will be written to the same directory specified in the command line argument.

## Running the .vm files
Now that you are in posession of a HACK assembly file, it can be tested via the VM tool, which will interpret the file(s), provided by the NAND2TETRIS course located here: https://nand2tetris.github.io/web-ide/vm. 

Or it can be fed into the course's toolchain as follows:
1. Feed all VM files into a VM Translator [like this one](https://github.com/FunHaver/VmTranslator). It will produce one HACK file written in assembly.
2. Feed that assembly file to a HACK assembler [like this one](https://github.com/FunHaver/HackAssembler). That will produce a "binary file" (actually a utf-8 encoded file of 16-digit strings) that can be executed on the hack platform.
3. You may use the CPU emulator tool here: https://nand2tetris.github.io/web-ide/cpu to execute the binary. Both options provide the same result.