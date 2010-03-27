
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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
Tests for the lepl.core.parser module.
'''

from traceback import format_exc
from types import MethodType
from unittest import TestCase

from lepl import Literal, Any, function_matcher


# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, E1101
# (dude this is just a test)

    
class InstanceMethodTest(TestCase):
    
    class Foo(object):
        class_attribute = 1
        def __init__(self):
            self.instance_attribute = 2
        def bar(self):
            return (self.class_attribute,
                    self.instance_attribute,
                    hasattr(self, 'baz'))

    def test_method(self):
        foo = self.Foo()
        assert foo.bar() == (1, 2, False)
        def my_baz(myself):
            return (myself.class_attribute,
                    myself.instance_attribute,
                    hasattr(myself, 'baz'))
        # pylint: disable-msg=W0201
        foo.baz = MethodType(my_baz, foo)
        assert foo.baz() == (1, 2, True)
        assert foo.bar() == (1, 2, True)


    
class FlattenTest(TestCase):
    def test_flatten(self):
        matcher = Literal('a') & Literal('b') & Literal('c')
        assert str(matcher) == "And(And, Literal)", str(matcher)
        matcher.config.clear().flatten()
        parser = matcher.get_parse_string()
        assert str(parser.matcher) == "And(Literal, Literal, Literal)", str(parser.matcher)


class RepeatTest(TestCase):
    
    def test_depth(self):
        matcher = Any()[:,...]
        matcher.config.full_first_match(False)
        matcher = matcher.get_match_string()
        print(repr(matcher.matcher))
        results = [m for (m, _s) in matcher('abc')]
        assert results == [['abc'], ['ab'], ['a'], []], results

    def test_breadth(self):
        matcher = Any()[::'b',...]
        matcher.config.full_first_match(False)
        matcher = matcher.get_match_string()
        results = [m for (m, _s) in matcher('abc')]
        assert results == [[], ['a'], ['ab'], ['abc']], results


class ErrorTest(TestCase):
    
    def test_error(self):
        class TestException(Exception): pass
        @function_matcher
        def Error(supprt, stream):
            raise TestException('here')
        matcher = Error()
        try:
            matcher.parse('a')
        except TestException:
            trace = format_exc()
            assert "TestException('here')" in trace, trace
            