grammar hackasm;

hackasm: (WS* inst_or_label? WS* COMMENT? NEWLINE)* inst_or_label? WS* COMMENT? EOF
       ;

inst_or_label: inst
             | label
             ;

inst: ainst | cinst;
ainst: '@' ainst_arg ;

ainst_arg   : pre_defined_syms 
            | other_syms  // symbol name other than defined_syms
            | ainst_number             
{
if int(self.Ainst_numberContext.getText(localctx)) > 32767:
    class OutOfRageException(Exception):
        def __init__(self, msg: str) -> None: ...
    raise OutOfRageException(self)
}
            ;
pre_defined_syms: def_syms;
other_syms: reg_syms
          | reg_mult_syms
          | jmp_syms
          | SYMBOLNAME
          ;

ainst_number: number;
number: (ZERO | ONE | DIGIT)+;

reg_syms: reg_syms_A | reg_syms_D | reg_syms_M;
reg_syms_A: REG_A; 
reg_syms_D: REG_D; 
reg_syms_M: MEM_M; 

reg_mult_syms: REG_AD | REG_AM | REG_MD | REG_AMD ;

def_syms: def_syms_sp | def_syms_lcl | def_syms_arg
        | def_syms_this | def_syms_that | def_syms_rx
        | def_syms_screen | def_syms_kbd;
def_syms_sp: DEF_SP;
def_syms_lcl: DEF_LCL;
def_syms_arg: DEF_ARG;
def_syms_this: DEF_THIS;
def_syms_that: DEF_THAT;
def_syms_rx: DEF_R0 | DEF_R1 | DEF_R2 | DEF_R3
           | DEF_R4 | DEF_R5 | DEF_R6 | DEF_R7
           | DEF_R8 | DEF_R9 | DEF_R10 | DEF_R11
           | DEF_R12 | DEF_R13 | DEF_R14 | DEF_R15;
def_syms_screen: DEF_SCREEN;
def_syms_kbd: DEF_KBD;


cinst: (dest WS* EQ WS* )? WS* comp WS* jump? ;

dest: MEM_M | REG_D | REG_MD | REG_A | REG_AM | REG_AD | REG_AMD;
    
//comp: comp_not? comp_1st_operand WS* (comp_op WS* comp_2nd_operand)?;
//comp_not: NOT;
//comp_1st_operand: ZERO | ONE | (MINUS ONE) 
//                | REG_A | M_REG_A 
//                | REG_D | M_REG_D
//                | MEM_M | M_MEM_M
//                ; 
//comp_op: PLUS | MINUS | AND | OR ;
//comp_2nd_operand: ONE
//                | REG_A
//                | REG_D
//                | MEM_M
//                ;

comp:    comp_a0_zero
       | comp_a0_one
       | comp_a0_minus_one
       | comp_a0_D
       | comp_a0_A
       | comp_a0_not_D
       | cmop_a0_not_A
       | comp_a0_minus_D
       | comp_a0_minus_A
       | comp_a0_D_plus_one
       | comp_a0_A_plus_one
       | comp_a0_D_minus_one
       | comp_a0_A_minus_one
       | comp_a0_D_plus_A
       | comp_a0_D_minus_A
       | comp_a0_A_minus_D
       | comp_a0_D_and_A
       | comp_a0_D_or_A
       | comp_a1_M 
       | comp_a1_not_M 
       | comp_a1_minus_M  
       | comp_a1_M_plus_one 
       | comp_a1_M_minus_one
       | comp_a1_D_plus_M 
       | comp_a1_D_minus_M
       | comp_a1_M_minus_D 
       | comp_a1_D_and_M
       | comp_a1_D_or_M
       ;
