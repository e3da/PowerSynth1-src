'''
Created on Oct 10, 2012

@author: pxt002
'''

class Solution:
    def __init__(self, name='', index=None, params=None):
        """Describes a solution saved from the Solution Browser
        
        Keyword arguments:
        name -- solution name
        index -- sym_layout solution index
        params -- list of objectives in tuples (name, unit, value)
        """
        self.name = name
        self.index = index
        self.params = params