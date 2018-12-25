# -*- coding: utf-8 -*-
"""
A simple l-system
"""
from math import radians
from random import random, seed
from collections import namedtuple
from mathutils import Vector, Matrix
import math as math


Quad = namedtuple('Quad', 'pos, up, right, forward')
Edge = namedtuple('Edge', 'start, end, radius')
BObject = namedtuple('BObject', 'name, pos, up, right, forward')
Branch = namedtuple('number','parent_num,　child_num,　age,　term,　radius,　child_radius_sum')

class Turtle(object):

    def __init__(self,
                 tropism=(0, 0, 0),
                 tropismsize=0,
                 pitch_angle=radians(30),
                 yaw_angle=radians(30),
                 roll_angle=radians(30),
                 radius=0.2,
                 iseed=42):
        self.tropism = Vector(tropism).normalized()
        self.magnitude = tropismsize
        self.forward = Vector((0, 0, 1))
        self.up = Vector((1, 0, 0))
        self.right = Vector((0, 1, 0))#(0,1,0)
        self.stack = []
        self.stack_curly = []
        self.position = Vector((0, 0, 0))
        self.pitch_angle = pitch_angle
        self.yaw_angle = yaw_angle
        self.roll_angle = roll_angle
        self.radius = radius
        self.__init_terminals()
        seed(iseed)

    def __init_terminals(self):
        """
        Initialize a map of predefined terminals.
        """
        self.terminals = {
            '+': self.term_plus,
            '-': self.term_minus,
            '[': self.term_push,
            ']': self.term_pop,
            '(': self.term_push_curly,
            ')': self.term_pop_curly,
            '/': self.term_slash,
            '\\': self.term_backslash,
            '<': self.term_less,
            '>': self.term_greater,
            '&': self.term_amp,
            '!': self.term_expand,
            '@': self.term_shrink,
            '#': self.term_fatten,
            '%': self.term_slink,
            '^': self.term_expand_g,
            '*': self.term_shrink_g,
            '=': self.term_fatten_g,
            '|': self.term_slink_g,
            'F': self.term_edge,
            'Q': self.term_quad,
            'b': self.fai_plus,
            #'d': self.fai_minus,
            #'j': self.sita_plus,
            #'l': self.sita_minus,
            '{': self.term_object
            }


    def fai_plus(self,value=None):
        val = radians(value) if not value is None else self.pitch_angle

        s = self.position.copy()
        r = math.sqrt(s[0]**2 + s[1]**2)
        self.apply_tropism()
        self.position = Vector((r*math.sin(val),r*math.cos(val),0))
        e = self.position.copy()
        #print("b",s," ",e," ",self.radius," ",self.apply_tropism())
        return Edge(start=s, end=e, radius=self.radius)

