// push constant 7
@7      //     0:A=7
D=A     //     1:D=A:7
@SP     //     2:A=&SP:0
A=M     //     3:A=SP
M=D     //     4:*(SP)=D:7
D=A+1   //     5:D=SP+1
@SP     //     6:A=&SP
M=D     //     7:SP=D:SP+1

// push constant 8
@8      //     8:A=8
D=A     //     9:D=A:8
@SP     //    10:A=&SP:0
A=M     //    11:A=SP
M=D     //    12:*(SP)=D:8
D=A+1   //    13:D=SP+1
@SP     //    14:A=&SP
M=D     //    15:SP=D:SP+1

// add ( *(SP-2) + *(SP-1) -> *(SP-2), SP=SP-1)
@SP     //    16:A=&SP
A=M     //    17:A=SP
A=A-1   //    18:A=A-1:SP-1
D=M     //    19:D=*(SP-1):y
A=A-1   //    20:A=A-1:SP-2
M=D+M   //    21:M=D:y+*(SP-2):x
D=A+1   //    22:D=A+1:SP-1
@SP     //    23:A=&SP
M=D     //    24:SP=D:SP-1

