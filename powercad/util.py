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
    TOP_SIDE = 1
    BOTTOM_SIDE = 2
    RIGHT_SIDE = 3
    LEFT_SIDE = 4
    
    def __init__(self, top=0.0, bottom=0.0, left=0.0, right=0.0):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        
    def __str__(self):
        return str(self.top)+', '+str(self.bottom)+', '+str(self.left)+', '+str(self.right)
    
    def set_pos_dim(self, x, y, width, length):
        self.top = y+length
        self.bottom = y
        self.left = x
        self.right = x+width
        
    def intersects(self, rect):
        return not(self.left > rect.right or rect.left > self.right or rect.bottom > self.top or self.bottom > rect.top)
    
    def intersects_contact_excluded(self, rect):
        return not(self.left >= rect.right or rect.left >= self.right or rect.bottom >= self.top or self.bottom >= rect.top)
    
    def intersection(self, rect):
        if not self.intersects(rect):
            return None
        
        horiz = [self.left, self.right, rect.left, rect.right]
        horiz.sort()
        vert = [self.bottom, self.top, rect.bottom, rect.top]
        vert.sort()
        
        return Rect(vert[2], vert[1], horiz[1], horiz[2])
    
    def encloses(self, x, y):
        if x >= self.left and x <= self.right and y >= self.bottom and y <= self.top:
            return True
        else:
            return False
    
    def translate(self, dx, dy):
        self.top += dy
        self.bottom += dy
        self.left += dx
        self.right += dx
    
    def area(self):
        return (self.top - self.bottom)*(self.right - self.left)
    
    def width(self):
        return self.right - self.left
    
    def height(self):
        return self.top - self.bottom
    
    def center(self):
        return 0.5*(self.right+self.left), 0.5*(self.top+self.bottom)
    
    def center_x(self):
        return 0.5*(self.right+self.left)
    
    def center_y(self):
        return 0.5*(self.top+self.bottom)
        
    def normal(self):
        # Returns False if the rectangle has any non-realistic dimensions
        if self.top < self.bottom:
            return False
        elif self.right < self.left:
            return False
        else:
            return True
        
    def scale(self, factor):
        self.top *= factor
        self.bottom *= factor
        self.left *= factor
        self.right *= factor
        
    def change_size(self, amount):
        # Changes the size of the rectangle on all sides by the size amount
        self.top += amount
        self.bottom -= amount
        self.right += amount
        self.left -= amount
        
    def find_contact_side(self, rect):
        # Returns the side which rect is contacting
        # Return -1 if not in contact
        side = -1
        if self.top == rect.bottom:
            side = self.TOP_SIDE
        elif self.bottom == rect.top:
            side = self.BOTTOM_SIDE
        elif self.right == rect.left:
            side = self.RIGHT_SIDE
        elif self.left == rect.right:
            side = self.LEFT_SIDE
        return side
    
    def find_pt_contact_side(self, pt):
        # Returns the side which pt is contacting
        # Return -1 if pt not in contact
        hside = -1
        vside = -1
        if self.top == pt[1]:
            vside = self.TOP_SIDE
        elif self.bottom == pt[1]:
            vside = self.BOTTOM_SIDE
        if self.right == pt[0]:
            hside = self.RIGHT_SIDE
        elif self.left == pt[0]:
            hside = self.LEFT_SIDE
        return hside, vside
    
    def deepCopy(self):
        rect = Rect(self.top, self.bottom, self.left, self.right)
        return rect

# Seed the random module
def seed_rand(num):
    random.seed(num)

# Generate a random number in the range
def rand(num_range):
    return random.uniform(num_range[0], num_range[1])

def distance(x1, x2):
    dist = 0
    for i in range(len(x1)):
        dist += math.pow(x2[i] - x1[i], 2)
        
    dist = math.sqrt(dist)
    return dist

def complex_rot_vec(theta_deg):
    theta = theta_deg*(math.pi/180)
    return complex(math.cos(theta), math.sin(theta))

def translate_pt(pt, *args):
    if len(pt) > len(args):
        return None
    
    ret_pt = []
    for i in xrange(len(args)):
        ret_pt.append(pt[i]+args[i])
        
    return tuple(ret_pt)

def get_overlap_interval(interval1, interval2):
    return (max(interval1[0], interval2[0]), min(interval1[1], interval2[1]))

if __name__ == '__main__':
    rect = Rect(2.0, 0.0, 0.0, 2.0)
    rect2 = Rect(2.0, 0.0, 0.0, 2.0)
    inter = rect.intersection(rect2)
    if inter is not None:
        print inter.area()
    else:
        print 'weird'