#==============================================================================
#
#==============================================================================
    def apply_tropism(self):
        # tropism is a normalized vector
        #
        t = self.tropism * self.magnitude #方向＊大きさ
        #print("t::",t)
        tf = self.forward + t
        tf.normalize()
        q = tf.rotation_difference(self.forward)
        #print("q::",q)
        self.forward.rotate(q)
        self.up.rotate(q)
        self.right.rotate(q)

    def term_plus(self, value=None):
        # + y軸正回転
        val = radians(value) if not value is None else self.pitch_angle
        r = Matrix.Rotation(val, 4, self.right)
        #(x,0,0)をrだけ回転させる
        self.forward.rotate(r)
        #(0,0,x)をrだけ回転させる
        self.up.rotate(r)

    def term_minus(self, value=None):
        val = radians(value) if not value is None else self.pitch_angle
        r = Matrix.Rotation(-val, 4, self.right)
        self.forward.rotate(r)
        self.up.rotate(r)

    def term_amp(self, value=30):
        k = (random() - 0.5) * value
        self.term_plus(value=k)
        k = (random() - 0.5) * value
        self.term_slash(value=k)

    def term_slash(self, value=None):
        r = Matrix.Rotation(radians(value) if not value is None
                            else self.yaw_angle, 4, self.up)
        self.forward.rotate(r)
        self.right.rotate(r)

    def term_backslash(self, value=None):
        r = Matrix.Rotation(-radians(value) if not value is None
                            else -self.yaw_angle, 4, self.up)
        self.forward.rotate(r)
        self.right.rotate(r)

    def term_less(self, value=None):
        r = Matrix.Rotation(radians(value) if not value is None
                            else self.roll_angle, 4, self.forward)
        self.up.rotate(r)
        self.right.rotate(r)

    def term_greater(self, value=None):
        r = Matrix.Rotation(-radians(value) if not value is None
                            else -self.roll_angle, 4, self.forward)
        self.up.rotate(r)
        self.right.rotate(r)

    def term_pop(self, value=None):
        t = self.stack.pop()
        (self.forward,
         self.up,
         self.right,
         self.position,
         self.radius) = t

    def term_push(self, value=None):
        t = (self.forward.copy(),
             self.up.copy(),
             self.right.copy(),
             self.position.copy(),
             self.radius)
        self.stack.append(t)

    def term_pop_curly(self, value=None):
        t = self.stack_curly.pop()
        (self.forward,
         self.up,
         self.right,
         self.position,
         self.radius) = t

    def term_push_curly(self, value=None):
        t = (self.forward.copy(),
             self.up.copy(),
             self.right.copy(),
             self.position.copy(),
             self.radius)
        self.stack_curly.append(t)

    expand_shrink_factor = 0.1#節の長さ
    fatten_slink_factor = 0.045
    expand_shrink_factor_g = 0.2#節の太さ
    fatten_slink_factor_g = 0.48

    def term_expand(self, value=1 + expand_shrink_factor):
        self.forward *= value
        self.up *= value
        self.right *= value

    def term_shrink(self, value=1 - expand_shrink_factor):
        self.forward *= value
        self.up *= value
        self.right *= value

    def term_fatten(self, value=1 + fatten_slink_factor):
        self.radius *= value

    def term_slink(self, value=1 - fatten_slink_factor):
        self.radius *= value

    def term_expand_g(self, value=1 + expand_shrink_factor_g):
        self.term_expand(value)

    def term_shrink_g(self, value=1 - expand_shrink_factor_g):
        self.term_shrink(value)

    def term_fatten_g(self, value=1 + fatten_slink_factor_g):
        self.term_fatten(value)

    def term_slink_g(self, value=1 - fatten_slink_factor_g):
        self.term_slink(value)

#==============================================================================
# Fならエッジクラスを返す
#==============================================================================
    def term_edge(self, value=None):# F
        s = self.position.copy()#今のポジション
        self.apply_tropism()
        self.position += self.forward
        e = self.position.copy()#動かした後のポジション
        return Edge(start=s, end=e, radius=self.radius)
#==============================================================================
# Qなら葉クラスを返す
#==============================================================================
    def term_quad(self, value=0.5):
        return Quad(pos=self.position,
                    right=self.right,
                    up=self.up,
                    forward=self.forward)
#==============================================================================
# BObjectクラスを返す
#==============================================================================
    def term_object(self, value=None, name=None):
        s = self.position.copy()
        self.apply_tropism()
        self.position += self.forward
        return BObject(name=name,
                       pos=s,
                       right=self.right,
                       up=self.up,
                       forward=self.forward)
#==============================================================================
# L-systemの文字列を受け取り
#==============================================================================
    def interpret(self, s):
        """
        interpret the iterable s, yield Quad, Edge or Object named tuples.
        文字列ｓを受け取り、Quad Edge Objectを生成する
        """
        print('interpret:', s)
        name = ''
        for c in s:
            t = None
            print(c,name)
            if c == '}':
                t = self.term_object(name=name[1:])
                name = ''
            elif c == '{' or name != '':
                name += c
                continue
            elif name != '':
                continue
            elif c in self.terminals:
                t = self.terminals[c]()
            print('yield',t)
            if not t is None:
                yield t
