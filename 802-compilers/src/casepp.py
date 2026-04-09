import os
import sys
import difflib
import argparse

try:
    from colorama import Fore, init
    COLORAMA_INSTALLED = True
except ImportError:
    COLORAMA_INSTALLED = False

# ---------------------------------- GLOBAL VARIABLES ------------------------------------------

OCCUPIED_WORDS = [
                    'program', 'declare', 'and', 'or', 'not', 'if', 'else', 'while', 
                    'switchcase', 'when', 'default', 'whilecase', 'incase', 'untilcase', 
                    'until', 'forcase', 'return', 'print', 'input', 'function', 'in', 'inout'
                 ]

LINES = []                  # a list with the lines of the whole program, used to report errors
TOKENS = []                 # list with the tokens
token = None                # the current token 
T_COUNTER = 0               # counter of temp variables T_i
VAR_LIST = []               # list with all the temp variables
QUAD_LIST = []              # list with all the quads
FILENAME = None             # the base name of the .c++ file
QUAD_COUNTER = 1            # counter of each quad
CURRENT_TOKEN_INDEX = 0     # index inside TOKENS list, used to store and get token

# ------------------------------------ TOKEN AND COLOR CLASSES ---------------------------------------------

class NoColor:
    def __getattribute__(self, name):
        return ""

class Token:
    def __init__(self, category, token, line_counter, line_pos):
        self.category = category
        self.token = token
        self.line_counter = line_counter
        self.line_pos = line_pos

    def __str__(self):
        return f"{Fore.CYAN}{self.token:<30}{Fore.RESET} {Fore.LIGHTMAGENTA_EX}{self.category:<15}{Fore.RESET}{Fore.LIGHTYELLOW_EX}line {self.line_counter}"

# ---------------------------- HELPER METHODS ------------------------------------------------

def report_error(error, message, line, line_number, line_pos):
    if error == 0: error = "SYNTAX ERROR"
    elif error == 1: error = "ILLEGAL SYMBOL"
    elif error == 3: error = "ILLEGAL INTEGER"  
    
    offset = len(line) - len(line.lstrip())
    line = line.lstrip()
    line_pos = line_pos - offset
    
    error_dist = len(f"{error}") + 2
    line_dist = len(f"in line {line_number}")
    maxdist = max(error_dist, line_dist)
    mindist = min(error_dist, line_dist)
    
    print(f"{Fore.RED}{error}: {Fore.RED}{message}")
    print(f"{Fore.LIGHTYELLOW_EX}in line {line_number} {' '*(maxdist -1- mindist)}{line}")
    print(f"{' '*(line_pos+maxdist-1)}{Fore.RED}^")
    
    sys.exit(1)
    

def is_valid_integer(value):
    try:
        integer = int(value)
        if integer >= -32767 and integer <= 32767: return True
        else: return False
    except:
        return False
    
    
def check_extension(infile):
    global FILENAME
    ext = infile.split('.')[-1]
    FILENAME = infile.rsplit('.', 1)[0]
    if ext != 'c++':
        print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid file extension: {Fore.YELLOW}.{ext}{Fore.RESET} (Did you mean .c++?)")
        sys.exit(1)
        
        
def get_token():
    global CURRENT_TOKEN_INDEX
    
    if CURRENT_TOKEN_INDEX >= len(TOKENS): return Token("EOF", "EOF", 0, 0)
    else:
        token = TOKENS[CURRENT_TOKEN_INDEX]
        CURRENT_TOKEN_INDEX += 1
        return token

    
def store_token():
    global CURRENT_TOKEN_INDEX
    
    if CURRENT_TOKEN_INDEX >= len(TOKENS): return Token("EOF", "EOF", 0, 0)
    else: return TOKENS[CURRENT_TOKEN_INDEX]


def word_prediction(word, possibilities):
    word = str(word)
    matches = difflib.get_close_matches(word, possibilities, n=1, cutoff=0.75)
    return matches[0] if matches else None


def get_line_pos(token):
    if token: return token.line_pos
    else: return 0
    
    
def initialize_lines(infile):
    global LINES
    
    raw = infile.read().splitlines()
    LINES.append("")
    for line in raw:
        l = line.split("//")[0] # REMOVE THE COMMENTS FROM THE ERROR REPORTING
        LINES.append(l)
            
    LINES.append("")
    infile.seek(0)
    
    
def initialize_colors(args_color):
    if COLORAMA_INSTALLED and not args_color:
        init(autoreset=True)
    else:
        global Fore
        Fore = NoColor()
        
# ---------------------------- INTERMEDIATE CODE FUNCTIONS AND CLASS ------------------------------------------------

