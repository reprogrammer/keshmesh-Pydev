# pylint: disable-msg=R0903
"""test class members"""

__revision__ = ''

class MyClass:
    """class docstring"""
    
    def __init__(self):
        """init"""
        self.correct = 1

    def test(self):
        """test"""
        self.correct += 2
        self.incorrect += 2
        self.nonexistent1.truc()
        self.nonexistent2[1] = 'hehe'

class XYZMixin:
    """access to undefined members should be ignored in mixin classes by 
    default
    """ 
    def __init__(self):
        print self.nonexistent
