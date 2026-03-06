                          CASE++ COMPILER
                  			    version 0.1
                  		 Lex and Syntax Analyzer

1. SYSTEM REQUIREMENTS
- Python 3+
- Dependencies listed in requirements.txt
---

2. INSTALLATION
------------------------------------------------------------------------
To install the necessary library for colored output:
> python3 -m pip install -r requirements.txt

3. USAGE
------------------------------------------------------------------------
Run the compiler from the command line:
> python3 lex-syntax-analyzer.py <filename>.c++ [options]

Options:
    --print-tokens          Display identifying tokens before syntax check
    --no-color              Disable colored output

Note: If colorama is not installed, the program defaults to no-color mode
      automatically

4. TECHNICAL SPECIFICATIONS
------------------------------------------------------------------------
- Integers: 16-bit signed range (-32767 to 32767)
- Identifier Limit: 30 characters (longer names are automatically trimmed)
- Nested Functions: Supports unlimited depth
- Nested Comments: Not allowed and will be treated as syntax error
- Error Handling: Typo-prediction and visual '^' pointer

5. DEVELOPERS INFO
------------------------------------------------------------------------
Developed by: 	BASIOS GEORGIOS, PAPPAS VIKTOR
========================================================================
