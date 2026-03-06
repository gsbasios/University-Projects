program ValidProgram {
    
    // Global declarations
    declare choice, n1, n2, res, dummy;

    // 1. RECURSIVE FUNCTION
    function factorial(in n) {
        declare temp;
        
        if n <= 1 {
            return 1
        } else {
            temp := factorial(in n - 1);
            return n * temp
        }
    }

    // 2. PASS-BY-REFERENCE FUNCTION (INOUT)
    function getGcd(inout a, inout b) {
        while a <> b {
            if a > b {
                a := a - b
            } else {
                b := b - a
            }
        };
        return a
    }

    // 3. COMPLEX LOOPS & CONDITIONS
    function isPrime(in p) {
        declare i, primeFlag, rem;
        
        if p <= 1 {
            return 0
        };
        
        primeFlag := 1;
        i := 2;
        
        // Strict bracketed boolean evaluation
        while [i < p] and [primeFlag = 1] {
            rem := p;
            
            // whilecase testing
            whilecase
                when rem >= i : rem := rem - i
            default : dummy := 0;
            
            // incase testing
            incase
                when rem = 0 : primeFlag := 0;
            
            i := i + 1
        };
        
        return primeFlag
    }

    // MAIN EXECUTION BLOCK
    dummy := 0;
    
    // untilcase testing 
    untilcase
        when choice <= 0 : {
            print 0;
            input choice
        }
    until choice > 0;

    // forcase testing
    forcase dummy = 1
        when choice = 1 : {
            input n1;
            res := factorial(in n1);
            print res
        }
        when choice = 2 : {
            input n1;
            input n2;
            res := getGcd(inout n1, inout n2);
            print res
        }
        when choice = 3 : {
            input n1;
            res := isPrime(in n1);
            
            if res = 1 {
                print 1
            } else {
                print 0
            }
        };

    // switchcase testing
    switchcase
        when choice > 3 : print dummy
    default : print choice
}