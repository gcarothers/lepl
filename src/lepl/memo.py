
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Memoisation (both as described by Norvig 1991, giving Packrat 
parsers for non-left recursive grammars, and the equivalent described by
Frost and Hafiz 2006 which allows left-recursive grammars to be used.
 
Note that neither paper describes the extension to backtracking with
generators implemented here. 
'''


from itertools import count

from lepl.matchers import BaseMatcher
from lepl.parser import tagged, GeneratorWrapper
from lepl.support import LogMixin


class RMemo(BaseMatcher):
    '''
    A simple memoizer for grammars that do not have left recursion.  Since this
    fails with left recursion it's safer to always use LMemo (this is here
    largely as documentation - the code is non-trivial and it helps to have 
    both cases available).
    '''
    
    def __init__(self, matcher):
        super(RMemo, self).__init__()
        self._arg(matcher=matcher)
        self.__table = {}
        self.tag(self.matcher.describe)
        
    @tagged
    def __call__(self, stream):
        if stream not in self.__table:
            # we have no cache for this stream, so we need to generate the
            # entry.  we do not care about nested calls with the same stream
            # because this memoization is not for left recursion.  that means
            # that we can return a table around this generator immediately.
            self.__table[stream] = RTable(self.matcher(stream))
        return self.__table[stream].generator(self.matcher, stream)


class RTable(LogMixin):
    '''
    Wrap a generator so that separate uses all call the same core generator,
    which is itself tabulated as it unrolls.
    '''
    
    def __init__(self, generator):
        self.__generator = generator
        self.__table = []
        self.__stopped = False
        
    def __read(self, i):
        try:
            while i >= len(self.__table) and not self.__stopped:
                result = yield self.__generator
                self.__table.append(result)
        except StopIteration:
            self._stopped = True
        if i < len(self.__table):
            yield self.__table[i]
        else:
            raise StopIteration()
    
    def generator(self, matcher, stream):
        for i in count():
            yield (yield GeneratorWrapper(self.__read(i), 
                            DummyMatcher(self.__class__.__name__, matcher.describe), 
                            stream))


class DummyMatcher(object):
    
    def __init__(self, outer, inner):
        self.describe = '{0}({1})'.format(outer, inner)
        
        
class LMemo(BaseMatcher):
    '''
    A memoizer for grammars that do have left recursion.
    '''
    
    def __init__(self, matcher):
        super(LMemo, self).__init__()
        self._arg(matcher=matcher)
        self.tag(self.matcher.describe)
        self.__caches = {}
        
    @tagged
    def __call__(self, stream):
        if stream not in self.__caches:
            self.__caches[stream] = PerStreamCache(self.matcher)
        return self.__caches[stream](stream)
        

class PerStreamCache(LogMixin):
    
    def __init__(self, matcher):
        super(PerStreamCache, self).__init__()
        self.__matcher = matcher
        self.__counter = 0
        self.__first = None
        
    def __curtail(self, count, stream):
        if count == 1:
            return False
        else:
            try:
                return not stream.check_len(count)
            except AttributeError:
                return count >= len(stream) 
        
    @tagged
    def __call__(self, stream):
        if not self.__first:
            self.__counter += 1
            if self.__curtail(self.__counter, stream):
                return self.__empty()
            else:
                cache = PerCallCache(self.__matcher(stream))
                if self.__first is None:
                    self.__first = cache
                return cache.generator()
        else:
            return self.__first.view()
        
    def __empty(self):
        if False:
            yield None


class PerCallCache(LogMixin):
    
    def __init__(self, generator):
        super(PerCallCache, self).__init__()
        self.__generator = generator
        self.__cache = []
        self.__returned = False # has an initial match completed?
        self.__complete = False # have all matches completed?
        self.__unstable = False # has a view completed before the matcher?
        
    def view(self):
        '''
        Provide available (cached) values.
        
        This does not generate further values itself - the assumption is that
        generator() has already done this.  I believe that is reasonable
        (the argument is basically that generator was created first, so is
        'above' whatever is using view()), but I do not have a proof.
        
        Note that changing this assumption is non-trivial.  It would be easy
        to have shared access to the generator, but we would need to guarantee
        that the generator is not "in the middle" of generating a new value
        (ie has not been yielded by some earlier, pending call).
        '''
        for value in self.__cache:
            yield value
        self.__unstable = not self.__complete
    
    def generator(self):
        '''
        Expand the underlying generator, storing results.
        '''
        try:
            while True:
                result = yield self.__generator
                if self.__unstable:
#                    self._warn('A view completed before the cache was complete: '
#                               '{0}'.format(self.__generator.describe))
                    raise Exception('A view completed before the cache was '
                                    'complete: {0}'
                                    .format(self.__generator.describe))
                self.__cache.append(result)
                self.__returned = True
                yield result
        finally:
            self.__complete = True
            
    def __bool__(self):
        '''
        Has the underlying call returned?  If so, then we can use the cache.
        If not, then the call tree is still being constructed via left-
        recursive calls.
        '''
        return self.__returned
            
    