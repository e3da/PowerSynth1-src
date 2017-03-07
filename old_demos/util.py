'''
Author:      Brett Shook; bxs003@uark.edu

Desc:        Some basic utility functions
             Uniform random numbers
             Distance for n dimensions
             
Created:     Apr 30, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''

import random
import math

class Rect:
    def __init__(self, top, bottom, left, right):
        self.t = top
        self.b = bottom
        self.l = left
        self.r = right
        
    def __str__(self):
        return str(self.t)+', '+str(self.b)+', '+str(self.l)+', '+str(self.r)
        
    def intersects(self, rect):
        return not(self.l >= rect.r or rect.l >= self.r or rect.b >= self.t or self.b >= rect.t)
    
    def intersection(self, rect):
        if not self.intersects(rect):
            return None
        
        horiz = [self.l, self.r, rect.l, rect.r]
        horiz.sort()
        vert = [self.b, self.t, rect.b, rect.t]
        vert.sort()
        
        return Rect(vert[2], vert[1], horiz[1], horiz[2])
    
    def encloses(self, x, y):
        if x >= self.l and x <= self.r and y >= self.b and y <= self.t:
            return True
        else:
            return False
    
    def translate(self, dx, dy):
        self.t += dy
        self.b += dy
        self.l += dx
        self.r += dx
    
    def area(self):
        return (self.t - self.b)*(self.r - self.l)
    
    def width(self):
        return self.r - self.l
    
    def height(self):
        return self.t - self.b
    
    def deepCopy(self):
        rect = Rect(self.t, self.b, self.l, self.r)
        return rect
    
    def top(self):
        return self.t
    
    def bottom(self):
        return self.b
        
    def left(self):
        return self.l
        
    def right(self):
        return self.r

# Seed the random module
def seed_rand():
    random.seed()

# Generate a random number in the range
def rand(num_range):
    return random.uniform(num_range[0], num_range[1])


def distance(x1, x2):
    dist = 0
    for i in range(len(x1)):
        dist += math.pow(x2[i] - x1[i], 2)
        
    dist = math.sqrt(dist)
    return dist