comp_a0_zero: ZERO;
comp_a0_one: ONE;
comp_a0_minus_one: MINUS ONE;
comp_a0_D: REG_D;
comp_a0_A: REG_A;
comp_a0_not_D: NOT REG_D;
cmop_a0_not_A: NOT REG_A;
comp_a0_minus_D: MINUS REG_D;
comp_a0_minus_A: MINUS REG_A;
comp_a0_D_plus_one: REG_D WS* PLUS WS* ONE;
comp_a0_A_plus_one: REG_A WS* PLUS WS* ONE;
comp_a0_D_minus_one: REG_D WS* MINUS WS* ONE;
comp_a0_A_minus_one: REG_A WS* MINUS WS* ONE;
comp_a0_D_plus_A: REG_D WS* PLUS WS* REG_A;
comp_a0_D_minus_A: REG_D WS* MINUS WS* REG_A;
comp_a0_A_minus_D: REG_A WS* MINUS WS* REG_D;
comp_a0_D_and_A: REG_D WS* AND WS* REG_A;
comp_a0_D_or_A: REG_D WS* OR WS* REG_A;
comp_a1_M: MEM_M;
comp_a1_not_M: NOT MEM_M; 
comp_a1_minus_M: WS* MINUS WS* MEM_M;  
comp_a1_M_plus_one: MEM_M WS* PLUS WS* ONE;
comp_a1_M_minus_one: MEM_M WS* MINUS WS* ONE;
comp_a1_D_plus_M: REG_D WS* PLUS WS* MEM_M;
comp_a1_D_minus_M: REG_D WS* MINUS WS* MEM_M;
comp_a1_M_minus_D: MEM_M WS* MINUS WS* REG_D; 
comp_a1_D_and_M: REG_D WS* AND WS* MEM_M;
comp_a1_D_or_M: REG_D WS* OR WS* MEM_M;

jump: ';' WS* jmp_syms ;

jmp_syms: JMP_JGT | JMP_JEQ | JMP_JGE 
        | JMP_JLT | JMP_JNE | JMP_JLE | JMP_JMP;    


label: '(' labelname ')' ;
labelname: SYMBOLNAME ;

EQ: '=';
AND: '&';
OR: '|';
PLUS: '+';
MINUS: '-';

ZERO: '0';
ONE: '1';
REG_A: 'A' ;
//M_REG_A: '-A';
REG_D: 'D' ;
//M_REG_D: '-D';
MEM_M: 'M' ;
//M_MEM_M: '-M';
REG_AD: 'AD' ;
REG_AM: 'AM' ;
REG_MD: 'MD' ;
REG_AMD: 'AMD' ;

NOT: '!';

JMP_JGT     :   'JGT' ;
JMP_JEQ     :   'JEQ' ;
JMP_JGE     :   'JGE' ;
JMP_JLT     :   'JLT' ;
JMP_JNE     :   'JNE' ;
JMP_JLE     :   'JLE' ;
JMP_JMP     :   'JMP' ;

DEF_SP      :   'SP' ;
DEF_LCL     :   'LCL' ;
DEF_ARG     :   'ARG' ;
DEF_THIS    :   'THIS' ;
DEF_THAT    :   'THAT' ;
DEF_R0      :   'R0' ;
DEF_R1      :   'R1' ;
DEF_R2      :   'R2' ;
DEF_R3      :   'R3' ;
DEF_R4      :   'R4' ;
DEF_R5      :   'R5' ;
DEF_R6      :   'R6' ;
DEF_R7      :   'R7' ;
DEF_R8      :   'R8' ;
DEF_R9      :   'R9' ;
DEF_R10     :   'R10' ;
DEF_R11     :   'R11' ;
DEF_R12     :   'R12' ;
DEF_R13     :   'R13' ;
DEF_R14     :   'R14' ;
DEF_R15     :   'R15' ;
DEF_SCREEN  :   'SCREEN' ;
DEF_KBD     :   'KBD' ;

NEWLINE     :   [\r\n]+ ;
WS          :   [ \t];

DIGIT       :   [0-9] ;

SYMBOLNAME  :  (SYMBOLSTART (SYMBOLSTART | DIGIT)*) ;
fragment LCASE      :   [a-z] ;
fragment UCASE      :   [A-Z] ;
fragment SYMBOLSTART :  LCASE | UCASE | '_' | '.' | '$' | ':';


COMMENT :  '//' ~('\r' | '\n')* ;
