# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" Copyright (c) 2002-2005 LOGILAB S.A. (Paris, FRANCE).
 http://www.logilab.fr/ -- mailto:contact@logilab.fr

 basic checker for Python code

 FIXME : should check constant names !
"""

__revision__ = "$Id: base.py,v 1.3 2005-01-21 17:42:08 fabioz Exp $"

from logilab.common import astng
from logilab.common.ureports import Table

from logilab.pylint.interfaces import IASTNGChecker
from logilab.pylint.reporters import diff_string
from logilab.pylint.checkers import BaseChecker
from logilab.pylint.checkers.utils import are_exclusive

import re

# regex for class/function/variable/constant nane
CLASS_NAME_RGX = re.compile('[A-Z_][a-zA-Z0-9]+$')
FUNC_NAME_RGX = re.compile('[a-z_][a-z0-9_]*$')
METH_NAME_RGX = re.compile('[a-z_][a-z0-9_]*$')
VAR_NAME_RGX = re.compile('[a-z_][a-z0-9_]*$')
MOD_NAME_RGX = re.compile('(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$')
#CST_NAME_RGX = re.compile('[A-Z_][A-Z1-9_]*')

# do not require a doc string on system methods
NO_REQUIRED_DOC_RGX = re.compile('__.*__')

del re

def in_nested_list(nested_list, obj):
    """return true if the object is an element of <nested_list> or of a nested
    list
    """
    for elmt in nested_list:
        if isinstance(elmt, (list, tuple)):
            if in_nested_list(elmt, obj):
                return True
        elif elmt == obj:
            return True
    return False

MSGS = {
    'E0101': ('Explicit return in __init__',
              'Used when the special class method __ini__ has an explicit \
              return value.'),    
    'E0102': ('%s already defined line %s',
              'Used when a function / class / method is redefined.'),

    'W0101': ('Unreachable code',
              'Used when there is some code behind a "return" or "raise" \
              statement, which will never be accessed.'),
    'W0102': ('Dangerous default value %s as argument',
              'Used when a mutable value as list or dictionary is detected in \
              a default value for an argument.'),
    'W0103': ('Missing required attribute "%s"',
              'Used when an attribute required for modules is missing.'),
    
    'W0121': ('Use of the global statement',
              'Used when you use the "global" statement, to discourage its \
              usage. That doesn\'t mean you can not use it !'),
    'W0122': ('Use of the exec statement',
              'Used when you use the "exec" statement, to discourage its \
              usage. That doesn\'t mean you can not use it !'),
    
    'W0131': ('Missing docstring',
              'Used when a module, function, class or method has no docstring.\
              Some special methods like __init__ doesn\'t necessary require a \
              docstring.'),
    'W0132': ('Empty docstring',
              'Used when a module, function, class or method has an empty \
              docstring (it would be to easy ;).'),

    'W0141': ('Used builtin function %r',
              'Used when a black listed builtin function is used (see the \
              bad-function option). Usual black listed functions are the ones \
              like map, or filter , where Python offers now some cleaner \
              alternative like list comprehension.'),
    'W0142': ('Used * or ** magic',
              'Used when a function or method is called using `*args` or \
              `**kwargs` to dispatch arguments. This doesn\'t improve readility\
               and should be used with care.'),

    'C0101': ('Too short name "%s"',
              'Used when a variable has a too short name.'),
    'C0102': ('Black listed name "%s"',
              'Used when the name is listed in the black list (unauthorized \
              names).'),
    'C0103': ('Invalid name "%s" (should match %s)',
              'Used when the name doesn\'t match the regular expression \
              associated to its type (constant, variable, class...).'),
    
    }

class BasicChecker(BaseChecker):
    """checks for :                                                            
    * doc strings                                                              
    * modules / classes / functions / methods / arguments / variables name     
    * number of arguments, local variables, branchs, returns and statements in
