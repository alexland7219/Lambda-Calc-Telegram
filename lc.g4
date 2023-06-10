grammar lc;

root : (macro | term) EOF
	;

macro : (NAME|OP) ASSIGN term 
      ;

term : '(' term ')'                          # paren 
     | term term                             # application
     | LETTER                                # letter
     | LAMBDA (LETTER)+ '.' term             # abstract
     | (NAME|OP)                             # macroTerm 
     ;

LETTER : ('a' .. 'z') ;
LAMBDA : ('λ' | '\\') ;
WS   : [ \t\n\r]+ -> skip ;
ASSIGN : ('=' | '≡' ) ;
NAME : ('A' .. 'Z') ( ('a'..'z') | ('A' .. 'Z') | ('0' .. '9') )* ;
OP   : ~[a-zA-Z=\\] ;