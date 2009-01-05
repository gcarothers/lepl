
from lepl.support import assert_type


class RepeatMixin():
    '''
    Allows the main class to be modified via the array index / slice syntax:
    [n] - Repeat exactly n times
    [n:m] - Repeat n to m times, starting with n and incrementing
    [n:m:s] - Repeat n, n+s, ... times, with an upper bound of m
    defaults are: n=0, m=infinity, s=1
    '''
    
    def __getitem__(self, index):
        start = 0
        stop = None
        step = 1
        if isinstance(index, int):
            start = index
            stop = index
        elif isinstance(index, slice):
            if index.start != None: start = index.start
            if index.stop != None: stop = index.stop
            if index.step != None: step = index.step
        return Repeat(self, start, stop, step)


class Repeat():
    '''
    Repeats the pattern supplied to the constructor.
    ''' 
    
    def __init__(self, pattern, start=0, stop=None, step=1):
        '''
        A value of None for stop implies no upper bound.
        '''
        self._pattern = pattern
        if start == None: start = 1
        assert_type('The start index for Repeat or [...]', start, int)
        assert_type('The stop index for Repeat or [...]', stop, int, none_ok=True)
        if step == None: step = 1
        assert_type('The index step for Repeat or [...]', step, int)
        if start < 0:
            raise ValueError('Repeat or [...] cannot have a negative start.')
        if stop != None and stop < start:
            raise ValueError('Repeat or [...] must have a stop '
                             'value greater than or equal to the start.')
        if stop == None and step < -1:
            raise ValueError('Repeat or [...] cannot have an open upper '
                             'bound with a decreasing step other than -1.')
        if step == 0:
            raise ValueError('Repeat or [...] must have a non-zero step.')
        self._start = start
        self._stop = stop
        self._step = step
        
    def __call__(self, stream):
        if self._step >= 0:
            return self.__call_up(stream)
        else:
            return self.__call_down(stream)
        
    def __call_up(self, stream):
        '''
        We generate all possibilities in order of increasing numbers of
        matches, so for each call to the underlying pattern we immediately
        examine all possible values (postponing another call as long as
        possible).  Since any of those values could be expanded on later
        we save them in a stack.
        
        Discarding stack duplicates may be a gain in odd circumstances?
        '''
        if 0 == self._start: yield ([], stream)
        stack = [(0, [], stream)]
        while stack:
            # smallest counts first
            (count1, acc1, stream1) = stack.pop(0)
            count2 = count1 + 1
            for (value, stream2) in self._pattern(stream1):
                acc2 = acc1 + value
                if count2 >= self._start and \
                    (self._stop == None or count2 <= self._stop) and \
                    (count2 - self._start) % self._step == 0:
                    yield (acc2, stream2)
                if self._stop == None or count2 + self._step <= self._stop:
                    stack.append((count2, acc2, stream2))

    def __call_down(self, stream):
        '''
        We generate all possibilities in order of decreasing numbers of 
        matches, so we build on calls to the underlying pattern by calling 
        again as soon as we have one value.  Later values (ie the generator
        that supplies later values) are saved on the stack.
        
        Despite that, we still accumulate many (all non-stop) values "on 
        the way".  These are stored for later use.
        '''
        stack = [(0, [], self._pattern(stream))]
        known = {}
        while stack:
            (count1, acc1, generator) = stack[-1]
            try:
                (value, stream2) = next(generator)
                count2 = count1 + 1
                acc2 = acc1 + value
                if count2 == self._stop:
                    yield (acc2, stream2)
                elif count2 >= self._start and \
                    (self._stop == None or \
                        (count2 <= self._stop and \
                        (self._stop - count2) % self._step == 0)):
                    if count2 not in known: known[count2] = []
                    known[count2].append((acc2, stream2))
                stack.append((count2, acc2, self._pattern(stream2)))
            except StopIteration:
                stack.pop(-1)
        counts = list(known.keys())
        counts.sort(reverse=True)
        for count in counts:
            for (acc, stream) in known[count]:
                yield (acc, stream)
