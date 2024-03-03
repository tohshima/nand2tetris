// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
// set R2 to 0
@2
M=0

// load R1 to D
@1
D=M

(LOOP)
// exit if R1=0
@END
D;JEQ 
// load R0 to D
@0
D=M
// R2 = R2+D
@2
M=M+D
// load R1 to D
@1
D=M
// MD = D-1
MD=D-1
// Re-loop
@LOOP
0;JMP
(END)

