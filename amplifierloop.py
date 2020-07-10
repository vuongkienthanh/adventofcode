import numpy as np
import logging
# logging.basicConfig(level=logging.DEBUG)
from itertools import permutations, cycle

class Amplifier():
    '''
    arr        : - list of integers 
                 - str
    phase      : phase setting
    input_gen : generator after phase
    '''
    def __init__(self, arr, phase, input_gen):
        if isinstance(arr, str):
            arr = [int(x) for x in arr.split(',')]
        self.arr = np.array(arr)
        self.arr_orig = self.arr.copy()
        self.phase = phase
        self.input_gen = input_gen
        self.input_curr = None
        self.output = None
        self.idx = 0
        self.initialised = False
        
    def run(self): # make this generator too
        while True:
            logging.debug("+"*20 + f"idx={self.idx}")
            logging.debug(f'intcode={self.arr[self.idx]}')
            try:
                prog, mode1, mode2, mode3 = self.intcode(self.arr[self.idx])
                logging.debug(f"{prog.__name__}, {mode1}, {mode2}, {mode3}" )
                try:
                    a =self.arr[self.idx+1]
                    b =self.arr[self.idx+2]
                    c =self.arr[self.idx+3]
                except IndexError:
                    b = c = None
                logging.debug(f'{prog.__name__}, pos1={a}, pos2={b}, pos3={c}')
                prog(
                    a,b,c,
                    modes = (mode1, mode2, mode3)
                )
                logging.debug(f"next to {self.idx}")
                if prog.__name__ == '_print':
                    yield self.output
            except Exception as e:
                logging.debug(repr(e))
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
            99: self.halt
        }
        mode = {
            0: "position",
            1: "immediate"
        }
        return dictionary[main], mode[first], mode[second], mode[third]
    
    def getval(self, val, mode):
        return self.arr[val] if mode=='position' else val

    def add(self, a,b,c, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        self.arr[c] = a+b
        logging.debug(f"{a} + {b} = {self.arr[c]}")
        self.idx +=4
    def multiply(self, a,b,c, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        self.arr[c] = a*b
        logging.debug(f"{a} * {b} = {self.arr[c]}")
        self.idx +=4
    def write(self, a, *args, modes):
        if not self.initialised:
            self.arr[a] = self.phase
            self.initialised=True
            logging.debug("--"*30 + f"Amp {self.phase} initialise with phase {self.phase}")
        else:
            self.input_curr = next(self.input_gen)
            self.arr[a] = self.input_curr
            logging.debug(f"write {self.input_curr} to pos {a}")
        self.idx +=2
    def _print(self, a, *args, modes):
        if modes[0]=="position":
            self.output = self.arr[a]  
            logging.debug(f"output {self.arr[a]} from pos {a}")
        else:
            self.output = a
            logging.debug(f"output {a}")
        self.idx +=2
    def jumpiftrue(self, a, b, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        logging.debug(f"compare {a} !=0")
        if a != 0:
            logging.debug(f"jump to {b}")
            self.idx =b
        else:
            logging.debug("not jump")
            self.idx +=3
    def jumpiffalse(self, a, b, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        logging.debug(f"compare {a} ==0")
        if a == 0:
            logging.debug(f"jump to {b}")
            self.idx =b
        else:
            logging.debug("not jump")
            self.idx +=3
    def lessthan(self, a,b,c, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        logging.debug(f"compare {a}<{b}")
        if a<b:
            logging.debug(f"pos {c} =1")
            self.arr[c] = 1
        else:
            logging.debug(f"pos {c} =0")
            self.arr[c] = 0   
        self.idx +=4
    def equals(self, a,b,c, *args, modes):
        a = self.getval(a, modes[0])
        b = self.getval(b, modes[1])
        logging.debug(f"compare {a}=={b}")
        if a==b:
            logging.debug(f"pos {c} =1")
            self.arr[c] = 1
        else:
            logging.debug(f"pos {c} =0")
            self.arr[c] = 0 
        self.idx +=4
    def halt(self, *args, modes):
        raise Exception('Intcode Computer halted!')
        

class AmplifierLoop():
    '''
    arr : amplifier intcode computer arr
    low, high: range of phase 
    '''
    def __init__(self, arr, low, high):
        self.arr = arr
        self.permut = permutations(range(low, high+1))
    
    def input_generator(self):
        x =0
        while True:
            i = (yield x)
            if i is not None: # prevent case x is also generator
                x = i
            
    def get_highest_output(self):
        res =[]
        for a,b,c,d,e in self.permut:
            logging.debug("*"*20 + f"Permutation {a} {b} {c} {d} {e}" + "*"*20)
            input_gen = self.input_generator()

            amp1 = Amplifier(self.arr, a, input_gen)
            amp2 = Amplifier(self.arr, b, input_gen)
            amp3 = Amplifier(self.arr, c, input_gen)
            amp4 = Amplifier(self.arr, d, input_gen)
            amp5 = Amplifier(self.arr, e, input_gen)
            
            loop = cycle([amp1,amp2,amp3,amp4,amp5])
            for amp in loop:
                try:
                    out = next(amp.run())
                    input_gen.send(out)
                except StopIteration:
                    break
            res += [out]
        return np.max(res)
