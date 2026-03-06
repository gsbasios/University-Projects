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

TOKENS = []
lines = []
token = None
current_index = 0

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
    ext = infile.split('.')[-1]
    if ext != 'c++':
        print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid file extension: {Fore.YELLOW}.{ext}{Fore.RESET} (Did you mean .c++?)")
        sys.exit(1)
        
        
def get_token():
    global current_index
    
    if current_index >= len(TOKENS): return Token("EOF", "EOF", 0, 0)
    else:
        token = TOKENS[current_index]
        current_index += 1
        return token

    
def store_token():
    global current_index
    
    if current_index >= len(TOKENS): return Token("EOF", "EOF", 0, 0)
    else: return TOKENS[current_index]


def word_prediction(word, possibilities):
    word = str(word)
    matches = difflib.get_close_matches(word, possibilities, n=1, cutoff=0.75)
    return matches[0] if matches else None


def get_line_pos(token):
    if token: return token.line_pos
    else: return 0
    
    
def initialize_lines(infile):
    global lines
    
    raw = infile.read().splitlines()
    lines.append("")
    for line in raw:
        l = line.split("//")[0] # REMOVE THE COMMENTS FROM THE ERROR REPORTING
        lines.append(l)
            
    lines.append("")
    infile.seek(0)
    
    
def initialize_colors(args_color):
    if COLORAMA_INSTALLED and not args_color:
        init(autoreset=True)
    else:
        global Fore
        Fore = NoColor()
        
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
    
    return 


def mul_oper():
    global token
    
    next_token = store_token()
    if next_token.token in "*/":
        token = get_token()
    
    return


def add_oper():
    global token
    
    next_token = store_token()
    if next_token.token in "-+":
        token = get_token()
    
    return


def relational_oper():
    global token
    
    next_token = store_token()
    if next_token.category == "RELATIONAL_OP":
        token = get_token()
        
    else:
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected a Relational Operator after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)    
    
    return


def actualparitem():
    global token
    
    next_token = store_token()
    
    if next_token.token == "in":
        token = get_token() # STORES 'in'
        expression()
        
    elif next_token.token == "inout":
        token = get_token() # STORES 'inout'
        next_token = store_token()
        
        if next_token.category != "IDENTIFIER":
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
            
        else: token = get_token() # STORES THE 'ID'
    
    # EMPTY ACTUALPARITEM
    elif next_token.token == ')': return    
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Keywords 'in'/'inout' but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)    
    
    return


def actualparlist():
    global token
    
    actualparitem()
    next_token = store_token() # SHOULD EITHER STORE ',' OR ')'
    
    while next_token.token == ",":
        token = get_token() # CONSUME THE ','
        actualparitem()
        next_token = store_token()
        
    if next_token.token in ["in", "inout"]:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Missing comma ',' before '{next_token.token}'", lines[error.line_counter], error.line_counter, line_pos)    
        
    
    return


