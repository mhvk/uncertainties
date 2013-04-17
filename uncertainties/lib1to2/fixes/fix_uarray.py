'''
Fixer for lib2to3.

Transforms uarray(tuple) into uarray(nominal_values, std_devs) and
uarray(single_arg) into uarray(*single_arg).

(c) 2013 by Eric O. LEBIGOT (EOL).
'''

from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import String, ArgList, Comma

###############################################################################
# lib2to3 grammar parts.

#! Warning: indentation is meaningful!

# (tuple):
tuple_call = """
        trailer< '('
            atom< '(' testlist_gexp< arg0=any ',' arg1=any > ')' >
        ')' >"""


###############################################################################

class FixUarray(BaseFix):

    # Non dotted access, then dotted access.
    # Tuple call, then single-argument call
    PATTERN = """
        power< 'uarray' {tuple_call} any* >
        |
        power< object=NAME trailer< '.' 'uarray' > {tuple_call} any* >
        |
        power< 'uarray' trailer< '(' arg=any ')' > any* >
        |
        power< object=NAME trailer< '.' 'uarray' >
            trailer< '(' arg=any ')' >
        any* >
        """.format(tuple_call=tuple_call)

    
    def transform(self, node, results):

        if 'object' in results:  # If dotted access: unc.uarray()
            args = node.children[2]
        else:
            args = node.children[1]

        if 'arg' in results: # Non-tuple argument

            # A star will be inserted in from of the single argument:
            
            # ! The following keeps spaces in front of the argument,
            # if any (but this is safer than adding forcefully a star
            # in front of the value of the argument: the argument can
            # be a name (where it works), but also anything else,
            # including a lib2to3.pytree.Node that has no value.) This
            # is OK, as the syntax f(* (2, 1)) is valid.
            
            new_args = [String('*'), results['arg'].clone()]
            
        else:  # Tuple argument

            # New arguments:
            new_args = [results['arg0'].clone(),
                        Comma(), results['arg1'].clone()]
            
        # Argument list update:
        args.replace(ArgList(new_args))
