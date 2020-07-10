from collections import defaultdict
from intcodecomputer import IntcodeComputer
import numpy as np
import matplotlib.pyplot as plt
class EmergencyHullPaintingRobot(IntcodeComputer):
    '''
    coord:   positive in lower right
    '''
    def __init__(self,arr,dtype='int32', start=0):
        self._map = defaultdict(lambda:0)
        self.camera = self.input_generator()
        super().__init__(arr, input_generator=self.camera, dtype=dtype)
        self.position = (0,0)
        self.direction = 90
        self._map[(0,0)] = start
        
    def input_generator(self):
        i = 1
        while True:
            yield self._map[self.position]
            i +=1
                
    def standardize_direction(self):
        if self.direction <0:
            self.direction += 360
        elif self.direction >=360:
            self.direction -= 360
            
    def change_direction(self, val):
        if val == 0:
            self.direction += 90
        elif val ==1:
            self.direction -= 90
        self.standardize_direction()
        
    def change_position(self):
        x, y = self.position
        stats ={0  : ( 0,  1),
                90 : (-1,  0),
                180: ( 0, -1),
                270: ( 1,  0)}
        st = stats[self.direction]
        self.position = (x+st[0], y+st[1])
                
    def step(self):
        color = next(self.run_w_yield())
        self._map[self.position] = color
        direction = next(self.run_w_yield())
        self.change_direction(direction)
        self.change_position()

    def visual_map(self):
        if len(self._map) <= 1:
            while True:
                try:
                    e.step()
                except StopIteration:
                    break
        _max = 1 + np.abs(
            max(
                list(max(self._map, key=lambda x : np.abs(x[0])))+list(max(self._map, key=lambda x : np.abs(x[1]))),
                key=lambda x:np.abs(x)
            )
        )
        img = np.zeros(shape=(_max,_max))
        for k,v in self._map.items():
            img[k]=v
        z = (img == 0).all(1)
        take = np.where(z==0)
        img = img[take]
        plt.imshow(img)
