# CASE++ COMPILER | version 0.1 - Lex and Syntax Analyzer

## SYSTEM REQUIREMENTS
- Python 3+
- Dependencies listed in requirements.txt

## INSTALLATION
To install the necessary library for colored output:
```
python3 -m pip install -r requirements.txt
```

## USAGE
```
> python3 lex-syntax-analyzer.py <filename>.c++ [options]

Options:
    --print-tokens          Display identifying tokens before syntax check
    --no-color              Disable colored output
```
***Note:*** *If colorama is not installed, the program defaults to no-color mode
      automatically*

## TECHNICAL SPECIFICATIONS
- Integers: 16-bit signed range (-32767 to 32767)
- Identifier Limit: 30 characters (longer names are automatically trimmed)
- Nested Functions: Supports unlimited depth
- Nested Comments: Not allowed and will be treated as syntax error
- Error Handling: Typo-prediction and visual '^' pointer

## DEVELOPERS INFO
***Developed by:*** 	
- BASIOS GEORGIOS
- PAPPAS VIKTOR