class Quad:
    def __init__(self, label, op, x, y, z):
        self.label = str(label)
        self.op = str(op)
        self.x = str(x)
        self.y = str(y)
        self.z = str(z)
        
    def __str__(self):
        pad = 1
        if QUAD_LIST:
            max_num = QUAD_LIST[-1].label
            pad = len(max_num)
            
        return f"{self.label:<{pad}}: {self.op}, {self.x}, {self.y}, {self.z}"

def newTemp():
    global T_COUNTER, VAR_LIST
    T_COUNTER += 1
    temp = "T_" + str(T_COUNTER)
    VAR_LIST.append(temp)
    return temp
    
def nextQuad():
    return QUAD_COUNTER

def genQuad(op, x, y, z):
    global QUAD_COUNTER, QUAD_LIST
    QUAD_LIST.append(Quad(nextQuad(), op, x, y, z))
    QUAD_COUNTER += 1
    
def emptyList():
    return []

def makeList(label):
    return [label]

def mergeList(list1, list2):
    return list1 + list2

def backpatch(lst, label):
    global QUAD_LIST
    for i in lst:
        if QUAD_LIST[i-1].z != "_":
            print(f"{Fore.RED}ERROR: Quad {QUAD_LIST[i]} has issues!")
            sys.exit(1)
        QUAD_LIST[i-1].z = str(label)
        
def write_int_code(QUAD_LIST):
    outfile = f"{FILENAME}.int"
    
    with open(outfile, "w", encoding="utf-8") as f:
        for q in QUAD_LIST:
            f.write(f"{q}\n")
            
    full_path = os.path.abspath(outfile)
    print(f"{Fore.GREEN}Intermediated code saved to: {full_path}")
        
# ---------------------------- LEX ANALYZER ------------------------------------------------

def lex_analyzer(infile):
    global TOKENS
    line_counter = 1
    word_counter = 0
    token = ""
    line = ""
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
                report_error(0, "IDENTIFIERS starting with Integer cannot contain Alphabetic characters!", line, line_counter, word_counter)
                char = infile.read(1)
            # ELSE PUT THE INTEGER IN THE TOKENS, IF IT'S VALID
            else:
                if is_valid_integer(token):
                    TOKENS.append(Token("INTEGER", token, line_counter, word_counter))
                    token = ""
                    continue
                else:
                    report_error(3, "Integer is out of bounds!", line, line_counter, word_counter)
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
            if len(token) > 30:
                print(f"{Fore.YELLOW}WARNING: Variable '{Fore.CYAN}{token}{Fore.YELLOW}' in {Fore.CYAN}line {line_counter}{Fore.YELLOW} is bigger than 30 characters long")
                print(f"         {Fore.YELLOW}and will be trimmed to 30 as: {Fore.CYAN}{token[:30]}\n")
            token = token[:30]

            if token in OCCUPIED_WORDS:
                TOKENS.append(Token("KEYWORD", token, line_counter, word_counter))
                token = ""
            else:
                TOKENS.append(Token("IDENTIFIER", token, line_counter, word_counter))
                token = ""
            continue
            
        # CHECK MATH OPERATORS
        elif char in "+-*/=": 
            line += char
            word_counter += 1
            
            # CHECK IF IT'S MATH OP OR COMMENT
            if char == "/":
                next_char = infile.read(1)
                
                # IF BLOCK COMMENT STARTED
                if next_char == "*": 
                    line += next_char
                    word_counter += 1
                    comm_line = line_counter
                    prev_char = ""
                    
                    while True:
                        char = infile.read(1)
                        if char == "":
                            first_line = line.split("\n")[0]
                            report_error(0, "Unclosed comment!", first_line, comm_line, word_counter)
                            break
                            
                        line += char
                        word_counter += 1
                        
                        if char == "\n":
                            line_counter += 1
                            line = ""
                            word_counter = 0
                            prev_char = ""
                            
                        elif char == "*" and prev_char == "/":
                            report_error(0, "Nested comments are not allowed!", line, line_counter, word_counter)
                            
                        elif char == "/" and prev_char == "*":
                            char = infile.read(1)
                            break
                        else:
                            prev_char = char
                    continue
                
                # IF LINE COMMENT STARTED
                elif next_char == "/":
                    line += next_char 
                    word_counter += 1
                    prev_char = ""
                    
                    while True:
                        char = infile.read(1)
                        if char == "" or char == "\n":
                            if char == "\n": 
                                line_counter += 1
                                line = ""
                                word_counter = 0
                            char = infile.read(1)
                            break
                            
                        line += char
                        word_counter += 1
                        
                        if char == "*" and prev_char == "/":
                            report_error(0, "Nested comments are not allowed!", line, line_counter, word_counter)
                        elif char == "/" and prev_char == "/":
                            report_error(0, "Nested comments are not allowed!", line, line_counter, word_counter)
                        else:
                            prev_char = char
                    continue
                
                # ELSE IT'S MATH OP
                else:
                    TOKENS.append(Token("MUL_OP", "/", line_counter, word_counter))
                    char = next_char
                    continue
    
            # ADD '+' OR '-' OR '*' OR '='
            if char == "*":
                TOKENS.append(Token("MUL_OP", char, line_counter, word_counter))
                char = infile.read(1)
                continue
            elif char in "+-":
                TOKENS.append(Token("ADD_OP", char, line_counter, word_counter))
                char = infile.read(1)
                continue
            else:
                TOKENS.append(Token("RELATIONAL_OP", char, line_counter, word_counter))
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
                TOKENS.append(Token("RELATIONAL_OP", "<=", line_counter, word_counter))
                char = infile.read(1)
                continue
            elif char == ">":
                TOKENS.append(Token("RELATIONAL_OP", "<>", line_counter, word_counter))
                char = infile.read(1)
                continue
            else:
                TOKENS.append(Token("RELATIONAL_OP", "<", line_counter, word_counter))
                continue
           
        # CHECK '>' SYMBOL 
        elif char == ">":
            line += char
            word_counter += 1
            
            char = infile.read(1)
            line += char
            word_counter += 1
            if char == "=":
                TOKENS.append(Token("RELATIONAL_OP", ">=", line_counter, word_counter))
                char = infile.read(1)
                continue
            else:
                TOKENS.append(Token("RELATIONAL_OP", ">", line_counter, word_counter))
                continue
            
        # CHECK : SYMBOL  
        elif char == ":":
            line += char
            word_counter += 1
            
            next_char = infile.read(1)
            line += next_char
                
            if next_char == "=":
                TOKENS.append(Token("ASSIGN_OP", ":=", line_counter, word_counter))
                char = infile.read(1)
                word_counter += 1
                continue
            else:
                TOKENS.append(Token("COLON", ":", line_counter, word_counter))
                line = line[:-1]
                char = next_char
                continue

        elif char in "()[]{}":
            line += char
            word_counter += 1
            TOKENS.append(Token("GROUP_SYMBOL", char, line_counter, word_counter))
            char = infile.read(1)
            continue

        elif char in ",;":
            line += char
            word_counter += 1
            TOKENS.append(Token("DELIMITER", char, line_counter, word_counter))
            char = infile.read(1)
            continue

        else:
            line += char
            word_counter += 1
            report_error(1, f"Symbol '{char}' doesn't exist in case++", line, line_counter, word_counter)
            char = infile.read(1)
            continue
    
    if TOKENS: TOKENS.append(Token("EOF", "EOF", line_counter + 1, 1))
    return
    