def actualpars():
    global token
    
    actualparlist()
    next_token = store_token()
    
    if next_token.token != ")":
        error = next_token
        line_pos = get_line_pos(token) + 1
        report_error(0, f"Expected parenthesis ')' but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)    
    
    else: token = get_token()
    
    return


def idtail():
    global token
    
    next_token = store_token()
    if next_token.token == "(":
        token = get_token()
        next_token = store_token()
        
        if next_token.token in ["in", "inout", ")"]:
            actualpars()  
            # ENTER actualpars() WITH TOKEN STORING THE '('
        
        else:
            error = next_token
            line_pos = get_line_pos(error) - 1
            report_error(0, f"Expected Keywords 'in'/'inout' for parameters, or you misssed an Operator before the parenthesis '('?", lines[error.line_counter], error.line_counter, line_pos)    

    
    return


def factor():
    global token
    
    last = token
    next_token = store_token()
    
    if next_token.category == "INTEGER":
        token = get_token()
        
    elif next_token.token == "(":
        token = get_token()
        expression() 
        next_token = store_token()
        
        if next_token.token == ")": token = get_token()
        
        else:
            error = next_token
            line_pos = get_line_pos(error) - 1
            report_error(0, f"Expected parenthesis ')' but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)      
    
    elif next_token.category == "IDENTIFIER": 
        token = get_token() # STORES 'ID'
        idtail()
        
    else:
        error = last
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Integer, Identifier, or an Expression after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
           
    return


def term():
    global token
    
    factor()
    next_token = store_token() # STORES THE NEXT TOKEN OF 'factor'
    
    while next_token.token in "*/":
        token = next_token
        mul_oper()
        factor()
        next_token = store_token()     
    
    return


def expression():
    global token
    
    optional_sign()           
    term()   
    
    next_token = store_token()
    while next_token.token in "-+":
        token = next_token
        add_oper()
        term()      
        next_token = store_token()   

    return


def boolfactor():
    global token
    
    next_token = store_token()
    
    if next_token.token == "not":
        token = get_token() # STORES '['
        next_token = store_token() # SHOUDL STORE '['
        
        if next_token.token == "[":
            token = get_token() # STORES '['
            
            condition()
            next_token = store_token()
            
            if next_token.token == "]": token = get_token()
            else:
                error = store_token()
                line_pos = get_line_pos(error)
                report_error(0, f"Symbol ']' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)     
            
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '[' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)    
        
    elif next_token.token == "[":
        token = get_token() # STORES '['
        condition()
        next_token = store_token()
        
        if next_token.token == "]": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ']' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)          
        
    else:
        expression()
        relational_oper()
        expression()
        
    
    return


def boolterm():
    global token
    
    next_token = store_token()
    boolfactor()
    
    next_token = store_token()
    
    while next_token.token == "and":
        token = next_token
        next_token = get_token() # STORES 'and'
        boolfactor()
        next_token = store_token()
    
    return


def condition():
    global token
    
    next_token = store_token()
    boolterm()
    
    next_token = store_token()
    
    while next_token.token == "or":
        token = next_token
        next_token = get_token() # STORE 'or'
        boolterm()
        next_token = store_token()  

    return


def return_stat():
    global token
    
    token = get_token()
    expression()
   
    return


def input_stat():
    global token
    
    token = get_token() # STORES 'input'
    next_token = store_token()
    
    if next_token.category == "IDENTIFIER":
        token = get_token()
        
    elif next_token.token == ";":
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"An Identifier was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
    
    return


def print_stat():
    global token
    
    token = get_token()
    expression()
    
    return


def untilcase_stat():
    global token
    
    token = get_token() # STORES 'untilcase'
    next_token = store_token()
    
    while next_token.token == "when":
        next_token = get_token() # STORES 'when'
        token = next_token
        condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)

        statements()
        next_token = store_token()
        
    next_token = store_token()
    if next_token.token == "until":
        next_token = get_token() # STORES 'until'
        token = next_token
        condition()
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'until' was expected to close untilcase after'{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
   
    return


def forcase_stat():
    global token
    
    token = get_token() # STORES 'forcase'
    next_token = store_token()
    
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        next_token = store_token()
        
        if next_token.token == "=":
            token = get_token() # STORES '='
            next_token = store_token()
            
            if next_token.category == "INTEGER":
                token = get_token() # STORES 'INTEGER'
            else:
                error = next_token
                line_pos = get_line_pos(error)
                report_error(0, f"Expected an Integer but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)    
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '=' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    
    next_token = store_token()
    
    while next_token.token == "when":
        next_token = get_token()
        token = next_token
        condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)

        statements()
        next_token = store_token()
        
    return


def incase_stat():
    global token
    
    token = get_token() # STORES 'incase'
    next_token = store_token()
    
    while next_token.token == "when":
        next_token = get_token()
        token = next_token
        condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)

        statements()
        next_token = store_token()
        
    return


def whilecase_stat():
    global token
    
    token = get_token() # STORES 'whilecase'
    
    next_token = store_token()
    while next_token.token == "when":
        next_token = get_token() # STORES 'when'
        token = next_token
        condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)

        statements()
        next_token = store_token()
        
    if next_token.token == "default":
        token = get_token() # STORES 'default'
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
        
        statements()
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'default' was expected to close whilecase after'{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)        
    
    return


