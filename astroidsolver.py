from collections import defaultdict
import numpy as np
class AstroidSolver():
    '''
    coord system is positive in upper right
    use row, col instead of y, x
    '''
    def __init__(self, data):
        self.map = self.astroid_map(data)
        self.count_max = 0
        self.pos_max = None
        self.info = {}

    def astroid_map(self, data):
        m = np.array([list(x) for x in data.split()])
        m = np.where(m=='.',0,1)
        return m

    def degree(self, row1, col1, row2, col2):
        o1, o2 = 1, 0
        v1, v2 = col2-col1, row1-row2
        cos = (o1*v1 + o2*v2)/(np.sqrt(o1**2+o2**2) * np.sqrt(v1**2+v2**2))
        d = np.arccos(cos)
        d = np.rad2deg(d)
        if v2 < o2:
            d = 360 -d
        return np.round(d,2)

    def get_astroids(self):
        return zip(*np.where(self.map==1))
    
    def get_angle_dict(self, row1, col1):
        res = defaultdict(lambda : [])
        for row2, col2 in self.get_astroids():
            if row1 == row2 and col1==col2:
                continue
            else:
                angle = self.degree(row1, col1, row2, col2)
                res[angle].append( (row2, col2))
        return res
    
    def get_count_max(self):
        for row1,col1 in self.get_astroids():
            self.info[(row1, col1)] = self.get_angle_dict(row1, col1)
        m = max(self.info.items(), key=lambda x : len(x[1]))
        self.count_max = len(m[1])
        self.pos_max = m[0]
        print("max_count=",self.count_max, "\nmax_position(row,col)=", self.pos_max)
    
    def transform_coord(self, deg_arr):
        deg_arr = np.array(deg_arr)
        deg_arr = 90 - deg_arr
        deg_arr = np.where(deg_arr<0, deg_arr+360, deg_arr)
        return deg_arr
    
    def distance_from(self, row1, col1):
        def f(row2, col2):
            return np.sqrt((row2-row1)**2 + (col2-col1)**2)
        return f
        
    def vaporize(self, pos=None):
        if self.count_max == 0:
                self.get_count_max()
        if pos is None:
            pos = self.pos_max
            
        astro = self.info[pos]
        astro2 = astro.copy()
        kill_list = []
        dist_calc = self.distance_from(pos[0], pos[1])
        
        while len(astro2) >0:
            for deg in sorted(astro2.keys(), key=self.transform_coord):
                target = min(astro2[deg], key=lambda x: dist_calc(x[0], x[1]))
                astro2[deg].remove(target)
                kill_list.append(target)
                if len(astro2[deg]) ==0:
                    del astro2[deg]
        return kill_list
