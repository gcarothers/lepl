
from unittest import TestCase

from lepl.repeat import Repeat, RepeatMixin


class RepeatTest(TestCase):

    def test_simple(self):
        self.assert_simple([1], 1, 1, -1, ['0'])
        self.assert_simple([1], 1, 2, -1, ['0'])
        self.assert_simple([2], 1, 1, -1, ['0','1'])
        self.assert_simple([2], 1, 2, -1, ['0','1'])
        self.assert_simple([2], 0, 2, -1, ['0','1', ''])
        self.assert_simple([1,2], 1, 1, -1, ['0'])
        self.assert_simple([1,2], 1, 2, -1, ['00','01', '0'])
        self.assert_simple([1,2], 2, 2, -1, ['00','01'])
        self.assert_simple([1,2], 1, 2, 1, ['0', '00','01'])
        self.assert_simple([1,2,3], 1, None, 2, ['0', '000', '001', '002', '010', '011', '012'])
        self.assert_simple([1,2,3], 1, 3, -2, ['000', '001', '002', '010', '011', '012', '0'])
        
    def assert_simple(self, stream, start, stop, step, target):
        result = [''.join(map(str, l)) 
                  for (l, s) in Repeat(RangeMatch(), start, stop, step)(stream)]
        assert target == result, result
        
    def test_mixin(self):
        r = RangeMatch()
        self.assert_mixin(r[1:1], [1], ['0'])
        self.assert_mixin(r[1:2], [1], ['0'])
        self.assert_mixin(r[1:1], [2], ['0','1'])
        self.assert_mixin(r[1:2], [2], ['0','1'])
        self.assert_mixin(r[0:], [2], ['0','1', ''])
        self.assert_mixin(r[0:2], [2], ['0','1', ''])
        self.assert_mixin(r[1], [1,2], ['0'])
        self.assert_mixin(r[1:2], [1,2], ['00','01', '0'])
        self.assert_mixin(r[2], [1,2], ['00','01'])
        self.assert_mixin(r[1:2:1], [1,2], ['0', '00','01'])
        self.assert_mixin(r[1::2], [1,2,3], ['0', '000', '001', '002', '010', '011', '012'])
        self.assert_mixin(r[1:3:-2], [1,2,3], ['000', '001', '002', '010', '011', '012', '0'])
        try:        
            self.assert_mixin(r[1::-2], [1,2,3], [])
            assert False, 'expected error'
        except ValueError:
            pass
    
    def assert_mixin(self, match, stream, target):
        result = [''.join(map(str, l)) for (l, s) in match(stream)]
        assert target == result, result
       
    
    
class RangeMatch(RepeatMixin):
    '''
    We test repetition by looking at "strings" of integers, where the 
    matcher for any particular value returns all values less than the
    current value. 
    '''
    
    def __call__(self, values):
        if values:
            for i in range(values[0]):
                yield ([i], values[1:])

            