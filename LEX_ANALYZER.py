# PAPPAS VIKTOR 5327
# GEORGIOS MPASIOS 5050

import sys
import argparse
from colorama import Fore, init

# AUTORESET OF COLORS
init(autoreset=True)

OCCUPIED_WORDS = [
                    'program', 'declare', 'and', 'or', 'not', 'if', 'else', 'while', 
                    'switchcase', 'when', 'default', 'whilecase', 'incase', 'untilcase', 
                    'until', 'forcase', 'return', 'print', 'input', 'function', 'in', 'inout'
                 ]

class Token:
    def __init__(self, category, token, line_counter):
        self.category = category
        self.token = token
        self.line_counter = line_counter

    def __str__(self):
        return f"{Fore.CYAN}{self.token:<30}{Fore.RESET} {Fore.LIGHTMAGENTA_EX}{self.category:<15}{Fore.RESET}{Fore.LIGHTYELLOW_EX}line {self.line_counter}"

# ------------------------------- HELPER METHODS ---------------------------------------------
def report_error(error, message, line, line_number, line_pos, show_all):
    if error == 0: error = "SYNTAX ERROR"
    elif error == 1: error = "ILLEGAL SYMBOL"
    elif error == 3: error = "ILLEGAL INTEGER"
    
    error_dist = len(f"{error}") + 2
    line_dist = len(f"in line {line_number}")
    maxdist = max(error_dist, line_dist)
    mindist = min(error_dist, line_dist)
    
    print(f"{Fore.RED}{error}: {Fore.RED}{message}")
    print(f"in line {line_number}:{' '*(maxdist -1- mindist)}{line}")
    print(f"{' '*(line_pos+maxdist-1)}{Fore.RED}^")
    
    if not show_all: sys.exit(0)
    return 1

def is_valid_integer(value):
    try:
        integer = int(value)
        if integer >= -32767 and integer <= 32767: return True
        else: return False
    except:
        return False
    
def check_extension(infile):
    ext = infile.split('.')[-1]
    if ext != 'c++':
        print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid file extension: {Fore.YELLOW}.{ext}{Fore.RESET} (Did you mean .c++?)")
        sys.exit(0)
        
