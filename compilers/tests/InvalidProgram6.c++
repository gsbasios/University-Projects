program test
{
    declare a, b;
    declare c;

    function increase(in a, inout b)                     
    {
        function useless()
        {
            function anotheruseless()
            {
                print 1  
            }
            print (1+(+2))*3  
        }
        b := a + 1;              
        return a + 10 
    }

    a := 1 ;
    b := 2 + a * a / (2 - a - (2*a));   
    c := increase(in x, in y);
    b := 1;
    while b<10
        if b<>22 or [b>=23 and b<=24]
            b := b+1;     
                          
    input b;
    c := 12 + (+12);

    switchcase                        
        when a=1 : a:=a+1   
        when a=2 : a:=a+2  
        when a=3 : {
                        a:=a+1;
                        a:=a+2  
                    }                       
        default:   a:=a+1  
    ;


    whilecase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1           // ERROR: MISSING SEMICOLON ';'
                        a:=a+2
                   }
        default:   a:=a+1
    ;

    incase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
    ;

    untilcase
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
        until a>100
    ;

    forcase b=10
        when a=1 : a:=a+1
        when a=2 : a:=a+2
        when a=3 : {
                        a:=a+1;
                        a:=a+2
                   }
}