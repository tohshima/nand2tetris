



// add ( *(SP-2) + *(SP-1) -> *(SP-2), SP=SP-1)
@SP     // A=&SP
A=M     // A=SP
A=A-1   // A=A-1:SP-1
D=M     // D=*(SP-1):y
A=A-1   // A=A-1:SP-2
M=D+M   // M=D:y+*(SP-2):x
D=A+1   // D=A+1:SP-1
@SP     // A=&SP
M=D     // SP=D:SP-1

