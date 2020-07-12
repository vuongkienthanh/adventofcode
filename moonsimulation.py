import re
from itertools import combinations
from copy import deepcopy
class Moon(dict):
    def __str__(self):
        s = "pos=<x={}, y={}, z={}>, vel=<x={}, y={}, z={}>".format(
            str(self['pos']['x']).rjust(3),
            str(self['pos']['y']).rjust(3),
            str(self['pos']['z']).rjust(3),
            str(self['vel']['x']).rjust(3),
            str(self['vel']['y']).rjust(3),
            str(self['vel']['z']).rjust(3),
        )
        return s
    
    def potential_energy(self):
        return sum([abs(self['pos'][ax]) for ax in 'xyz'])
    
    def kinetic_energy(self):
        return sum([abs(self['vel'][ax]) for ax in 'xyz'])
    
    def total_energy(self):
        return self.potential_energy() * self.kinetic_energy()

class MoonSimulation():
    def __init__(self, data):
        self.moon_list = []
        for dat in data.split('\n'):
            coord = re.findall(r"-?\d+", dat)
            pos = dict(zip("xyz", [int(x) for x in coord]))
            vel = dict(zip("xyz", [0,0,0]))
            self.moon_list.append(Moon(pos=pos , vel=vel))
            self.idx = 0
            self.moon_list_orig = deepcopy(self.moon_list)
    
    def step(self, on_ax=None):
        self.update_vel(on_ax)
        self.update_pos(on_ax)
        self.idx +=1
        
    def update_vel(self, on_ax=None):
        def update(ax):
            if m1['pos'][ax] > m2['pos'][ax]:
                m1['vel'][ax] -=1
                m2['vel'][ax] +=1
            elif m1['pos'][ax] < m2['pos'][ax]:
                m1['vel'][ax] +=1
                m2['vel'][ax] -=1
            
        for m1, m2 in combinations(self.moon_list, 2):
            if on_ax is not None:
                update(on_ax)
            else:
                for ax in 'xyz':
                    update(ax)
                
    
    def update_pos(self, on_ax=None):
        for m in self.moon_list:
            if on_ax is not None:
                m['pos'][on_ax] += m['vel'][on_ax]
            else:
                for ax in 'xyz':
                    m['pos'][ax] += m['vel'][ax]
                
    def print_moon_list(self):
        for m in self.moon_list:
            print(m)
        print()
                  
    def run(self, steps, verbose=False):
        if verbose:
            print('After 0 step:')
            self.print_moon_list()
        for i in range(steps):
            self.step()
            if verbose:
                s = '' if self.idx ==1 else 's'
                print(f'After {self.idx} step{s}:')
                self.print_moon_list()
    
    def system_total_energy(self, verbose=False):
        if verbose:
            pk = 0
            s = "Sum of total energy: "
            print(f'Energy after {self.idx} steps:')
            for m in self.moon_list:
                p = m.potential_energy()
                k = m.kinetic_energy()
                print('pot:{a} +{b} +{c} ={d};   kin:{e} +{f} +{g} ={h};   total:{d} *{h} ={i}'.format(
                    a=str(abs(m['pos']['x'])).rjust(3),
                    b=str(abs(m['pos']['y'])).rjust(3),
                    c=str(abs(m['pos']['z'])).rjust(3),
                    d=str(p).rjust(3),
                    e=str(abs(m['vel']['x'])).rjust(3),
                    f=str(abs(m['vel']['y'])).rjust(3),
                    g=str(abs(m['vel']['z'])).rjust(3),
                    h=str(k).rjust(3),
                    i=str(p+k).rjust(4)
                ))
                pk += (p*k)
                s += (str(p*k) + " + ")
            s = s[:-2] + "= " + str(pk)
            print(s)
        else:
            return sum( [ m.total_energy() for m in self.moon_list])
        
    def check_equal(self, ax):
        for m1,m2 in zip(self.moon_list,self.moon_list_orig):
            if m1['pos'][ax] != m2['pos'][ax] or m1['vel'][ax] != m2['vel'][ax]:
                return False
        return True
    
    def steps_to_origin(self):
        each = []
        for ax in 'xyz':
            self.idx =0
            self.moon_list = deepcopy(self.moon_list_orig)
            self.step(on_ax=ax)
            while True:
                if self.check_equal(ax):
                    each.append(self.idx)
                    break
                else:
                    self.step(on_ax=ax)
        return np.lcm.reduce(each)
