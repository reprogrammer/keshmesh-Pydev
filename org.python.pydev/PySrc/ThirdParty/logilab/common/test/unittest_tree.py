"""
unit tests for module logilab.common.tree
squeleton generated by /home/syt/bin/py2tests on Jan 20 at 10:43:25
"""
__revision__ = "$Id: unittest_tree.py,v 1.1 2005-01-21 17:46:21 fabioz Exp $"

import unittest
from logilab.common.tree import *

tree = ('root', (
    ('child_1_1', (
    ('child_2_1', ()), ('child_2_2', (
    ('child_3_1', ()),)))),
    ('child_1_2', (('child_2_3', ()),))))

def make_tree(tuple):
    n = Node(tuple[0])
    for child in tuple[1]:
        n.append(make_tree(child))
    return n
    
class Node_ClassTest(unittest.TestCase):
    """ a basic tree node, caracterised by an id"""
    def setUp(self):
        """ called before each test from this class """        
        self.o = make_tree(tree)
    def test_known_values_remove(self):
        """ 
        remove a child node
        """
        self.o.remove(self.o.get_node_by_id('child_1_1'))
        self.assertRaises(NodeNotFound, self.o.get_node_by_id, 'child_1_1')
    
    def test_known_values_replace(self):
        """
        replace a child node with another
        """
        self.o.replace(self.o.get_node_by_id('child_1_1'), Node('hoho'))
        self.assertRaises(NodeNotFound, self.o.get_node_by_id, 'child_1_1')
        self.assertEqual(self.o.get_node_by_id('hoho'), self.o.children[0])
    
    def test_known_values_get_sibling(self):
        """
        return the sibling node that has given id
        """
        self.assertEqual(self.o.children[0].get_sibling('child_1_2'), self.o.children[1], None)
    
    def test_raise_get_sibling_NodeNotFound(self):
        self.assertRaises(NodeNotFound, self.o.children[0].get_sibling, 'houhou')
    
    def test_known_values_get_node_by_id(self):
        """
        return node in whole hierarchy that has given id
        """
        self.assertEqual(self.o.get_node_by_id('child_1_1'), self.o.children[0])
    
    def test_raise_get_node_by_id_NodeNotFound(self):
        self.assertRaises(NodeNotFound, self.o.get_node_by_id, 'houhou')
    
    def test_known_values_get_child_by_id(self):
        """
        return child of given id
        """
        self.assertEqual(self.o.get_child_by_id('child_2_1', recurse=1), self.o.children[0].children[0])
    
    def test_raise_get_child_by_id_NodeNotFound(self):
        self.assertRaises(NodeNotFound, self.o.get_child_by_id, nid='child_2_1')
        self.assertRaises(NodeNotFound, self.o.get_child_by_id, 'houhou')
    
    def test_known_values_get_child_by_path(self):
        """
        return child of given path (path is a list of ids)
        """
        self.assertEqual(self.o.get_child_by_path(['root', 'child_1_1', 'child_2_1']), self.o.children[0].children[0])
    
    def test_raise_get_child_by_path_NodeNotFound(self):
        self.assertRaises(NodeNotFound, self.o.get_child_by_path, ['child_1_1', 'child_2_11'])
    
    def test_known_values_depth(self):
        """
        return depth of this node in the tree
        """
        self.assertEqual(self.o.depth(), 0)
        self.assertEqual(self.o.get_child_by_id('child_2_1',1).depth(), 2)
    
    def test_known_values_root(self):
        """
        return the root node of the tree
        """
        self.assertEqual(self.o.get_child_by_id('child_2_1', 1).root(), self.o)
    
    def test_known_values_leafs(self):
        """
        return a list with all the leaf nodes descendant from this task
        """
        self.assertEqual(self.o.leafs(), [self.o.get_child_by_id('child_2_1',1),
                                          self.o.get_child_by_id('child_3_1',1),
                                          self.o.get_child_by_id('child_2_3',1)])
    

    
class post_order_list_FunctionTest(unittest.TestCase):
    """"""
    def setUp(self):
        """ called before each test from this class """
        self.o = make_tree(tree)

    def test_known_values_post_order_list(self):
        """ 
        create a list with tree nodes for which the <filter> function returned true
        in a post order foashion
        """
        L = ['child_2_1', 'child_3_1', 'child_2_2', 'child_1_1', 'child_2_3', 'child_1_2', 'root']
        l = [n.id for n in post_order_list(self.o)]
        self.assertEqual(l, L, l)

    def test_known_values_post_order_list2(self):
        """ 
        create a list with tree nodes for which the <filter> function returned true
        in a post order foashion
        """
        def filter(node):
            if node.id == 'child_2_2':
                return 0
            return 1
        L = ['child_2_1', 'child_1_1', 'child_2_3', 'child_1_2', 'root']
        l = [n.id for n in post_order_list(self.o, filter)]
        self.assertEqual(l, L, l)

    
class PostfixedDepthFirstIterator_ClassTest(unittest.TestCase):
    """"""
    def setUp(self):
        """ called before each test from this class """
        self.o = make_tree(tree)

    def test_known_values_next(self):
        L = ['child_2_1', 'child_3_1', 'child_2_2', 'child_1_1', 'child_2_3', 'child_1_2', 'root']
        iter = PostfixedDepthFirstIterator(self.o)
        o = iter.next()
        i = 0
        while o:
            self.assertEqual(o.id, L[i])
            o = iter.next()
            i += 1
        
    
class pre_order_list_FunctionTest(unittest.TestCase):
    """"""
    def setUp(self):
        """ called before each test from this class """
        self.o = make_tree(tree)
    
    def test_known_values_pre_order_list(self):
        """ 
        create a list with tree nodes for which the <filter> function returned true
        in a pre order fashion
        """
        L = ['root', 'child_1_1', 'child_2_1', 'child_2_2', 'child_3_1', 'child_1_2', 'child_2_3']
        l = [n.id for n in pre_order_list(self.o)]
        self.assertEqual(l, L, l)

    def test_known_values_pre_order_list2(self):
        """ 
        create a list with tree nodes for which the <filter> function returned true
        in a pre order fashion
        """
        def filter(node):
            if node.id == 'child_2_2':
                return 0
            return 1
        L = ['root', 'child_1_1', 'child_2_1', 'child_1_2', 'child_2_3']
        l = [n.id for n in pre_order_list(self.o, filter)]
        self.assertEqual(l, L, l)


class PrefixedDepthFirstIterator_ClassTest(unittest.TestCase):
    """"""
    def setUp(self):
        """ called before each test from this class """
        self.o = make_tree(tree)

    def test_known_values_next(self):
        L = ['root', 'child_1_1', 'child_2_1', 'child_2_2', 'child_3_1', 'child_1_2', 'child_2_3']
        iter = PrefixedDepthFirstIterator(self.o)
        o = iter.next()
        i = 0
        while o:
            self.assertEqual(o.id, L[i])
            o = iter.next()
            i += 1

       
if __name__ == '__main__':
    unittest.main()
