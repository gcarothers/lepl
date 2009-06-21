
from lepl.bin.bits import BitString
from lepl.bin.literal import parse
from lepl._example.support import Example


class ParseExample(Example):
    
    def test_parse(self):
        '''
        An 803.3 MAC frame - see http://en.wikipedia.org/wiki/Ethernet
        '''
        b = parse('''
Frame(
  Header(
    preamble  = 0b10101010*7,
    start     = 0b10101011,
    destn     = 123456x0,
    source    = 890abcx0,
    ethertype = 0800x0
  ),
  Data(1/8,2/8,3/8,4/8),
  CRC(234d0/4.)
)
''')
        print(b)
        
        
class RepresentationExample(Example):
    
    def test_representation(self):
        self._assert(0b101100, '00110100 00000000 00000000 00000000')
        self._assert('0b101100', '001101')
        self._assert('001101b0', '001101')
        self._assert(0o073, '11011100 00000000 00000000 00000000')
        self._assert('0o073', '11011100 0')
        self._assert('073o0', None)
        self._assert('0o01234567', '11101110 10011100 10100000') #!
        self._assert('01234567o0', '10100000 10011100 11101110')
        self._assert(1980, '00111101 11100000 00000000 00000000')
        self._assert('0d1980', '00111101 11100000 00000000 00000000')
        self._assert('1980', '00111101 11100000 00000000 00000000')
        self._assert('1980d0', '00000000 00000000 11100000 00111101')
        self._assert(0xfe01, '10000000 01111111 00000000 00000000')        
        self._assert('0xfe01', '10000000 01111111')
        self._assert('fe01x0', '01111111 10000000')
        
    def _assert(self, repr, value):
        try:
            b = BitString.from_int(repr)
            assert str(b) == value + 'b0/' + str(len(b)), str(b)
        except ValueError:
            assert value is None
            
        