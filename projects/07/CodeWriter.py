from HackVM import CommandType, MapDefLabelToAddr

class CommandWriterUnsupported(Exception):
    pass

class CodeWriter:
    def __init__(self, filename_or_testLines, pcOffset=0, labelMode=False, debug=0):
        self.__debug = debug

        self.__writeToList = False
        self.__filename_or_testLines = filename_or_testLines
        self.__pc = pcOffset
        self.__labelMode = labelMode
        self.__callCount = 0 # increments by each call
        self.__lastFuncName = ""
        self.__staticVarAddrHeadForFile = 16
        self.__staticVarMaxOffsetInFile = -1
        self.__pt = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT", "temp":"R5", 
                     "static":str(self.__staticVarAddrHeadForFile), "pointer":"THIS"}

        if isinstance(filename_or_testLines, list):
            self.__writeToList = True
        else:
            self.__f = open(filename_or_testLines, "w")

    def setFileName(self, fileName):
        self.__staticVarAddrHeadForFile = self.__staticVarAddrHeadForFile + self.__staticVarMaxOffsetInFile + 1
        self.__staticVarMaxOffsetInFile = -1
        self.__pt["static"] = str(self.__staticVarAddrHeadForFile)
        code = []
        code.append("//===============================" + "="*len(fileName))
        code.append(f'// Hack VM code translation for {fileName}')
        code.append(f'// (Static var head = {self.__staticVarAddrHeadForFile})')
        code.append("//===============================" + "="*len(fileName))
        self.__update(code)

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
        self.__update(code)

    def writePushPop(self, push_or_pop:CommandType, segment, index):
        code = []
        if push_or_pop == CommandType.C_PUSH:
            self.__makePushCode(segment, index, code)
        elif push_or_pop == CommandType.C_POP:
            self.__makePopCode(segment, index, code)
        else:
            raise CommandWriterUnsupported(f'Unsupported command {push_or_pop}.')
        self.__update(code)

    def writeLabel(self, label):
        code = []
        self.__makeLabelCode(label, code)
        self.__update(code)

    def writeGoto(self, label):
        code = []
        self.__makeGotoCode(label, code)
        self.__update(code)

    def writeIf(self, label):
        code = []
        self.__makeIfCode(label, code)
        self.__update(code)

    def writeFunction(self, functionName, nVals):
        code = []
        self.__makeFunctionCode(functionName, nVals, code)
        self.__update(code)

    def writeCall(self, functionName, nArgs):
        code = []
        self.__makeCallCode(functionName, nArgs, code)
        self.__callCount += 1
        self.__update(code)

    def writeReturn(self):
        code = []
        self.__makeReturnCode(code)
        self.__update(code)

    def close(self):
        if not self.__writeToList:
            self.__f.close()

    def __update(self, code:list):
        if self.__writeToList:
            self.__filename_or_testLines.extend(code)           
        else:
            self.__f.write("\n".join(code))
            self.__f.write("\n\n")

    def __makeConditionalOpCodePre(self, command, code:list, op):
        code.append(f'// {command} ( if *(SP-2) {op} *(SP-1) then -1 else 0 -> *(SP-2), SP=SP-1)')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP')
        code.append(f'D=M     // {self.__pc+1: >5}:D=SP')
        code.append(f'A=D-1   // {self.__pc+2: >5}:A=D-1:SP-1')
        code.append(f'D=M     // {self.__pc+3: >5}:D=*(SP-1):y')
        code.append(f'A=A-1   // {self.__pc+4: >5}:A=A-1:SP-2')
        code.append(f'D=M-D   // {self.__pc+5: >5}:D=*(SP-2):x-D:y')
        self.__pc += 6

    def __makeConditionalOpCodePost(self, command, code:list):
        code.append(f'@SP     // {self.__pc+3: >5}:A=&SP')
        code.append(f'A=M-1   // {self.__pc+4: >5}:A=SP-1')
        code.append(f'A=A-1   // {self.__pc+5: >5}:A=A-1:SP-2')
        code.append(f'M=D     // {self.__pc+6: >5}:*(SP-2)=D:result')
        code.append(f'D=A+1   // {self.__pc+7: >5}:D=A+1:SP-1')
        code.append(f'@SP     // {self.__pc+8: >5}:A=&SP')
        code.append(f'M=D     // {self.__pc+9: >5}:SP=D:SP-1')
        self.__pc += 10

    def __makeConditionalOpCode(self, command, code:list):
        op = {"eq":"=", "gt":">", "lt":"<"}[command]
        jmp = {"eq":"JEQ", "gt":"JGT", "lt":"JLT"}[command]
        self.__makeConditionalOpCodePre(command, code, op)
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
        self.__makeConditionalOpCodePost(command, code)
 
    def __makeArtithmeticTwoArgsCode(self, command, code:list, headComment=""):
        op = {"add":"+", "sub":"-", "and":"&", "or":"|"}[command]
        if len(headComment) > 0:
            code.append(headComment)
        else:
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

    def __makePushCodePre(self, segment, index, code:list):
        if segment == "constant":
            code.append(f'@{index: <6} // {self.__pc+0: >5}:A={index}')
            code.append(f'D=A     // {self.__pc+1: >5}:D=A:{index}')
            self.__pc += 2
        elif segment == "label":
            code.append(f'@{index: <6} // {self.__pc+0: >5}:A=address of label {index}')
            code.append(f'D=A     // {self.__pc+1: >5}:D=A:address of label {index}')
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
                
    def __makePushCode(self, segment, index, code:list, headComment=""):
        if len(headComment) > 0:
            code.append(headComment)
        else:
            code.append(f'// push {segment} {index}')
        if segment == "static":
            if index > self.__staticVarMaxOffsetInFile:
                self.__staticVarMaxOffsetInFile = index
        
        self.__makePushCodePre(segment, index, code)

        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP:0')
        code.append(f'A=M     // {self.__pc+1: >5}:A=SP')
        if segment == "constant":
            code.append(f'M=D     // {self.__pc+2: >5}:*(SP)=D:{index}')
        elif segment == "label":
            code.append(f'M=D     // {self.__pc+2: >5}:*(SP)=D:address of label {index}')
        else:
            pt = self.__pt[segment]
            code.append(f'M=D     // {self.__pc+2: >5}:*(SP)=D:*(*{pt}+{index})')
        code.append(f'D=A+1   // {self.__pc+3: >5}:D=SP+1')
        code.append(f'@SP     // {self.__pc+4: >5}:A=&SP')
        code.append(f'M=D     // {self.__pc+5: >5}:SP=D:SP+1')
        self.__pc += 6
        
    def __makePopCode(self, segment, index, code:list, headComment=""):
        if len(headComment) > 0:
            code.append(headComment)
        else:
            code.append(f'// pop {segment} {index}')
        if segment == "static":
            if index > self.__staticVarMaxOffsetInFile:
                self.__staticVarMaxOffsetInFile = index
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
            code.append(f'@R13    // {self.__pc+4: >5}:A=&R13')
            code.append(f'M=D     // {self.__pc+5: >5}:R13=D:destination address (temporally storing)')
            code.append(f'@SP     // {self.__pc+6: >5}:A=&SP:0')
            code.append(f'AM=M-1  // {self.__pc+7: >5}:A=SP-1, SP=SP-1')
            code.append(f'D=M     // {self.__pc+8: >5}:D=*(SP-1):copying data')
            code.append(f'@R13    // {self.__pc+9: >5}:A=&R13')
            code.append(f'A=M     // {self.__pc+10: >5}:A=R13:destination address')
            code.append(f'M=D     // {self.__pc+11: >5}:*(destination address)=D:copying data')
            self.__pc += 12
        else:
            raise CommandWriterUnsupported(f'Unsupported Pop segment: {segment}.')
        
    def __makeLabelCode(self, label, code:list):
        code.append(f'({label})')

    def __makeGotoCode(self, label, code:list):
        code.append(f'// goto {label}')
        code.append(f'@{label: <6} // {self.__pc+0: >5}:A=jump address')
        code.append(f'0;JMP   // {self.__pc+1: >5}:Jump to the address')
        self.__pc += 2

    def __makeIfCode(self, label, code:list):
        code.append(f'// if-goto {label}')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP:0')
        code.append(f'AM=M-1  // {self.__pc+1: >5}:A=SP-1, SP=SP-1')
        code.append(f'D=M     // {self.__pc+2: >5}:D=*(SP-1)')
        code.append(f'@{label: <6} // {self.__pc+3: >5}:A=jump address')
        code.append(f'D;JNE   // {self.__pc+4: >5}:Jump to the address if *(SP-1) is not zero')
        self.__pc += 5

    def __makeFunctionCode(self, functionName, nVals, code:list):
        self.__lastFuncName = functionName
        code.append(f'// function {functionName} {nVals}')
        self.__makeLabelCode(functionName, code)
        if nVals > 0:
            code.append(f'// Initialize {nVals} local val(s) to 0')
            code.append(f'D=0     // {self.__pc+0: >5}:D=0')
            code.append(f'@SP     // {self.__pc+1: >5}:A=&SP:0')
            code.append(f'A=M     // {self.__pc+2: >5}:A=SP')
            self.__pc += 3
            for i in range(nVals):
                code.append(f'M=D     // {self.__pc+0: >5}:*(SP+{i})=D:0')
                code.append(f'A=A+1   // {self.__pc+1: >5}:A=SP+{1+i}')
                self.__pc += 2                 
            code.append(f'D=A     // {self.__pc+0: >5}:D=A:SP+{nVals}')
            code.append(f'@SP     // {self.__pc+1: >5}:A=&SP:0')
            code.append(f'M=D     // {self.__pc+2: >5}:SP=D:SP+{nVals}')
            self.__pc += 3                 
            code.append(f'// End of initialization of function {functionName} {nVals}')

    def __makeCallCode(self, functionName, nArgs, code:list):
        retLabel = functionName + f'$ret.{self.__callCount}'
        code.append(f'// Start of call routine of {functionName} {nArgs}')
        self.__makePushCode("label", retLabel, code, "// Push return address to the caller's stack frame") # Store return address
        code.append(f'// Store the caller pointer LCL to the stack frame')
        code.append(f'@LCL    // {self.__pc+0: >5}:A=&LCL:1')
        code.append(f'D=M     // {self.__pc+1: >5}:D=LCL')
        code.append(f'@SP     // {self.__pc+2: >5}:A=&SP:0')
        code.append(f'A=M     // {self.__pc+3: >5}:A=SP')
        code.append(f'M=D     // {self.__pc+4: >5}:*SP=D:LCL')
        code.append(f'D=A     // {self.__pc+5: >5}:D=SP')
        code.append(f'@LCL    // {self.__pc+6: >5}:A=&LCL:1')
        code.append(f'M=D     // {self.__pc+7: >5}:LCL=SP:newLCL')
        self.__pc += 8
        code.append(f'// Store the caller pointers (ARG/THIS/THAT) to the stack frame')
        for pointer in ["ARG", "THIS", "THAT"]:
            code.append(f'@{pointer: <4}   // {self.__pc+0: >5}:A=&{pointer}')
            code.append(f'D=M     // {self.__pc+1: >5}:D=current {pointer}')
            code.append(f'@LCL    // {self.__pc+2: >5}:A=&LCL:1')
            code.append(f'AM=M+1  // {self.__pc+3: >5}:A=LCL+1, LCL=LCL+1')
            code.append(f'M=D     // {self.__pc+4: >5}:*(LCL-1)=D:current {pointer}')
            self.__pc += 5
        code.append(f'// Reposition SP/LCL to the callee stack frame')
        code.append(f'D=A+1   // {self.__pc+0: >5}:D=LCL+1')
        code.append(f'@SP     // {self.__pc+1: >5}:A=&SP:0')
        code.append(f'M=D     // {self.__pc+2: >5}:SP=LCL+1')
        code.append(f'@LCL    // {self.__pc+3: >5}:A=&LCL:1')
        code.append(f'M=D     // {self.__pc+4: >5}:LCL=LCL+1')
        offsetOfNewArgToSP = 5+nArgs
        code.append(f'// Reposition ARG to the first of the args pushed by caller')
        code.append(f'@{offsetOfNewArgToSP: <6} // {self.__pc+5: >5}:A={offsetOfNewArgToSP}')
        code.append(f'D=D-A   // {self.__pc+6: >5}:D=D:SP-A:{offsetOfNewArgToSP}')
        code.append(f'@ARG    // {self.__pc+7: >5}:A=&ARG:2')
        code.append(f'M=D     // {self.__pc+8: >5}:ARG=SP-A:{offsetOfNewArgToSP}')
        code.append(f'// Jump to the function')
        code.append(f'@{functionName: <6} // {self.__pc+9: >5}:A=address of {functionName}')
        code.append(f'0;JMP   // {self.__pc+10: >5}:jump to the function')
        self.__pc += 11
        self.__makeLabelCode(retLabel, code) # Return address label
        code.append(f'// End of call routine')

    def __makeReturnCode(self, code:list):
        code.append(f'// Start of return from {self.__lastFuncName}')
        code.append(f'// Pop the return value of the function to R14 temporally')
        code.append(f'@SP     // {self.__pc+0: >5}:A=&SP:0')
        code.append(f'AM=M-1  // {self.__pc+1: >5}:A=SP-1, SP=SP-1')
        code.append(f'D=M     // {self.__pc+2: >5}:D=*(SP-1):return address')
        code.append(f'@R14    // {self.__pc+3: >5}:A=&R14')
        code.append(f'M=D     // {self.__pc+4: >5}:R14=D:return address')
        code.append(f'// Reposition of SP')
        code.append(f'@ARG    // {self.__pc+5: >5}:A=&ARG:2')
        code.append(f'D=M+1   // {self.__pc+6: >5}:D=ARG+1')
        code.append(f'@SP     // {self.__pc+7: >5}:A=&SP:0')
        code.append(f'M=D     // {self.__pc+8: >5}:SP=ARG+1')
        self.__pc += 9
        code.append(f'// Restore caller pointer set (THAT/THIS/ARG)')
        for pointer in ["THAT", "THIS", "ARG"]:
            code.append(f'@LCL    // {self.__pc+0: >5}:A=&LCL:1')
            code.append(f'AM=M-1  // {self.__pc+1: >5}:A=LCL-1, LCL=LCL-1')
            code.append(f'D=M     // {self.__pc+2: >5}:D=*(LCL-1):saved {pointer}')
            code.append(f'@{pointer: <4}   // {self.__pc+3: >5}:A=&{pointer}')
            code.append(f'M=D     // {self.__pc+4: >5}:{pointer}=*(LCL-1):saved {pointer}')
            self.__pc += 5
        code.append(f'// Restore LCL and store return address to R13 temporally')
        code.append(f'@LCL    // {self.__pc+0: >5}:A=&LCL:1')
        code.append(f'D=M-1   // {self.__pc+1: >5}:D=LCL-1')
        code.append(f'A=D-1   // {self.__pc+2: >5}:A=LCL-2')
        code.append(f'D=M     // {self.__pc+3: >5}:D=*(LCL-2):saved return address')
        code.append(f'@R13    // {self.__pc+4: >5}:A=&R13')
        code.append(f'M=D     // {self.__pc+5: >5}:R13=return address')
        code.append(f'@LCL    // {self.__pc+6: >5}:A=&LCL:1')
        code.append(f'A=M-1   // {self.__pc+7: >5}:A=LCL-1')
        code.append(f'D=M     // {self.__pc+8: >5}:D=*(LCL-1):saved LCL')
        code.append(f'@LCL    // {self.__pc+9: >5}:A=&LCL:1')
        code.append(f'M=D     // {self.__pc+10: >5}:LCL=*(LCL-1):saved LCL')
        code.append(f'// Restore return value from R14')
        code.append(f'@R14    // {self.__pc+11: >5}:A=&R14')
        code.append(f'D=M     // {self.__pc+12: >5}:D=R14:retrun value')
        code.append(f'@SP     // {self.__pc+13: >5}:A=&SP:0')
        code.append(f'A=M-1   // {self.__pc+14: >5}:A=SP-1')
        code.append(f'M=D     // {self.__pc+15: >5}:*(SP-1)=D:return value')
        code.append(f'// Jump to the return address stored in R13 temporally')
        code.append(f'@R13    // {self.__pc+16: >5}:A=&R13')
        code.append(f'A=M     // {self.__pc+17: >5}:A=R13:return address')
        code.append(f'0;JMP   // {self.__pc+18: >5}:jump to the return address')
        code.append(f'// End of return routine')
        self.__pc += 19

    # for unit test
    @property
    def pc(self):
        return self.__pc
    
    @property
    def callCount(self):
        return self.__callCount
    
    @property
    def staticVarAddrHeadForFile(self):
        return self.__staticVarAddrHeadForFile

    @property
    def staticVarMaxOffsetInFile(self):
        return self.__staticVarMaxOffsetInFile
    