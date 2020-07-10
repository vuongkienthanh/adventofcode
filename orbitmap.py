class Obj_map(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def populate(self, text):
        for line in text.split():
            x1,_,x2 = line.partition(')')
            Obj(x2, x1)
    
    def total_orbits(self):
        total = 0
        for obj in self.values():
            total += obj.total()
        return total
    
    def get_num_transfer(self, a, b):
        a = Obj_dict.get(a).get_parent_list()
        b = Obj_dict.get(b).get_parent_list()
        if len(b) < len(a):
            a,b = b,a
        c = 0
        for idx, obj in enumerate(a):
            try:
                c = b.index(obj)
            except:
                continue
            break
        return idx+c
    
class Obj:
    global Obj_dict
    def __init__(self, name, parent):
        self.name = name
        if name not in Obj_dict.keys():
            Obj_dict[name] = self
        else:
            self = Obj_dict[name]
        if parent is not None:
            if parent not in Obj_dict.keys():
                self.parent = Obj(parent,None)
            else:
                self.parent = Obj_dict[parent]
        else:
            self.parent =None
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    @classmethod
    def get(cls,name):
        return Obj_dict[name]
    def direct_orbit(self):
        return 1 if self.parent is not None else 0
    def indirect_orbit(self):
        count = 0
        sw = self.parent
        if sw is None:
            return 0
        while True:
            count += sw.direct_orbit()
            sw = sw.parent
            if sw is None:
                break
        return count
    def total(self):
        return self.direct_orbit() + self.indirect_orbit()
    def get_parent_list(self):
        res = []
        sw = self.parent
        while sw is not None:
            res.append(sw)
            sw = sw.parent
        return res