# ---------------------------- SYNTAX ANALYZER ------------------------------------------------

def optional_sign():
    global token
    
    next_token = store_token()
    if next_token.token in "-+":
        token = get_token()    


def mul_oper():
    global token
    
    next_token = store_token()
    if next_token.token in "*/":
        token = get_token()


def add_oper():
    global token
    
    next_token = store_token()
    if next_token.token in "-+":
        token = get_token()


def relational_oper():
    global token
    
    next_token = store_token()
    if next_token.category == "RELATIONAL_OP":
        token = get_token()
        return token.token
        
    else:
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected a Relational Operator after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)    


def actualparitem():
    global token
    
    next_token = store_token()
    
    if next_token.token == "in":
        token = get_token()             # STORES 'in'
        a = expression()                # STORE EXPRESSION RESULT TO VARIABLE FOLLOWING 'in'
        genQuad("par", a, "CV", "_")    # GENERATE 'CV' PARAMETER QUAD
        
    elif next_token.token == "inout":
        token = get_token()             # STORES 'inout'
        next_token = store_token()
        
        if next_token.category != "IDENTIFIER":
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
            
        else: 
            token = get_token()             # STORES THE 'ID'
            b = token.token                 # STORE EXPRESSION RESULT TO VARIABLE FOLLOWING 'inout'
            genQuad("par", b, "REF", "_")   # GENERATE 'REF' PARAMETER QUAD
    
    elif next_token.token == ')': return    # EMPTY ACTUALPARITEM
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Keywords 'in'/'inout' but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)    


def actualparlist():
    global token
    
    actualparitem()
    next_token = store_token()      # SHOULD EITHER STORE ',' OR ')'
    
    while next_token.token == ",":
        token = get_token()         # CONSUME THE ','
        actualparitem()
        next_token = store_token()
        
    if next_token.token in ["in", "inout"]:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Missing comma ',' before '{next_token.token}'", LINES[error.line_counter], error.line_counter, line_pos)    


