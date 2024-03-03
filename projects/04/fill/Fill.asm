// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// count: number of words of screen
// pixel: black(0xFFFF) or white(0) write value
// current: current pointer to word address of screen

(LOOP)

// write count 512x256/16
// initialize count
@8192
D=A
@count
M=D

// check key pushed
@KBD
D=M

// black or white value. it is set to 0xFFFFFFFF if key pressed
@pixel
M=0

@CHECKED
D;JEQ

@pixel
M=!M

(CHECKED)

// initialize current pointer to the head of screen (0x4000)
@SCREEN
D=A

@current
M=D     

(WRITELOOP)
// load count to D
@count
D=M
// count--
M=D-1
// exit if count=0 (counte refers to that of before decrement)
@WRITEEND
D;JEQ

// write pixels *current=black
@pixel
D=M
@current
A=M
M=D
// current++
@current
M=M+1

@WRITELOOP
0;JMP

(WRITEEND)
@LOOP
0;JMP
