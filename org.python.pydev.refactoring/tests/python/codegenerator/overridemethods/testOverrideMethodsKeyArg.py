class A:
    def foo(self, arg=123):
        print "foo"

class B(A):
    try:
        print "foo"
    finally:
        print "done."
    
    anAttribute = "hello"  
    
    def myMethod(self):
        print self.anAttribute
        
a = A()
a.myMethod()

##c
'''
<config>
  <classSelection>0</classSelection>
  <methodSelection>
    <int>0</int>
  </methodSelection>
  <offsetStrategy>4</offsetStrategy>
  <editClass>1</editClass>
</config>
'''

##r
class A:
    def foo(self, arg=123):
        print "foo"

class B(A):
    try:
        print "foo"
    finally:
        print "done."
    
    anAttribute = "hello"  
    
    def myMethod(self):
        print self.anAttribute

    def foo(self, arg=123):
        return A.foo(self, arg)

        
a = A()
a.myMethod()