def actualpars():
    global token
    
    actualparlist()
    next_token = store_token()
    
    if next_token.token != ")":
        error = next_token
        line_pos = get_line_pos(token) + 1
        report_error(0, f"Expected parenthesis ')' but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)    
    
    else: token = get_token()


def idtail():
    global token
    
    token = get_token()             # STORES 'ID'
    name = token.token              # STORE IDENTIFIER
    
    next_token = store_token()
    if next_token.token == "(":     # IF IT'S FUNCTION CALL
        token = get_token()         # STORES '('
        next_token = store_token()
        
        if next_token.token in ["in", "inout"]:
            w = newTemp()                       # CREATE TEMPORARY VAR
            actualpars()                        # ENTER actualpars() WITH TOKEN STORING THE '('
            genQuad("par", w, "RET", "_")       # STORE FUNCTION RESULT TO TEMP VAR
            genQuad("call", name, "_", "_")     # GENERATE FUNCTION CALL QUAD
            return w                            # RETURN FUNCTION RESULT
            
        elif next_token.token == ")":           # EMPTY PARAMETER LIST
            token = get_token()                 # CONSUME THE ')'
            w = newTemp()                       # CREATE TEMPORARY VAR
            genQuad("par", w, "RET", "_")       # STORE FUNCTION RESULT TO TEMP VAR
            genQuad("call", name, "_", "_")     # GENERATE FUNCTION CALL QUAD
            return w                            # RETURN FUNCTION RESULT
        
        else:
            error = next_token
            line_pos = get_line_pos(error) - 1
            report_error(0, f"Expected Keywords 'in'/'inout' for parameters, or you misssed an Operator before the parenthesis '('?", LINES[error.line_counter], error.line_counter, line_pos)    

    return name

def factor():
    global token
    
    last = token
    next_token = store_token()
    
    if next_token.category == "INTEGER":
        token = get_token()
        t1_place = token.token      # IF INTEGER, JUST RETURN IT 
        
    elif next_token.token == "(":
        token = get_token()
        t1_place = expression()     # STORE EXPRESSION RESULT
        next_token = store_token()
        
        if next_token.token == ")": token = get_token()
        
        else:
            error = next_token
            line_pos = get_line_pos(error) - 1
            report_error(0, f"Expected parenthesis ')' but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)      
    
    elif next_token.category == "IDENTIFIER": 
        token = store_token()   # STORES 'ID' WITHOUT CONSUMING
        t1_place = idtail()     # STORE IDTAIL RESULT, FUNCTION RESULT OR AN IDENTIFIER
        
    else:
        error = last
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Integer, Identifier, or an Expression after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)
           
    return t1_place


def term():
    global token
    
    t1_place = factor()                     # STORE T1 RESULT
    next_token = store_token()              # STORES THE NEXT TOKEN OF 'factor'
    
    while next_token.token in "*/":         # STORE OPERATOR ('*' OR '/')
        op = next_token.token
        token = next_token
        mul_oper()
        t2_place = factor()                 # STORE T2 RESULT
        w = newTemp()                       # CREATE TEMPORARY VAR
        genQuad(op, t1_place, t2_place, w)  # GENERATE TERM QUAD, STORE RESULT 
        t1_place = w                        # TO TEMPORARY VAR
        next_token = store_token()          # REPEAT IF MORE EXIST
    
    return t1_place


def expression():
    global token
    
    optional_sign()           
    t1_place = term()                       # STORE T1 RESULT
    
    next_token = store_token()
    while next_token.token in "-+":
        op = next_token.token               # STORE OPERATOR ('+' OR '-')
        token = next_token
        add_oper()              
        t2_place = term()                   # STORE T2 RESULT
        w = newTemp()                       # CREATE TEMPORARY VAR
        genQuad(op, t1_place, t2_place, w)  # GENERATE EXPRESSION QUAD, STORE RESULT 
        t1_place = w                        # TO TEMPORARY VAR
        next_token = store_token()          # REPEAT IF MORE EXIST

    return t1_place


def boolfactor():
    global token
    
    next_token = store_token()
    
    if next_token.token == "not":
        token = get_token()                         # STORES 'not'
        next_token = store_token()                  # SHOULD STORE '['
        
        if next_token.token == "[":
            token = get_token()                     # STORES '['
            
            false_list, true_list = condition()     # IF 'not' KEYWORD, INVERT RESULTS IN TRUE/FALSE LISTS
            next_token = store_token()
            
            if next_token.token == "]": token = get_token()
            else:
                error = store_token()
                line_pos = get_line_pos(error)
                report_error(0, f"Symbol ']' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)     
            
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '[' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)    
        
    elif next_token.token == "[":
        token = get_token()                 # STORES '['
        
        true_list, false_list = condition() # IF NOT 'not', KEEP RESULTS AS IS
        next_token = store_token()
        
        if next_token.token == "]": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ']' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)          
        
    else:
        e1_place = expression()     # STORE E1 RESULT
        op = relational_oper()      # STORE OPERATOR
        e2_place = expression()     # STORE E2 RESULT
        
        true_list = makeList(nextQuad())        # CREATE TRUE LIST
        genQuad(op, e1_place, e2_place, "_")    # GENERATE BOOLFACTOR QUAD
        
        false_list = makeList(nextQuad())       # CREATE FALSE LIST
        genQuad("jump", "_", "_", "_")          # GENERATE JUMP QUAD
                                                # WILL BACKPATCH LATER
    return true_list, false_list


