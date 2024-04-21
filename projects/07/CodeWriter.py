from CommandType import CommandType

class CommandWriterUnsupported(Exception):
    pass

class CodeWriter:
    def __init__(self, filename_or_testLines, pcOffset=0, labelMode=False, debug=0):
        self.__debug = debug

        self.__writeToList = False
        self.__filename_or_testLines = filename_or_testLines
        self.__pc = pcOffset
        self.__labelMode = labelMode
        self.__pt = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT", "temp":"R5", "static":"R0", "pointer":"THIS"}

        if isinstance(filename_or_testLines, list):
            self.__writeToList = True
        else:
            self.__f = open(filename_or_testLines, "w")

    def __makeConditionalOpCode(self, command, code:list):
        op = {"eq":"=", "gt":">", "lt":"<"}[command]
        jmp = {"eq":"JEQ", "gt":"JGT", "lt":"JLT"}[command]
        code.append(f'// {command} ( if *(SP-2) {op} *(SP-1) then -1 else 0 -> *(SP-2), SP=SP-1)')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP')
        code.append(f'D=M     // {self.__pc+1: >5}:D=SP')
        code.append(f'A=D-1   // {self.__pc+2: >5}:A=D-1:SP-1')
        code.append(f'D=M     // {self.__pc+3: >5}:D=*(SP-1):y')
        code.append(f'A=A-1   // {self.__pc+4: >5}:A=A-1:SP-2')
        code.append(f'D=M-D   // {self.__pc+5: >5}:D=*(SP-2):x-D:y')
        self.__pc += 6
        if self.__labelMode:
            code.append(f'@TRUE   // {self.__pc+0: >5}:A=Jump target address if x {op} y')
        else:
            truepc = self.__pc+5
            code.append(f'@{truepc: <6} // {self.__pc+0: >5}:A=Jump target address if x {op} y')
        code.append(f'D;{jmp}   // {self.__pc+1: >5}:D=*(SP-2):x-D:y')
        code.append(f'D=0     // {self.__pc+2: >5}:D=false')
        self.__pc += 3
        if self.__labelMode: 
            code.append(f'@END    // {self.__pc+0: >5}:A=end address')
        else:
            endpc = self.__pc+3
            code.append(f'@{endpc: <6} // {self.__pc+0: >5}:A=end address')
        code.append(f'0;JMP   // {self.__pc+1: >5}:jump to END')
        if self.__labelMode: 
            code.append(f'(TRUE)  // true case')
        code.append(f'D=-1    // {self.__pc+2: >5}:D=true')
        if self.__labelMode: 
            code.append(f'(END)   // post processing')
        code.append(f'@SP     // {self.__pc+3: >5}:A=&SP')
        code.append(f'A=M-1   // {self.__pc+4: >5}:A=SP-1')
        code.append(f'A=A-1   // {self.__pc+5: >5}:A=A-1:SP-2')
        code.append(f'M=D     // {self.__pc+6: >5}:*(SP-2)=D:result')
        code.append(f'D=A+1   // {self.__pc+7: >5}:D=A+1:SP-1')
        code.append(f'@SP     // {self.__pc+8: >5}:A=&SP')
        code.append(f'M=D     // {self.__pc+9: >5}:SP=D:SP-1')
        self.__pc += 10
 
    def __makeArtithmeticTwoArgsCode(self, command, code:list):
        op = {"add":"+", "sub":"-", "and":"&", "or":"|"}[command]
        code.append(f'// {command} ( *(SP-2) {op} *(SP-1) -> *(SP-2), SP=SP-1)')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP')
        code.append(f'A=M     // {self.__pc+1: >5}:A=SP')
        code.append(f'A=A-1   // {self.__pc+2: >5}:A=A-1:SP-1')
        code.append(f'D=M     // {self.__pc+3: >5}:D=*(SP-1):y')
        code.append(f'A=A-1   // {self.__pc+4: >5}:A=A-1:SP-2')
        code.append((f'M=M{op}D   // {self.__pc+5: >5}:M=*(SP-2):x{op}D:y') 
                    if command == "sub" else (f'M=D{op}M   // {self.__pc+5: >5}:M=D:y{op}*(SP-2):x'))
        code.append(f'D=A+1   // {self.__pc+6: >5}:D=A+1:SP-1')
        code.append(f'@SP     // {self.__pc+7: >5}:A=&SP')
        code.append(f'M=D     // {self.__pc+8: >5}:SP=D:SP-1')
        self.__pc += 9

    def __makeArithmeticOneArgCode(self, command, code:list):
        if command == "not":
            code.append(f'// {command} ( !(*(SP-1)) -> *(SP-2))')
        else:
            code.append(f'// {command} ( -(*(SP-1)) -> *(SP-2))')    
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP')
        code.append(f'A=M     // {self.__pc+1: >5}:A=SP')
        code.append(f'A=A-1   // {self.__pc+2: >5}:A=A-1:SP-1')
        if command == "not":
            code.append(f'M=!M    // {self.__pc+3: >5}:*(SP-1)=!(*(SP-1)):!x')
        else:
            code.append(f'M=-M    // {self.__pc+3: >5}:*(SP-1)=-(*(SP-1)):-x')
        self.__pc += 4

    def writeArithmetic(self, command):
        code = []
        if command == "add" or command == "sub" or command == "and" or command == "or":
            self.__makeArtithmeticTwoArgsCode(command, code)
        elif command == "eq" or command == "gt" or command == "lt":
            self.__makeConditionalOpCode(command, code)
        elif command == "not" or command == "neg":
            self.__makeArithmeticOneArgCode(command,code)
        else:
            raise CommandWriterUnsupported(f'Unsupported command {command}.')        
        if self.__writeToList:
            self.__filename_or_testLines.extend(code)           
        else:
            self.__f.write("\n".join(code))
            self.__f.write("\n\n")

    def __makePushCode(self, segment, index, code:list):
        code.append(f'// push {segment} {index}')
        if segment == "constant":
            code.append(f'@{index: <6} // {self.__pc+0: >5}:A={index}')
            code.append(f'D=A     // {self.__pc+1: >5}:D=A:{index}')
            self.__pc += 2
        elif segment == "local" or segment == "argument" or segment == "this" or \
            segment == "that" or segment == "temp" or segment == "static" or segment == "pointer":
            pt = self.__pt[segment]
            code.append(f'@{index: <6} // {self.__pc+0: >5}:A={index}')
            code.append(f'D=A     // {self.__pc+1: >5}:D=A:{index}')
            code.append(f'@{pt: <6} // {self.__pc+2: >5}:A=&{pt}:1')
            if segment == "temp" or segment == "static" or segment == "pointer":
                code.append(f'A=D+A   // {self.__pc+3: >5}:A=D:{index}+A:&{pt}')
            else:
                code.append(f'A=M+D   // {self.__pc+3: >5}:A=*{pt}+{index}')
            code.append(f'D=M     // {self.__pc+4: >5}:D=*(*{pt}+{index})')
            self.__pc += 5
        else:
            raise CommandWriterUnsupported(f'Unsupported Push segment: {segment}.')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP:0')
        code.append(f'A=M     // {self.__pc+1: >5}:A=SP')
        code.append(f'M=D     // {self.__pc+2: >5}:*(SP)=D:'+(f'{index}' if segment == "constant" else f'*(*{pt}+{index})'))
        code.append(f'D=A+1   // {self.__pc+3: >5}:D=SP+1')
        code.append(f'@SP     // {self.__pc+4: >5}:A=&SP')
        code.append(f'M=D     // {self.__pc+5: >5}:SP=D:SP+1')
        self.__pc += 6
        
    def __makePopCode(self, segment, index, code:list):
        code.append(f'// pop {segment} {index}')
        if segment == "constant":
            code.append(f'@SP     // {self.__pc+0: >5}:A=&SP:0')
            code.append(f'M=M-1   // {self.__pc+1: >5}:SP=SP-1')
            self.__pc += 2
        elif segment == "local" or segment == "argument" or segment == "this" or \
                segment == "that" or segment == "temp" or segment == "static" or segment == "pointer":
            pt = self.__pt[segment]
            code.append(f'@{index: <6} // {self.__pc+0: >5}:A={index}')
            code.append(f'D=A     // {self.__pc+1: >5}:D=A:{index}')
            code.append(f'@{pt: <6} // {self.__pc+2: >5}:A=&{pt}:1')
            if segment == "temp" or segment == "static" or segment == "pointer":
                code.append(f'D=D+A   // {self.__pc+3: >5}:D=D:{index}+A:&{pt}:destination address')
            else:
                code.append(f'D=D+M   // {self.__pc+3: >5}:D=D:{index}+{pt}:destination address')
            code.append(f'@SP     // {self.__pc+4: >5}:A=&SP:0')
            code.append(f'A=M     // {self.__pc+5: >5}:A=SP')
            code.append(f'M=D     // {self.__pc+6: >5}:*SP=D:destination address (temporally storing)')

            code.append(f'A=A-1   // {self.__pc+7: >5}:A=SP-1')
            code.append(f'D=M     // {self.__pc+8: >5}:*(SP-1)=D:copying data')
            code.append(f'A=A+1   // {self.__pc+9: >5}:A=SP')
            code.append(f'A=M     // {self.__pc+10: >5}:A=*SP:destination address')
            code.append(f'M=D     // {self.__pc+11: >5}:*(destination address)=D:copying data')

            code.append(f'@SP     // {self.__pc+12: >5}:A=&SP:0')
            code.append(f'M=M-1   // {self.__pc+13: >5}:SP=SP-1')
            self.__pc += 14
        else:
            raise CommandWriterUnsupported(f'Unsupported Pop segment: {segment}.')
        
    def writePushPop(self, push_or_pop:CommandType, segment, index):
        code = []
        if push_or_pop == CommandType.C_PUSH:
            self.__makePushCode(segment, index, code)
        elif push_or_pop == CommandType.C_POP:
            self.__makePopCode(segment, index, code)
        else:
            raise CommandWriterUnsupported(f'Unsupported command {push_or_pop}.')
        if self.__writeToList:
            self.__filename_or_testLines.extend(code)           
        else:
            self.__f.write("\n".join(code))
            self.__f.write("\n\n")

    def close(self):
        if not self.__writeToList:
            self.__f.close()

    # for unit test
    @property
    def pc(self):
        return self.__pc
    
    