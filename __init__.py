# -*- coding: utf-8 -*-
bl_info = {
    "name": "New Lsystem Object polar",
    "author": "Michel Anders (varkenvarken)",
    "version": (1, 0),
    "blender": (2, 5, 5),
    "location": "View3D > Add > Mesh > New Lsystem polar",
    "description": "Adds a new Lsystem Object polar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}


from math import radians
from random import random, seed
import bpy
from bpy.types import Operator
from bpy.props import (FloatProperty,
                       FloatVectorProperty,
                       IntProperty,
                       StringProperty)
from mathutils import Vector, Matrix
from .lsystem_polar import Turtle, Edge, Quad


def nupdate(self, context):

    for n in range(self.nproductions):
        namep = 'prod' + str(n + 1)
        namem = 'mod' + str(n + 1)

        try:
            s = getattr(self, namep)
        except AttributeError:
            setattr(
                self.__class__,
                namep,
                StringProperty(
                    name=namep,
                    description="replacement string")
            )
        try:
            s = getattr(self, namem)
        except AttributeError:
            setattr(
                self.__class__,
                namem,
                StringProperty(
                    name=str(n + 1),
                    description="a single character module",
                    maxlen=1)
            )


class OBJECT_OT_add_lsystem(Operator):#Blenderに追加するクラス
    """Add an L-system Object"""
    bl_idname = "mesh.add_lsystem_polar"#名前
    bl_label = "Add Lsystem Object polar"
    bl_description = "Create a new Lsystem Object polar"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    nproductions = IntProperty(
        name="productions",#Blender画面上でのproductionの数
        min=0,
        max=50,
        update=nupdate)

    niterations = IntProperty(
        name="iterations",
        min=0,
        max=20)

    zyukei = StringProperty(name ="樹形")

    seed = IntProperty(name="seed")

    start = StringProperty(name='start')

    radius = FloatProperty(
        name='radius',
        default=0.2,
        description="radius")

    pitch_angle = FloatProperty(
        name='pitch_angle',
        default=radians(30),
        subtype='ANGLE',
        description="size in degrees of pitch operators: +-")

    yaw_angle = FloatProperty(
        name='yaw_angle',
        default=radians(30),
        subtype='ANGLE',
        description="size in degrees of yaw operators: /\\")

    roll_angle = FloatProperty(
        name='roll_angle',
        default=radians(30),
        subtype='ANGLE',
        description="size in degrees of roll operators: <>")

    tropism = FloatVectorProperty(
        name='tropism',
        subtype='DIRECTION',
        description="direction of tropism")

    tropismsize = FloatProperty(
        name='tropism size',
        description="size of tropism")

#==============================================================================
# L-systemの置換
#==============================================================================
    def iterate(self):
        s = self.start #初期規則
        #prod = {}
        #for i in range(self.nproductions):
            #namep = 'prod' + str(i + 1)
            #namem = 'mod' + str(i + 1)
            #prod[getattr(self, namem)] = getattr(self, namep)
        #for i in range(self.niterations):
            #s = "".join(prod[c] if c in prod else c for c in s)#L-systemの置換
            #print("iterate is",s,i)
        return s

    @staticmethod
    def add_obj(obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        base = scene.objects.link(obj_new)
        return obj_new, base

#==============================================================================
# Turtleで頂点位置を変更して保存
#==============================================================================
    def interpret(self, s, context):
        q = None
        qv = ((0.5, 0, 0), (0.5, 1, 0), (-0.5, 1, 0), (-0.5, 0, 0))
        verts = []
        edges = []
        quads = []
        self.radii = []
        t = Turtle(self.tropism,#lsystem_polar.pyのTurtleに渡す
                   self.tropismsize,
                   self.pitch_angle,
                   self.yaw_angle,
                   self.roll_angle,
                   self.radius,
                   self.seed)
        for e in t.interpret(s):
            """
            tのinterpretにs（文字列）を渡す　
            返り値はQuad Edge Objectのどれか
            """
            if isinstance(e, Edge):"""eがエッジクラスだったら(Fが入力)"""
                # this comprehension is shorter, but is it clearer?
                si, ei = (verts.index(v)
                          if v in verts
                          else (len(verts),
                                verts.append(v),
                                self.radii.append(e.radius))[0]
                          for v in (e.start, e.end))
                #if e.start in verts:
                #   si = verts.index(e.start)
                #else:
                #   si=len(verts)
                #   verts.append(e.start)
                #   self.radii.append(e.radius)
                #if e.end in verts:
                #   ei = verts.index(e.end)
                #else:
                #   ei=len(verts)
                #   verts.append(e.end)
                #   self.radii.append(e.radius)

                edges.append((si, ei))
                #print("edges::",edges)
            #elif isinstance(e, Quad):#eがQuad（葉）クラスだったら(Qが入力)
                #if q is None:
                    #q = bpy.data.meshes.new('lsystem-leaf')
                    #q.from_pydata(qv, [], [(0, 1, 2, 3)])
                    #q.update()
                    #q.uv_textures.new()
                #obj, base = self.add_obj(q, context)
                #r = Matrix()
                #for i in (0, 1, 2):
                    #r[i][0] = e.right[i]
                    #r[i][1] = e.up[i]
                    #r[i][2] = e.forward[i]
                #obj.matrix_world = Matrix.Translation(e.pos) * r
                #quads.append(obj)

        mesh = bpy.data.meshes.new('lsystem_polar')
        #print("verts::",verts)
        mesh.from_pydata(verts, edges, [])#頂点、エッジ、メッシュを登録
        mesh.update()
        obj, base = self.add_obj(mesh, context)
        for ob in context.scene.objects:
            ob.select = False
        base.select = True
        context.scene.objects.active = obj
        for q in quads:
            q.parent = obj
        return base
#=============================================================================
#  実際にモデルを生成し、シェーディングの設定
#=============================================================================
    def execute(self, context):
        s = self.iterate()
        obj = self.interpret(s, context)#オブジェクト生成

        bpy.ops.object.modifier_add(type='SKIN')#SKINモディファイアを設定(線分に肉付け)
        context.active_object.modifiers[0].use_smooth_shade = True #面のシェーディングを滑らかに(無くてもよい)

        skinverts = \
            context.active_object.data.skin_vertices[0].data

        for i, v in enumerate(skinverts):
            v.radius = [self.radii[i], self.radii[i]]
            #print("v[",i,"]=",v)

        bpy.ops.object.modifier_add(type='SUBSURF')#面を分割し滑らかにする
        context.active_object.modifiers[1].levels = 2 #lebels=2は円に近い表示

        return {'FINISHED'}

#==============================================================================
# 生成時に出てくるオペレーターの描画
#==============================================================================
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'nproductions')#Blender画面上でoperatorボックス生成
        box = layout.box()
        if getattr(self, 'start') == '':#もしstartが空欄だったら
            box.alert = True  #アラートを発生
        box.prop(self, 'start')

        for i in range(self.nproductions):#nproductionsの数だけボックス生成
            namep = 'prod' + str(i + 1)
            namem = 'mod' + str(i + 1)

            box = layout.box()
            row = box.row(align=True)
            if getattr(self, namem) == '' or \
               getattr(self, namep) == '':
                    row.alert = True
            row.prop(self, namem)
            row.prop(self, namep, text="")

        box = layout.box()
        box.label(text="Interpretation section")#ボックスのラベル
        box.prop(self, 'niterations')
        box.prop(self, 'zyukei')
        box.prop(self, 'seed')
        box.prop(self, 'radius')
        box.prop(self, 'pitch_angle')
        box.prop(self, 'yaw_angle')
        box.prop(self, 'roll_angle')
        box.prop(self, 'tropism')
        box.prop(self, 'tropismsize')


def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_lsystem.bl_idname,
        text="Lsystem_polar",
        icon='PLUGIN')


def register():
    bpy.utils.register_class(OBJECT_OT_add_lsystem)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)



def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_lsystem)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