def boolterm():
    global token
    
    true_list, false_list = boolfactor()                    # CREATE TRUE/FALSE LISTS
    
    next_token = store_token()
    while next_token.token == "and":
        backpatch(true_list, nextQuad())                    # BACKPATCH TRUE LIST
        
        token = next_token
        next_token = get_token() # STORES 'and'
        
        true_list2, false_list2 = boolfactor()              # CREATE SECOND BOOLTERM TRUE/FALSE LISTS
                                                            # IF THEY EXIST
        true_list = true_list2                              # BOTH BOOLFACTORS SHOULD BE TRUE
        false_list = mergeList(false_list, false_list2)     # MERGE FALSE LISTS
                                                            # IF ONE IS FALSE, THE RESULT IS FALSE AS WELL
        next_token = store_token()
    
    return true_list, false_list


def condition():
    global token
    
    true_list, false_list = boolterm()                  # CREATE TRUE/FALSE LISTS
    
    next_token = store_token()
    while next_token.token == "or":
        backpatch(false_list, nextQuad())               # BACKPATCH FALSE LIST
        
        token = next_token
        next_token = get_token()                        # STORE 'or'
        
        true_list2, false_list2 = boolterm()            # CREATE SECOND BOOLTERM TRUE/FALSE LISTS
                                                        # IF THEY EXIST
        true_list = mergeList(true_list, true_list2)    # MERGE ALL THE TRUE LISTS
        false_list = false_list2                        # IF SECOND IN FALSE, WE JUST CHECK THE FIRST

        next_token = store_token()  

    return true_list, false_list


def return_stat():
    global token
    
    token = get_token()                     # STORES 'return'
    e_place = expression()                  # STORE EXPRESSION RESULT
    genQuad("retv", e_place, "_", "_")      # GENERATE RETURN QUAD


def input_stat():
    global token
    
    token = get_token() # STORES 'input'
    next_token = store_token()
    
    if next_token.category == "IDENTIFIER":
        token = get_token()
        id_place = token.token                  # STORE IDENTIFIER
        genQuad("inp", id_place, "_", "_")      # GENERATE INPUT QUAD
        
    elif next_token.token == ";":
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"An Identifier was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)


def print_stat():
    global token
    
    token = get_token()                 # STORES 'print'
    e_place = expression()              # STORE EXPRESSION RESULT TO E
    genQuad("out", e_place, "_", "_")   # GENERATE PRINT QUAD


def untilcase_stat():
    global token
    
    token = get_token()                 # STORES 'untilcase'
    
    previous_false_list = emptyList()
    restart_quad = nextQuad()
    
    next_token = store_token()
    while next_token.token == "when":
        next_token = get_token()        # STORES 'when'
        token = next_token

        backpatch(previous_false_list, nextQuad())
        true_list, false_list = condition()
        
        next_token = store_token()
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

        backpatch(true_list, nextQuad())

        statements()
        
        genQuad("jump", "_", "_", restart_quad)
        previous_false_list = false_list
        
        next_token = store_token()
        
    next_token = store_token()
    if next_token.token == "until":
        next_token = get_token()        # STORES 'until'
        token = next_token
        
        backpatch(previous_false_list, nextQuad())
        
        until_true_list, until_false_list = condition()
        
        backpatch(until_false_list, restart_quad)
        backpatch(until_true_list, nextQuad())
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'until' was expected to close untilcase after'{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)