# ------------------------------- LEX ANALYZER --------------------------------------------- 
def lex_analyzer(infile, show_all=False):
    TOKENS = []
    
    line_counter = 1
    word_counter = 0
    token = ""
    line = ""
    errors = 0
    char = infile.read(1)
    
    # IF char == "" WE REACHED THE END OF FILE
    while char != "": 
         
        # CHECK SPACES AND NEW LINES
        if char.isspace():
            if char == "\n": 
                line_counter +=1
                line = ""
                word_counter = 0
            else:   
                word_counter += 1
                line += char
            char = infile.read(1)
            continue

        # CHECK INTEGERS
        elif char.isdigit():
            token = ""
            # CREATE THE INTEGER
            while char.isdigit():
                token += char
                line += char
                word_counter += 1
                char = infile.read(1)
            
            # THROW ERROR IF ALPHABETICAL CHARACTER COMES UP
            if char.isalpha():
                line += char
                word_counter += 1
                errors += report_error(0, "Identifiers starting with Integer cannot contain Alphabetic characters!", line, line_counter, word_counter, show_all)
                char = infile.read(1)
            # ELSE PUT THE INTEGER IN THE TOKENS, IF IT'S VALID
            else:
                if is_valid_integer(token):
                    integer = int(token)
                    TOKENS.append(Token("INTEGER", integer, line_counter))
                    token = ""
                    continue
                else:
                    errors += report_error(3, "Integer is out of bounds!", line, line_counter, word_counter, show_all)
                    continue

        # CHECK ALPHANUMERICALS
        elif char.isalpha():
            token = ""
            while char.isalnum():
                token += char
                line += char
                char = infile.read(1)
                word_counter += 1

            # LIMIT TO 30 CHARACTERS
            token = token[:30]

            if token in OCCUPIED_WORDS:
                TOKENS.append(Token("KEYWORD", token, line_counter))
                token = ""
            else:
                TOKENS.append(Token("IDENTIFIER", token, line_counter))
                token = ""
            continue
            
        # CHECK MATH OPERATORS
        elif char in "+-*/=": 
            line += char
            word_counter += 1
            
            # CHECK IF IT'S MATH OP OR COMMENT
            if char == "/":
                next_char = infile.read(1)
                line += next_char
                word_counter += 1
                
                # IF BLOCK COMMENT STARTED
                if next_char == "*": 
                    comm_line = line_counter
                    while True:
                        char = infile.read(1)
                        line += char
                        
                        # IF EOF
                        if char == "":
                            first_line = line.split("\n")[0]
                            errors += report_error(0, "Unclosed comment!", first_line, comm_line, word_counter, show_all)
                            break
                            
                        # IF NEW LINE
                        elif char == "\n":
                            line_counter += 1
                            
                        # IF '*' CHECK IF IT'S COMMENT CLOSURE
                        elif char == "*":
                            next_c = infile.read(1)
                            line += next_c
                            
                            # IF IT'S COMMENT CLOSURE, MOVE UP AND CHECK NEXT
                            if next_c == "/":
                                char = infile.read(1)
                                break
             
                            elif next_c == "\n":
                                line_counter += 1
                    continue
                
                # IF LINE COMMENT STARTED
                elif next_char == "/":
                    line = "" 
                    # SKIP THIS LINE
                    while char != "\n" and char != "":
                        char = infile.read(1)
                        
                    # CHECK NEXT WHEN LINE FINISHED
                    if char == "\n": 
                        line = ""
                        word_counter = 0
                        line_counter += 1
                    char = infile.read(1) 
                    continue
                
                # ELSE IT'S MATH OP
                else:
                    TOKENS.append(Token("MATHS_OP", "/", line_counter))
                    char = next_char
                    continue
    
            # ADD '+' OR '-' OR '*' OR '='
            TOKENS.append(Token("MATHS_OP", char, line_counter))
            char = infile.read(1)
            continue

        # CHECK '<' SYMBOL
        elif char == "<":
            line += char
            word_counter += 1
            
            char = infile.read(1)
            line += char
            word_counter += 1
            if char == "=":
                TOKENS.append(Token("BINARY_OP", "<=", line_counter))
                char = infile.read(1)
                continue
            elif char == ">":
                TOKENS.append(Token("BINARY_OP", "<>", line_counter))
                char = infile.read(1)
                continue
            else:
                TOKENS.append(Token("BINARY_OP", "<", line_counter))
                continue
           
        # CHECK '>' SYMBOL 
        elif char == ">":
            line += char
            word_counter += 1
            
            char = infile.read(1)
            line += char
            word_counter += 1
            if char == "=":
                TOKENS.append(Token("BINARY_OP", ">=", line_counter))
                char = infile.read(1)
                continue
            else:
                TOKENS.append(Token("BINARY_OP", ">", line_counter))
                continue
            
        # CHECK : SYMBOL  
        elif char == ":":
            line += char
            word_counter += 1
            
            next_char = infile.read(1)
            line += next_char
            
            if next_char == "=":
                TOKENS.append(Token("ASSIGN_OP", ":=", line_counter))
                char = infile.read(1)
                word_counter += 1
                continue
            else:
                errors += report_error(1, "Expected '=' after ':'. Did you mean ':='?", line, line_counter, word_counter, show_all)
                line = line[:-1]
                char = next_char
                continue

        elif char in "()[]{}":
            TOKENS.append(Token("GROUP_SYMBOL", char, line_counter))
            char = infile.read(1)
            continue

        elif char in ",;":
            TOKENS.append(Token("DELIMITER", char, line_counter))
            char = infile.read(1)
            continue

        else:
            line += char
            word_counter += 1
            errors += report_error(1, f"Symbol '{char}' doesn't exist in case++", line, line_counter, word_counter, show_all)
            char = infile.read(1)
            continue
     
    if errors != 0: print(f"{Fore.RED}TOTAL ERRORS: {errors}\n") # ONLY PRINT ERRORS COUNT IF ERRORS EXIST
    else: return TOKENS # ONLY RETURN TOKENS IF NO ERRORS OCCUR


def main():
    parser = argparse.ArgumentParser(description="CASE++ Compiler: Turn your .c++ programs in executable (RISC-V ARCH)")
    parser.add_argument("infile", help="The filename of your .c++ program")
    parser.add_argument("-all", "--all-errors", action="store_true", help="Show all errors instead of stopping in the first")
    args = parser.parse_args()

    try:
        with open(args.infile, "r", encoding="utf-8") as infile:
            check_extension(args.infile)
            tokens = lex_analyzer(infile, args.all_errors)
            if tokens:
                for token in tokens:
                    print(token)
            else:
                print(f"{Fore.YELLOW}ERROR OCCURED, TOKENS MATRIX IS EMPTY")    
            
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: {Fore.RESET}File {args.infile} was not found in this directory!")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}ERROR: {Fore.RESET}{e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
