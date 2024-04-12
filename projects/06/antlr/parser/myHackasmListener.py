from antlr4 import *
if "." in __name__:
    from .hackasmParser import hackasmParser
else:
    from hackasmParser import hackasmParser
from hackasmListener import hackasmListener

class myHackasmListener(hackasmListener):

    # @override Hackasm 開始時のインスタンス変数の初期化
    def enterHackasm(self, ctx:hackasmParser.HackasmContext):
        self.myDebug = 0

        # Encoding 中の Program Counter
        self.pc = 0

        # PC to Encodeされた Binary 列 Map
        self.encodedBin = {}

        # PC to Undetermined symbol Map in 1st-pass
        self.undetSymTbl = {}

        # Variable to (Data) Address Map
        self.variableTbl = {}
        
        # Pre defined symbol to Address Map
        self.preDefSymTbl = \
            {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4,\
             'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, \
             'R5':5, 'R6':6, 'R7':7, 'R8':8, 'R9':9, \
             'R10':10, 'R11':11, 'R12':12, 'R13':13, \
             'R14':14, 'R15':15, 'SCREEN':16384, 'KBD': 24576 }
        
        # 変数にアサインするアドレスとその最大限界
        self.variableAddress = 16
        self.variableAddressEnd = 16384
        
        # C-instruction の Detination 部の Encoding table
        self.destBinTbl = \
            {'M':"001", 'D':"010", 'MD':"011", 'A':"100",\
             'AM':"101", 'AD':"110", "AMD":"111"}
        
        # C-instruction の Jump 部の Encoding table
        self.jmpBinTbl = \
            {'JGT':"001", 'JEQ':"010", 'JGE':"011", 'JLT':"100",\
             'JNE':"101", 'JLE':"110", "JMP":"111"}
        
        # Label to Program Counter Map
        self.labelTbl = {}

    def exitHackasm(self, ctx:hackasmParser.HackasmContext):
        if self.myDebug > 0:
            print(f'undetSym: {self.undetSymTbl}')
            print(f'labelTbl: {self.labelTbl}')
        
        # 2nd pass for undetermined address assignment
        for pc, symbol in self.undetSymTbl.items():
            def makeAinst(addr):
                return "0" + f'{addr:015b}'

            if symbol in self.labelTbl:
                # アドレス未決定のシンボルがラベル表にあった場合ラベル割り当てを優先
                labelAddr = self.labelTbl[symbol]
                self.encodedBin[pc] = makeAinst(labelAddr)
            else:
                if symbol not in self.variableTbl:
                    # Variableとして登録されていない場合
                    if self.variableAddress == self.variableAddressEnd:
                        raise "Symbol address can not be assignned any more."
                    self.variableTbl[symbol] = self.variableAddress
                    self.variableAddress += 1
                                    
                valAddr = self.variableTbl[symbol]
                self.encodedBin[pc] = makeAinst(valAddr)

        if self.myDebug > 0:
            print('### 2nd pass result ###')
            print(f'variableTbl: {self.variableTbl}')
        # Output
        for pc, bin in self.encodedBin.items():
            if self.myDebug > 0:
                print(f'PC:{pc:04d} -> {bin}')
            else:
                print(bin)

    def enterInst(self, ctx:hackasmParser.InstContext):
        self.encodedBin[self.pc] = ""

    def exitInst(self, ctx:hackasmParser.InstContext):
        if self.myDebug > 0:
            print(f'PC:{self.pc:04d} -> {self.encodedBin[self.pc]} // {ctx.getText()}')
        self.pc += 1

    def enterAinst(self, ctx:hackasmParser.AinstContext):
        self.encodedBin[self.pc] += "0"

    def enterAinst_arg(self, ctx:hackasmParser.Ainst_argContext):
        self.ainstArg = ctx.getText()

    def enterPre_defined_syms(self, ctx:hackasmParser.Pre_defined_symsContext):
        number = self.preDefSymTbl[self.ainstArg]
        self.encodedBin[self.pc] += f'{number:015b}'

    def enterOther_syms(self, ctx:hackasmParser.Other_symsContext):
        self.undetSymTbl[self.pc] = self.ainstArg
        self.encodedBin[self.pc] = f'u{self.pc:015b}'

    def exitAinst_number(self, ctx:hackasmParser.Ainst_numberContext):
        number = int(self.ainstArg)
        self.encodedBin[self.pc] += f'{number:015b}'

    def enterCinst(self, ctx:hackasmParser.CinstContext):
        self.encodedBin[self.pc] += "111"
        self.compBin = "0000000"
        self.destBin = "000"
        self.jmpBin = "000"

    def exitCinst(self, ctx:hackasmParser.CinstContext):
        self.encodedBin[self.pc] += self.compBin + self.destBin + self.jmpBin


    def enterComp_a0_zero(self, ctx:hackasmParser.Comp_a0_zeroContext):
        self.compBin = "0" + "101010"

    def enterComp_a0_one(self, ctx:hackasmParser.Comp_a0_oneContext):
        self.compBin = "0" + "111111"

    def enterComp_a0_minus_one(self, ctx:hackasmParser.Comp_a0_minus_oneContext):
        self.compBin = "0" + "111010"

    def enterComp_a0_D(self, ctx:hackasmParser.Comp_a0_DContext):
        self.compBin = "0" + "001100"

    def enterComp_a0_A(self, ctx:hackasmParser.Comp_a0_AContext):
        self.compBin = "0" + "110000"

    def enterComp_a0_not_D(self, ctx:hackasmParser.Comp_a0_not_DContext):
        self.compBin = "0" + "001101"

    def enterCmop_a0_not_A(self, ctx:hackasmParser.Cmop_a0_not_AContext):
        self.compBin = "0" + "110001"

    def enterComp_a0_minus_D(self, ctx:hackasmParser.Comp_a0_minus_DContext):
        self.compBin = "0" + "001111"

    def enterComp_a0_minus_A(self, ctx:hackasmParser.Comp_a0_minus_AContext):
        self.compBin = "0" + "110011"

    def enterComp_a0_D_plus_one(self, ctx:hackasmParser.Comp_a0_D_plus_oneContext):
        self.compBin = "0" + "011111"

    def enterComp_a0_A_plus_one(self, ctx:hackasmParser.Comp_a0_A_plus_oneContext):
        self.compBin = "0" + "110111"

    def enterComp_a0_D_minus_one(self, ctx:hackasmParser.Comp_a0_D_minus_oneContext):
        self.compBin = "0" + "001110"

    def enterComp_a0_A_minus_one(self, ctx:hackasmParser.Comp_a0_A_minus_oneContext):
        self.compBin = "0" + "110010"

    def enterComp_a0_D_plus_A(self, ctx:hackasmParser.Comp_a0_D_plus_AContext):
        self.compBin = "0" + "000010"

    def enterComp_a0_D_minus_A(self, ctx:hackasmParser.Comp_a0_D_minus_AContext):
        self.compBin = "0" + "010011"

    def enterComp_a0_A_minus_D(self, ctx:hackasmParser.Comp_a0_A_minus_DContext):
        self.compBin = "0" + "000111"

    def enterComp_a0_D_and_A(self, ctx:hackasmParser.Comp_a0_D_and_AContext):
        self.compBin = "0" + "000000"

    def enterComp_a0_D_or_A(self, ctx:hackasmParser.Comp_a0_D_or_AContext):
        self.compBin = "0" + "010101"

    def enterComp_a1_M(self, ctx:hackasmParser.Comp_a1_MContext):
        self.compBin = "1" + "110000"

    def enterComp_a1_not_M(self, ctx:hackasmParser.Comp_a1_not_MContext):
        self.compBin = "1" + "110001"

    def enterComp_a1_minus_M(self, ctx:hackasmParser.Comp_a1_minus_MContext):
        self.compBin = "1" + "110011"

    def enterComp_a1_M_plus_one(self, ctx:hackasmParser.Comp_a1_M_plus_oneContext):
        self.compBin = "1" + "110111"

    def enterComp_a1_M_minus_one(self, ctx:hackasmParser.Comp_a1_M_minus_oneContext):
        self.compBin = "1" + "110010"

    def enterComp_a1_D_plus_M(self, ctx:hackasmParser.Comp_a1_D_plus_MContext):
        self.compBin = "1" + "000010"

    def enterComp_a1_D_minus_M(self, ctx:hackasmParser.Comp_a1_D_minus_MContext):
        self.compBin = "1" + "010011"

    def enterComp_a1_M_minus_D(self, ctx:hackasmParser.Comp_a1_M_minus_DContext):
        self.compBin = "1" + "000111"

    def enterComp_a1_D_and_M(self, ctx:hackasmParser.Comp_a1_D_and_MContext):
        self.compBin = "1" + "000000"

    def enterComp_a1_D_or_M(self, ctx:hackasmParser.Comp_a1_D_or_MContext):
        self.compBin = "1" + "010101"


    def enterDest(self, ctx:hackasmParser.DestContext):
        dest = ctx.getText()
        self.destBin = self.destBinTbl[dest]
    
    def enterJmp_syms(self, ctx:hackasmParser.Jmp_symsContext):
        jmp = ctx.getText()
        self.jmpBin = self.jmpBinTbl[jmp]

    def enterLabelname(self, ctx:hackasmParser.LabelnameContext):
        label = ctx.getText()
        self.labelTbl[label] = self.pc
        if self.myDebug > 0:
            print(f'PC:{self.pc:04d} -> label:{label}')
