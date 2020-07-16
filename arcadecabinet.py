from intcodecomputer import IntcodeComputer
import numpy as np

class ArcadeCabinet(IntcodeComputer):
    def __init__(self, arr):
        self.js = self.joystick()
        super().__init__(arr, input_generator=self.js)
            
    def run(self, start=None):
        if start is None:
            super().run()
        else:
            self.arr[0] = start
            while True:
                try:
                    x = next(self.run_w_yield())
                    y = next(self.run_w_yield())
                    item = next(self.run_w_yield())
                    if x==-1 and y ==0:
                        print("NEW SCORE:", item)
                    if item ==4:
                        self.ball = x
                    elif item ==3:
                        self.paddle = x
                except StopIteration:
                    print("LAST SCORE", item)
                    break
    
    def count_block(self):
        self.run()
        data = np.array(self.output).reshape((-1, 3))
        return np.where(data[:,2]==2)[0].shape            
    
    def joystick(self):
        while True:
            if self.ball > self.paddle:
                yield 1
            elif self.ball <self.paddle:
                yield -1
            else:
                yield 0