def forcase_stat():
    global token
    
    token = get_token() # STORES 'forcase'
    next_token = store_token()
    
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        id = token.token
        next_token = store_token()
        
        if next_token.token == "=":
            token = get_token() # STORES '='
            next_token = store_token()
            
            if next_token.category == "INTEGER":
                token = get_token() # STORES 'INTEGER'
                integer = token.token
                genQuad(":=", integer, "_", id)
            else:
                error = next_token
                line_pos = get_line_pos(error)
                report_error(0, f"Expected an Integer but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)    
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '=' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
    
    restart_quad = nextQuad()
    
    next_token = store_token()
    while next_token.token == "when":
        next_token = get_token()
        token = next_token
        true_list, false_list = condition()
        backpatch(true_list, nextQuad())
        
        next_token = store_token()
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

        statements()
        
        genQuad("jump", "_", "_", restart_quad)
        backpatch(false_list, nextQuad())
        
        next_token = store_token()


def incase_stat():
    global token
    
    token = get_token() # STORES 'incase'
    
    flag = newTemp()
    restart_quad = nextQuad()
    genQuad(":=", "0", "_", flag)
    
    next_token = store_token()
    while next_token.token == "when":
        next_token = get_token()
        token = next_token

        true_list, false_list = condition()
        backpatch(true_list, nextQuad())
        
        next_token = store_token()
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

        statements()
        
        genQuad(":=", "1", "_", flag)
        backpatch(false_list, nextQuad())

        next_token = store_token()
        
    genQuad("=", flag, "1", restart_quad)


def whilecase_stat():
    global token
    
    token = get_token() # STORES 'whilecase'
    
    previous_false_list = emptyList()
    restart_quad = nextQuad()
    
    next_token = store_token()
    while next_token.token == "when":
        next_token = get_token() # STORES 'when'
        token = next_token
        
        backpatch(previous_false_list, nextQuad())
        true_list, false_list = condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

        backpatch(true_list, nextQuad())
        
        statements()
        
        genQuad("jump", "_", "_", restart_quad)
        previous_false_list = false_list
        
        next_token = store_token()
        
    if next_token.token == "default":
        token = get_token() # STORES 'default'
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
        
        backpatch(previous_false_list, nextQuad())
        statements()
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'default' was expected to close whilecase after'{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)        


def switchcase_stat():
    global token
    
    exit_list = emptyList()             # HOLDS QUADS THAT JUMP OUTSIDE SWITCHCASE
    previous_false_list = emptyList()   # STORES EACH STEP'S PREVIOUS FALSE LIST
    
    token = get_token() # STORES 'switchcase'
    next_token = store_token()
    
    while next_token.token == "when":
        next_token = get_token() # STORES 'when'
        token = next_token
        
        backpatch(previous_false_list, nextQuad())      # IF PREVIOUS CONDITION FAILED, JUMP HERE
        true_list, false_list = condition()             # STORE CONDITION'S RESULTS
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

        backpatch(true_list, nextQuad())            # IF TRUE CONDITION, JUMP HERE AND
        statements()                                # EXECUTE IT'S STATEMENTS
        
        e_quad = makeList(nextQuad())               # CREATE THE EXIT QUAD
        genQuad("jump", "_", "_", "_")              # AND GENERATE JUMP

        exit_list = mergeList(exit_list, e_quad)    # ADD THIS EXIT QUAD TO EXIT LIST
        previous_false_list = false_list            # MAKE THIS FALSE LIST THE PREVIOUS, FOR NEXT LOOP
        
        next_token = store_token()
        
    token = next_token
    next_token = store_token()
        
    if next_token.token == "default":
        token = get_token() # STORES 'default'
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
        
        backpatch(previous_false_list, nextQuad())  # THE LAST FALSE CONDITION WILL JUMP HERE
        statements()                                # AND EXECUTE STATEMENTS OF DEFAULT
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'default' was expected to close switchcase after '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)

    backpatch(exit_list, nextQuad())    # BACKPATCH EXIT LIST TO JUMP OUTSIDE SWITCHCASE


def while_stat():
    global token
    
    token = get_token() # STORES 'while'
    
    b_quad = nextQuad()                     # STORE STARTING LABEL
    true_list, false_list = condition()     # CREATE TRUE/FALSE LISTS
    backpatch(true_list, nextQuad())        # BACKPATCH TRUE LIST
    
    statements()
    
    genQuad("jump", "_", "_", b_quad)       # JUMP TO THE STARTING POSITION TO REEVALUATE
    backpatch(false_list, nextQuad())       # BACKPATCH FALSE LIST


def elsepart():
    global token
    
    token = get_token() # STORES 'else'
    statements()


def if_stat():
    global token
    
    token = get_token()                     # STORES 'if'
    
    true_list, false_list = condition()     # STORE TRUE/FALSE LISTS
    backpatch(true_list, nextQuad())        # BACKPATCH TRUE LIST
    
    statements()
    
    next_token = store_token()
    if next_token.token == "else":
        if_list = makeList(nextQuad())      # IF ELSEPART EXISTS
        genQuad("jump", "_", "_", "_")      # CREATE AND BACKPATCH THE FALSE LIST
        backpatch(false_list, nextQuad())
        
        elsepart()
        backpatch(if_list, nextQuad())      # BACKPATCH AFTER ELSEPART
    else:
        backpatch(false_list, nextQuad())   # IF NO ELSEPART EXISTS, JUST BACKPATCH THE FALSE LIST                                            


def assignment_stat():
    global token
    
    token = get_token() # STORES ID
    assign_var = token.token                        # STORE THE VAR WHERE RESULT WILL BE STORED
    next_token = store_token()
    
    if next_token.token == ":=":
        token = get_token()
        e_place = expression()                      # STORE EXPRESSSION RESULT
        genQuad(":=", e_place, "_", assign_var)     # AND CREATE THE ASSIGNMENT QUAD
        
    else:
        error = token
        line_pos = get_line_pos(error)
        
        KEYWORDS = ["if", "else", "while", "switchcase", "whilecase", "incase", "forcase", "untilcase", "print", "input", "return", "declare", "function"]
        next = word_prediction(error.token, KEYWORDS)

        if next:
            report_error(0, f"Unexpected word '{error.token}' came up. Did you mean '{next}'?", LINES[error.line_counter], error.line_counter, line_pos)
        else:    
            report_error(0, f"Expected Symbol ':=' after '{error.token}' but got '{next_token.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)


def statement():
    global token
    
    next_token = store_token() # SHOULD STORE A STATEMENT KEYWORD
    
    if next_token.token == "if":
        token = next_token
        if_stat()
    
    elif next_token.token == "while":
        token = next_token
        while_stat()
    
    elif next_token.token == "switchcase":
        token = next_token
        switchcase_stat()
        
    elif next_token.token == "whilecase":
        token = next_token
        whilecase_stat()
        
    elif next_token.token == "incase":
        token = next_token
        incase_stat()
        
    elif next_token.token == "forcase":
        token = next_token
        forcase_stat()
        
    elif next_token.token == "untilcase":
        token = next_token
        untilcase_stat()
        
    elif next_token.token == "print":
        token = next_token
        print_stat()

    elif next_token.token == "input":
        input_stat()   
    
    elif next_token.token == "return":
        token = next_token
        return_stat()
        
    else:
        if next_token.category == "IDENTIFIER":
            token = next_token
            assignment_stat()
        
        elif next_token.category == "KEYWORD":
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Unexpected Keyword '{error.token}' came up where a statement expected!", LINES[error.line_counter], error.line_counter, line_pos)           
        
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Expected a statement but got '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)    


def statements_sequence():
    global token
    
    next_token = store_token()
    if next_token.token == "}":
        return
    
    statement()

    next_token = store_token()
    while next_token.token == ";":
        next_token = get_token()
        token = next_token
        statement()
        next_token = store_token()
      
    token = next_token
    if token.token not in ["}", "EOF", "default", "until", "when", "else"]:
        error = token
        line_pos = get_line_pos(error) - len(error.token) + 1
        report_error(0, f"You missed ';' before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)


def statements():
    global token
    
    next_token = store_token()
    if next_token.token == "{":
        token = get_token() # CONSUME THE '{'
        statements_sequence()
        
        next_token = store_token()
        
        if next_token.token == "}":
            token = get_token()
            
        else:
            error = token
            line_pos = get_line_pos(error) - len(error.token) + 1
            report_error(0, f"Symbol '}}' was expected before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)    
    
    else: statement()


def formalparitem():
    global token
    
    next_token = store_token()
    
    if next_token.token == "in" or next_token.token == "inout":
        token = get_token() # STORES 'in' OR 'inout'
        next_token = store_token()
        
        if next_token.category == "IDENTIFIER":
            token = get_token() # STORES 'ID'
            
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
    
    # EMPTY FORMALPARITEMS
    elif next_token.token == ')': return    
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Keywords 'in'/'inout' but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)    


def formalparlist():
    global token
    
    token = store_token()
    
    # EMPTY LIST
    if token.token == ")": return
    
    formalparitem()
    next_token = store_token()
        
    if next_token.token in ["in", "inout"]:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Missing comma ',' before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)
     
    # EXITS WHILE WITH STORED THE LAST ELEM BEFORE ')'       
    while next_token.token == ",":
        token = get_token()
        formalparitem()
        next_token = store_token()
        
        if next_token.token in ["in", "inout"]:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Missing comma ',' before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)


def formalpars():
    global token
    
    next_token = store_token() # SHOULD STORE '('
    
    if next_token.token == "(":
        token = get_token() # STORES '('
        formalparlist()
        
        next_token = store_token()
        
        if next_token.token == ")": token = get_token()
        else:
            token = next_token
            line_pos = get_line_pos(token)
            report_error(0, f"Expected parenthesis ')' but got '{token.token}' instead!", LINES[token.line_counter], token.line_counter, line_pos)
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected parenthesis '(' but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)


