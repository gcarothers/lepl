

# what happens when we pass various things to []?

class CheckSlice():
    
    def __getattr__(self, attr):
        self.dump('__getattr__', attr)
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            raise AttributeError()
        
#    def __getslice__(self, *attr):
#        self.dump('__getslice__', attr)
        
    def __getitem__(self, *attr):
        self.dump('__getitem__', *attr)
        
    def dump(self, name, value):
        print(name, value)
        print(type(value))
        print(dir(value))
    
    def callable(self, *args, **kargs):
        print(args)
        print(kargs)
        
    def run(self):
        print("1")
        self[1]
        print("1:2")
        self[1:2]
        print("'a':'b'")
        self['a':'b']
        print("1:2:3")
        self[1:2:3]
        print("'a':'b':'c'")
        self['a':'b':'c']
        print("...")
        self[...]
        print("...,1:")
        self[...,1:]
        print("::")
        self[::]
        

class CheckReturnYield():
    
    def counter(self, n, direct):
        if direct:
            for i in range(n):
                yield i
        else:
            # this does not compile
            #return self.indirect(n)
            pass
        
    def indirect(self, n):
        for i in range(n):
            yield i
            
    def run(self):
        c = self.counter(3, True)
        print(type(c))
        for i in c:
            print(i)
        c = self.counter(3, False)
        print(type(c))
        for i in c:
            print(i)
            
            
class CheckGeneratorProxy():
    
    def __getattr__(self, name):
        return getattr(self.target, name)
    
    def run(self):
        self.target = Numbers()
        for i in self.numbers():
            print(i)

class Numbers():
    
    def numbers(self):
        for i in range(5):
            yield i

        

if __name__ == '__main__':
    #CheckSlice().run()
    #CheckReturnYield().run()
    CheckGeneratorProxy().run()
    