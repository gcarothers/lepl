
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
Matchers that call the regular expression engine.

These are used internally for rewriting; users typically use `Regexp` which
calls the standard Python regular expression library (and so is faster).
'''

from lepl.matchers import Transformable
from lepl.parser import tagged
from lepl.regexp.core import Regexp
from lepl.regexp.unicode import UnicodeAlphabet


class BaseRegexp(Transformable):
    '''
    Common code for all matchers.
    '''
    
    def __init__(self, regexp, alphabet=None):
        super(BaseRegexp, self).__init__()
        self._arg(regexp=regexp)
        self._arg(alphabet=alphabet)
        self.tag(regexp)
        
    def compose(self, transform):
        return self.compose_transformation(transform.function)
    
    def compose_transformation(self, transformation):
        copy = type(self)(self.regexp, self.alphabet)
        copy.function = self.function.compose(transformation)
        return copy
    
    def precompose_transformation(self, transformation):
        copy = type(self)(self.regexp, self.alphabet)
        copy.function = self.function.precompose(transformation)
        return copy
    

class NfaRegexp(BaseRegexp):
    '''
    A matcher for NFA-based regular expressions.  This will yield alternative
    matches.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        super(NfaRegexp, self).__init__(regexp, alphabet)
        self.__matcher = regexp.nfa()

    @tagged
    def __call__(self, stream_in):
        matches = self.__matcher(stream_in)
        for (terminal, match, stream_out) in matches:
            yield self.function([match], stream_in, stream_out)

        

class DfaRegexp(BaseRegexp):
    '''
    A matcher for DFA-based regular expressions.  This yields a single greedy
    match.
    
    Typically used only in specialised situations (see `Regexp`).
    '''
    
    def __init__(self, regexp, alphabet=None):
        alphabet = UnicodeAlphabet.instance() if alphabet is None else alphabet
        if not isinstance(regexp, Regexp):
            regexp = Regexp.single(regexp, alphabet)
        super(DfaRegexp, self).__init__(regexp, alphabet)
        self.__matcher = regexp.dfa()

    @tagged
    def __call__(self, stream_in):
        match = self.__matcher(stream_in)
        if match is not None:
            (terminals, match, stream_out) = match
            yield self.function([match], stream_in, stream_out)