def switchcase_stat():
    global token
    
    token = get_token() # STORES 'switchcase'
    next_token = store_token()
    
    while next_token.token == "when":
        next_token = get_token() # STORES 'when'
        token = next_token
        condition()
        
        next_token = store_token()
        
        if next_token.token == ":": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol ':' was expected after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)

        statements()
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
            report_error(0, f"Symbol ':' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
        
        statements()
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'default' was expected to close switchcase after '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
    
    return


def while_stat():
    global token
    
    token = get_token() # STORES 'while'
    condition()
    statements()
    
    return


def elsepart():
    global token
    
    token = get_token() # STORES 'else'
    statements()
    
    return


def if_stat():
    global token
    
    token = get_token() # STORES 'if'
    condition()
    statements()
    
    next_token = store_token()
    
    if next_token.token == "else":
        elsepart()
        
    return


def assignment_stat():
    global token
    
    token = get_token() # STORES ID
    next_token = store_token()
    
    if next_token.token == ":=":
        token = get_token()
        expression()
        
    else:
        error = token
        line_pos = get_line_pos(error)
        
        KEYWORDS = ["if", "else", "while", "switchcase", "whilecase", "incase", "forcase", "untilcase", "print", "input", "return", "declare", "function"]
        next = word_prediction(error.token, KEYWORDS)

        if next:
            report_error(0, f"Unexpected word '{error.token}' came up. Did you mean '{next}'?", lines[error.line_counter], error.line_counter, line_pos)
        else:    
            report_error(0, f"Expected Symbol ':=' after '{error.token}' but got '{next_token.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)

    return


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
            report_error(0, f"Unexpected Keyword '{error.token}' came up where a statement expected!", lines[error.line_counter], error.line_counter, line_pos)           
        
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Expected a statement but got '{error.token}'! Maybe you missed a bracket '['/']'?", lines[error.line_counter], error.line_counter, line_pos)    
    
    return


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
        report_error(0, f"You missed ';' before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
        
    return


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
            report_error(0, f"Symbol '}}' was expected before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)    
    
    else: statement()
    
    return


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
            report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    
    # EMPTY FORMALPARITEMS
    elif next_token.token == ')': return    
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected Keywords 'in'/'inout' but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)    
    
    return


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
        report_error(0, f"Missing comma ',' before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
     
    # EXITS WHILE WITH STORED THE LAST ELEM BEFORE ')'       
    while next_token.token == ",":
        token = get_token()
        formalparitem()
        next_token = store_token()
        
        if next_token.token in ["in", "inout"]:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Missing comma ',' before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
        
    return


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
            report_error(0, f"Expected parenthesis ')' but got '{token.token}' instead!", lines[token.line_counter], token.line_counter, line_pos)
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected parenthesis '(' but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    
    return


def function():
    global token
    
    token = get_token() # STORES 'function'
    
    next_token = store_token()
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        formalpars()
        programblock()
        
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    
    return


def functions():
    global token
        
    next_token = store_token()
    
    while next_token.token == "function":
        token = next_token
        function() # CALLS function() WITHOUT STORING 'function'
        next_token = store_token()

    return


def varlist():
    global token
    
    next_token = store_token() # SHOULD STORE 'ID'
    
    if next_token.category == "IDENTIFIER":
        token = get_token() # STORES 'ID'
        
        next_token = store_token()
        if next_token.category == "IDENTIFIER":
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Missing comma ',' before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
            
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
                    report_error(0, f"Missing comma ',' before '{error.token}'!", lines[error.line_counter], error.line_counter, line_pos)
                    
            else:
                error = next_token
                line_pos = get_line_pos(error)
                report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
        
    elif next_token.token == ";": return
    
    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Expected an Identifier but got {error.category} '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
        
    return


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
            report_error(0, f"Missing ';' after '{error.token}'", lines[error.line_counter], error.line_counter, line_pos)
        
        next_token = store_token()
    
    return 


def programblock():
    global token
    
    next_token = store_token() # SHOULD STORE '{'
    if next_token.token == "{":
        token = get_token() # STORES '{'
        declarations()
        functions()
        statements_sequence()
        
        next_token = store_token() # SHOULD STORE '}'
        
        if next_token.token == "}": token = get_token()
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Symbol '}}' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)        

    else:
        error = next_token
        line_pos = get_line_pos(error)
        report_error(0, f"Symbol '{{' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)        
    
    return 


def program():
    global token
    
    token = get_token() # SHOULD STORE 'program'
    if token.token == "program":
        
        next_token = store_token() # SHOULD STORE 'ID'
        if next_token.category == "IDENTIFIER":
            token = get_token() # STORES 'ID'
            programblock()
            
        else:
            error = next_token
            line_pos = get_line_pos(error)
            report_error(0, f"Program name was expected but got {error.category} '{error.token}' instead! Only Identifier are acceptable!", lines[error.line_counter], error.line_counter, line_pos)
    else:
        error = token
        line_pos = get_line_pos(error)
        report_error(0, f"Keyword 'program' was expected but got '{error.token}' instead!", lines[error.line_counter], error.line_counter, line_pos)
    
    return


def syntax_analyzer():
    global token
    global current_index
    
    current_index = 0

    program()
    
    if store_token().token != "EOF":
        error_token = store_token()
        report_error(0, "Unexpected tokens found after the end of the program!", lines[-1], error_token.line_counter, error_token.line_pos)


    print(f"{Fore.GREEN}Compilation was successful!")
    
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
                
            sys.exit(0)

    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: File {Fore.LIGHTYELLOW_EX}{args.infile}{Fore.RED} was not found in this directory!")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}ERROR: {Fore.RESET}{e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
