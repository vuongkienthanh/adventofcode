from collections import defaultdict
import numpy as np

def InputHolder(start):
    while True:
        temp = yield start
        if temp is not None:
            start = temp

class IntcodeComputer():
    '''
    arr             : list of integers OR str
    input_generator : a generator of input values
    dtype           : "int32"; "int64"
    ----------------
    methods
    run()           : run the intcode provided, raise exception when halted
    ----------------
    notes
    Currently have opcode 1,2,3,4,5,6,7,8,9 and 99
    Currently have mode "position", "immediate", "relative"
    Opcode 3        : will get input from the input_generator and write to postion from param
                      , no support for immediate mode
    '''
    def __init__(self, arr, input_generator=None, dtype='int64'):
        if isinstance(arr, str):
            arr = [int(x) for x in arr.split(',')]
        self.arr = defaultdict(lambda :0)
        self.arr.update({i:x for i,x in enumerate(np.array(arr, dtype=dtype))})
        self.arr_orig = self.arr.copy()
        self.input_gen = input_generator
        self.output = []
        self.idx = 0
        self.relative_base = 0
        
    def run(self):
        while True:
            try:
                prog, mode1, mode2, mode3 = self.intcode(self.arr[self.idx])
                try:
                    a =self.arr[self.idx+1]
                    b =self.arr[self.idx+2]
                    c =self.arr[self.idx+3]
                except IndexError:
                    b = c = None
                prog(
                    a,b,c,
                    modes = (mode1, mode2, mode3)
                )
            except Exception as e:
                print(repr(e))
                break
                
    def run_w_yield(self):
        while True:
            try:
                prog, mode1, mode2, mode3 = self.intcode(self.arr[self.idx])
                try:
                    a =self.arr[self.idx+1]
                    b =self.arr[self.idx+2]
                    c =self.arr[self.idx+3]
                except IndexError:
                    b = c = None
                prog(
                    a,b,c,
                    modes = (mode1, mode2, mode3)
                )
                if prog.__name__ == "_print":
                    yield self.output[-1]
            except Exception as e:
                print(repr(e))
                break
        
    def intcode(self, code):
        code = str(code).rjust(5,"0")
        main = int(code[-2:])
        first = int(code[2])
        second = int(code[1])
        third = int(code[0])
        dictionary = {
            1 : self.add,
            2 : self.multiply,
            3 : self.write,
            4 : self._print,
            5 : self.jumpiftrue,
            6 : self.jumpiffalse,
            7 : self.lessthan,
            8 : self.equals,
            9 : self.adjust_relative,
            99: self.halt
        }
        mode = {
            0: "position",
            1: "immediate",
            2: "relative"
        }
        return dictionary[main], mode[first], mode[second], mode[third]
    
    def getval(self, val, mode):
        if mode=='position':
            return self.arr[val]
        elif mode=='immediate':
            return val
        elif mode=="relative":
            return self.arr[val+self.relative_base]
        
    def getpos(self, val, mode):
        if mode=='position':
            return val
        elif mode=="relative":
            return val+self.relative_base

    def add(self, a,b,c, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        c = self.getpos(c, modes[2])
        self.arr[c] = a+b
        self.idx +=4
    def multiply(self, a,b,c, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        c = self.getpos(c, modes[2])
        self.arr[c] = a*b
        self.idx +=4
    def write(self, a, *args, modes):
        val = next(self.input_gen)
        a = self.getpos(a, modes[0])
        self.arr[a] = val
        self.idx +=2
    def _print(self, a, *args, modes):
        self.output += [self.getval(a, modes[0])]
        self.idx +=2
    def jumpiftrue(self, a, b, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        if a != 0:
            self.idx =b
        else:
            self.idx +=3
    def jumpiffalse(self, a, b, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        if a == 0:
            self.idx =b
        else:
            self.idx +=3
    def lessthan(self, a,b,c, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        c = self.getpos(c, modes[2])
        if a<b:
            self.arr[c] = 1
        else:
            self.arr[c] = 0   
        self.idx +=4
    def equals(self, a,b,c, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        c = self.getpos(c, modes[2])
        if a==b:
            self.arr[c] = 1
        else:
            self.arr[c] = 0 
        self.idx +=4
    def adjust_relative(self, a, *args, modes):
        a = self.getval(a, modes[0])
        self.relative_base += a
        self.idx +=2
    def halt(self, *args, modes):
        raise Exception('Intcode Computer halted!')