def function():
    global token
    
    token = get_token() # STORES 'function'
    
    next_token = store_token()
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        func_name = token.token
        formalpars()
        programblock(func_name, is_main=False)
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)


def functions():
    global token
        
    next_token = store_token()
    
    while next_token.token == "function":
        token = next_token
        function() # CALLS function() WITHOUT STORING 'function'
        next_token = store_token()


def varlist():
    global token
    
    next_token = store_token() # SHOULD STORE 'ID'
    
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        
        next_token = store_token()
        if next_token.category == "IDENTIFIER":
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Missing comma ',' before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)
            
        while store_token().token == ",":
            next_token = get_token()
            token = next_token
            
            next_token = store_token()
                
            if next_token.category == "IDENTIFIER": 
                token = get_token() # STORES ID
                next_token = store_token()
                
                if next_token.category == "IDENTIFIER":
                    error = next_token
                    line_pos = get_line_pos(error)
                    report_error(0, f"Missing comma ',' before '{error.token}'!", LINES[error.line_counter], error.line_counter, line_pos)
                    
            else:
                error = next_token
                line_pos = get_line_pos(error)
                report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)
        
    elif next_token.token == ";": return
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)


def declarations():
    global token
    
    next_token = store_token()
    while next_token.token == "declare":
        next_token = get_token() # STORES 'declare'
        token = next_token
        varlist()

        next_token = store_token()
        if next_token.token == ";": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Missing ';' after '{error.token}'", LINES[error.line_counter], error.line_counter, line_pos)
        
        next_token = store_token() 


