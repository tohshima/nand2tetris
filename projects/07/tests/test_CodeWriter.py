import sys
sys.path.append("../")
from CodeWriter import CodeWriter 
from CommandType import CommandType

class TestCase:

    def setup_method(self,method):
        pass

    def teardownn_method(self,method):
        pass

    def test_A(self):
        outlines = []
        writer = CodeWriter(outlines)
        writer.writeArithmetic("add")
        print(outlines)