functions, methods                                                       
    * required module attributes                                             
    * dangerous default values as arguments                                    
    * redefinition of function / method / class                                
    * uses of the global statement                                             
    """
    
    __implements__ = IASTNGChecker

    name = 'basic'
    msgs = MSGS
    priority = -1
    options = (('required-attributes',
                {'default' : ('__revision__',), 'type' : 'csv',
                 'metavar' : '<attributes>',
                 'help' : 'Required attributes for module, separated by a '
                          'comma'}
                ),
               ('no-docstring-rgx',
                {'default' : NO_REQUIRED_DOC_RGX,
                 'type' : 'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match '
                          'functions or classes name which do not require a '
                          'docstring'}
                ),
               ('min-name-length',
                {'default' : 3, 'type' : 'int', 'metavar' : '<int>',
                 'help': 'Minimal length for module / class / function / '
                         'method / argument / variable names'}
                ),
               ('module-rgx',
                {'default' : MOD_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'module names'}
                ),
               ('class-rgx',
                {'default' : CLASS_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'class names'}
                ),
               ('function-rgx',
                {'default' : FUNC_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'function names'}
                ),
               ('method-rgx',
                {'default' : METH_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'method names'}
                ),
               ('argument-rgx',
                {'default' : VAR_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'argument names'}),
               ('variable-rgx',
                {'default' : VAR_NAME_RGX,
                 'type' :'regexp', 'metavar' : '<regexp>',
                 'help' : 'Regular expression which should only match correct '
                          'variable names'}
                ),
               ('good-names',
                {'default' : ('i', 'j', 'k', 'ex', 'Run', '_'),
                 'type' :'csv', 'metavar' : '<names>',
                 'help' : 'Good variable names which should always be accepted,'
                          ' separated by a comma'}
                ),
               ('bad-names',
                {'default' : ('foo', 'bar', 'baz', 'toto', 'tutu', 'tata'),
                 'type' :'csv', 'metavar' : '<names>',
                 'help' : 'Bad variable names which should always be refused, '
                          'separated by a comma'}
                ),
               
               ('bad-functions',
                {'default' : ('map', 'filter', 'apply', 'input'),
                 'type' :'csv', 'metavar' : '<builtin function names>',
                 'help' : 'List of builtins function names that should not be '
                          'used, separated by a comma'}
                ),
               )

    def __init__(self, linter):
        BaseChecker.__init__(self, linter)
        self.stats = None
        self._returns = None
        self.reports = (('R0101', 'Statistics by type',
                         self.report_by_type_stats),
                        )
        
    def open(self):
        """initialize visit variables and statistics
        """
        self._returns = []
        self.stats = self.linter.add_stats(module=0, constant=0, function=0,
                                           method=0, class_=0, badname_module=0,
                                           badname_class=0, badname_function=0,
                                           badname_method=0, badname_constant=0,
                                           badname_variable=0,
                                           badname_argument=0,
                                           undocumented_module=0,
                                           undocumented_function=0,
                                           undocumented_method=0,
                                           undocumented_class=0)

    def visit_module(self, node):
        """check module name, docstring and required arguments
        """
        self.stats['module'] += 1
        self._check_name('module', node.name.split('.')[-1], node)
        self._check_docstring('module', node)
        self._check_required_attributes(node, self.config.required_attributes)
            
    def visit_class(self, node):
        """check module name, docstring and redefinition
        increment branch counter
        """
        self.stats['class'] += 1
        self._check_name('class', node.name, node)
        if self.config.no_docstring_rgx.match(node.name) is None:
            self._check_docstring('class', node)
        self._check_redefinition('class', node)
            
    def visit_function(self, node):
        """check function name, docstring, arguments, redefinition,
        variable names, max locals
        """
        is_method = node.is_method()
        self._returns.append(0)
        f_type = is_method and 'method' or 'function'
        self.stats[f_type] += 1
        # function name
        self._check_name(f_type, node.name, node)
        # docstring
        if self.config.no_docstring_rgx.match(node.name) is None:
            self._check_docstring(f_type, node)
        # check default arguments'value
        self._check_defaults(node)
        # check arguments name
        args = node.argnames
        self._recursive_check_names(args, node)
        # check local variable, avoiding argument, imported names, global names
        # and current class name if the function is actually a method
        for var, stmt in node.locals.items():
            if (not in_nested_list(args, var)
                and not isinstance(stmt, astng.Import) 
                and not isinstance(stmt, astng.From) 
                and not isinstance(stmt, astng.Global) 
                and not isinstance(stmt, astng.Class) 
                and not (is_method and var == node.parent.get_frame().name)):
                self._check_name('variable', var, stmt)
        # check for redefinition
        self._check_redefinition(is_method and 'method' or 'function', node)

    def leave_function(self, node):
        """most of the work is done here on close:
        checks for max returns, branch, return in __init__
        """
        is_method = node.is_method()
        if is_method and node.name == '__init__' and self._returns.pop():
            self.add_message('E0101', node=node)

    def visit_return(self, node):
        """check is the node has a right sibling (if so, that's some unreachable
        code)
        """
        self._returns[-1] += 1
        self._check_unreachable(node)
        
    def visit_yield(self, _):
        """check is the node has a right sibling (if so, that's some unreachable
        code)
        """
        self._returns[-1] += 1

    def visit_continue(self, node):
        """check is the node has a right sibling (if so, that's some unreachable
        code)
        """
        self._check_unreachable(node)

    def visit_break(self, node):
        """check is the node has a right sibling (if so, that's some unreachable
        code)
        """
        self._check_unreachable(node)

    def visit_raise(self, node):
        """check is the node has a right sibling (if so, that's some unreachable
        code)
        """
        self._check_unreachable(node)

    def visit_global(self, node):
        """just print a warning on global statements"""
        self.add_message('W0121', node=node)
        
    def visit_exec(self, node):
        """just pring a warning on exec statements"""
        self.add_message('W0122', node=node)

    def visit_callfunc(self, node):
        """visit a CallFunc node -> check if this is not a blacklisted builtin
        call and check for * or ** use
        """
        if isinstance(node.node, astng.Name):
            name = node.node.name
            # ignore the name if it's not a builtin (ie not defined in the
            # locals nor globals scope)
            if not (node.get_frame().locals.has_key(name) or
                    node.root().locals.has_key(name)):
                if name in self.config.bad_functions:
                    self.add_message('W0141', node=node, args=name)
        if node.star_args or node.dstar_args:
            self.add_message('W0142', node=node.node)
            

    def _check_unreachable(self, node):
        """check unreachable code"""
        unreach_stmt = node.next_sibling()
        if unreach_stmt is not None:
            self.add_message('W0101', node=unreach_stmt)
        
    def _check_redefinition(self, redef_type, node):
        """check for redefinition of a function / method / class name"""
        defined_self = node.parent.get_frame().locals[node.name]
        if defined_self is not node and not are_exclusive(node, defined_self):
            self.add_message('E0102', node=node,
                             args=(redef_type, defined_self.lineno))
        
    def _check_docstring(self, node_type, node):
        """check the node has a non empty docstring"""
        docstring = node.doc
        if docstring is None:
            self.stats['undocumented_'+node_type] += 1
            self.add_message('W0131', node=node)
        elif not docstring.strip():
            self.stats['undocumented_'+node_type] += 1
            self.add_message('W0132', node=node)
            
    def _recursive_check_names(self, args, node):
        """check names in a possibly recursive list <arg>"""
        for arg in args:
            if type(arg) is type(''):
                self._check_name('argument', arg, node)
            else:
                self._recursive_check_names(arg, node)
    
    def _check_name(self, node_type, name, node):
        """check for a name using the type's regexp"""
        if name in self.config.good_names:
            return
        if name in self.config.bad_names:
            self.stats['badname_' + node_type] += 1
            self.add_message('C0102', node=node, args=name)
            return
        regexp = getattr(self.config, node_type + '_rgx')
        if regexp.match(name) is None:
            self.add_message('C0103', node=node, args=(name, regexp.pattern))
            self.stats['badname_' + node_type] += 1
        elif len(name) < self.config.min_name_length:
            self.add_message('C0101', node=node, args=name)
            self.stats['badname_' + node_type] += 1

    def _check_defaults(self, node):
        """check for dangerous default values as arguments"""
        for default in node.defaults:
            if default.__class__ is astng.Name:
                try:
                    value = node.resolve(default.name)
                except astng.ResolveError:
                    continue
            else:
                value = default
            if value.__class__ in (astng.Dict, astng.List):
                if value is default:
                    msg = default.as_string()
                else:
                    msg = '%s (%s)' % (default.as_string(), value.as_string())
                self.add_message('W0102', node=node, args=(msg,))
        
    def _check_required_attributes(self, node, attributes):
        """check for required attributes"""
        locs = node.locals
        for attr in attributes:
            if not locs.has_key(attr):
                self.add_message('W0103', node=node, args=attr)

    def report_by_type_stats(self, sect, stats, old_stats):
        """make a report of
    
        * percentage of different types documented
        * percentage of different types with a bad name
        """
        # percentage of different types documented and/or with a bad name
        nice_stats = {} 
        for node_type in ('module', 'class', 'method', 'function'):
            nice_stats[node_type] = {}
            total = stats[node_type]
            if total == 0:
                doc_percent = 0
                badname_percent = 0
            else:
                documented = total - stats['undocumented_'+node_type]
                doc_percent = float((documented)*100) / total
                badname_percent = (float((stats['badname_'+node_type])*100)
                                   / total)
            nice_stats[node_type]['percent_documented'] = doc_percent
            nice_stats[node_type]['percent_badname'] = badname_percent
        
##         for node_type in ('constant', ):#'variable', 'argument'):
##             nice_stats[node_type] = {}
##             total = stats[node_type]
##             if total == 0:
##                 badname_percent = 0
##             else:
##                 badname = stats['badname_'+node_type]
##                 badname_percent = float((badname)*100) / total
##             nice_stats[node_type]['percent_badname'] = badname_percent
        lines = ('type', 'number', 'old number', 'difference',
                 '%documented', '%badname')
        for node_type in ('module', 'class', 'method', 'function'):
            new = stats[node_type]
            old = old_stats.get(node_type, None)
            if old is not None:
                diff_str = diff_string(old, new)
            else:
                old, diff_str = 'NC', 'NC'
            lines += (node_type, str(new), str(old), diff_str,
                      '%.2f' % nice_stats[node_type]['percent_documented'],
                      '%.2f' % nice_stats[node_type]['percent_badname'])

        sect.append(Table(children=lines, cols=6, rheaders=1))

    
def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(BasicChecker(linter))