def programblock(name, is_main):
    global token
    
    next_token = store_token()      # SHOULD STORE '{'
    if next_token.token == "{":
        token = get_token()         # STORES '{'
        declarations()              # CHECK DECLARATIONS
        functions()                 # CHECK FUNCTIONS
        genQuad("begin_block", name, "_", "_")      # GENERATE BLOCK BEGIN QUAD
        statements_sequence()
        if is_main:                                 # ONLY 'halt' IF MAIN PROGRAM CALLED
            genQuad("halt", "_", "_", "_")          # GENERATE HALT QUAD
        genQuad("end_block", name, "_", "_")        # GENERATE BLOCK END QUAD
        
        next_token = store_token()                  # SHOULD STORE '}'
        
        if next_token.token == "}": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '}}' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)        

    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Symbol '{{' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)        


def program():
    global token
    
    token = get_token()             # SHOULD STORE 'program'
    if token.token == "program":
        
        next_token = store_token()                  # SHOULD STORE 'ID'
        if next_token.category == "IDENTIFIER":
            token = get_token()                     # STORES 'ID'
            prog_name = token.token                 # STORE PROGRAM'S NAME
            programblock(prog_name, is_main=True)   # PASS IT TO PROGRAM BLOCK
            
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Program name was expected but got {error.category} '{error.token}' instead! Only Identifier are acceptable!", LINES[error.line_counter], error.line_counter, line_pos)
    else:
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'program' was expected but got '{error.token}' instead!", LINES[error.line_counter], error.line_counter, line_pos)


def syntax_analyzer():
    global token
    global CURRENT_TOKEN_INDEX
    
    CURRENT_TOKEN_INDEX = 0

    program()
    
    if store_token().token != "EOF":
        error_token = store_token()
        report_error(0, "Unexpected tokens found after the end of the program!", LINES[-1], error_token.line_counter, error_token.line_pos)

    #print(f"{Fore.GREEN}Compilation was successful!")
    
# ---------------------------------------- MAIN ------------------------------------------------ 

def main():
    parser = argparse.ArgumentParser(description="CASE++ Compiler: Turn your .c++ programs into executable (RISC-V ARCH)")
    parser.add_argument("infile", help="The filename of your .c++ program")
    parser.add_argument("--print-tokens", action="store_true", help="Print all the tokens that were saved from the lex analyzer")
    parser.add_argument("--no-color", action="store_true", help="Use this flag if you can't install colorama, or you just don't want colors")
    args = parser.parse_args()

    try:
        # USING UTF-8 TO SUCCESSFULLY READ CHARS LIKE GREEK ETC
        with open(args.infile, "r", encoding="utf-8") as infile:
            check_extension(args.infile)

            # INITIALIZE THE LINES TO PRINT ERRORS
            initialize_lines(infile)
            
            # INITIALIZE COLORING FEATURES
            args_color = args.no_color
            initialize_colors(args_color)
                
            # RUN LEX_ANALYZER
            lex_analyzer(infile)
            
            # PRINT ALL FLAG
            if args.print_tokens: 
                for t in TOKENS: 
                    print(t)

            # RUN SYNTAX_ANALYZER
            syntax_analyzer()

            # WRITE INT CODE TO FILE
            write_int_code(QUAD_LIST)
                
            sys.exit(0)

    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: File {Fore.LIGHTYELLOW_EX}{args.infile}{Fore.RED} was not found in this directory!")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}ERROR: {Fore.RESET}{e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
