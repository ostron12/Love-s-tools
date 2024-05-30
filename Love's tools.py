bl_info = {
    "name": "Love's Tools",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "LoveD",
    "description": "A collection of custom tools for various operations including origin transforms, material management, backdrops, lighting, face orientation toggle, scale checker, and UV checker.",
}

import bpy
import bmesh
import math
import random
from mathutils import Vector

# Origin and Transform Tool Operators
class OBJECT_OT_SetOriginTopZeroTransforms(bpy.types.Operator):
    bl_idname = "object.set_origin_top_zero_transforms"
    bl_label = "Top"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                mesh.verts.ensure_lookup_table()

                top_z = max((obj.matrix_world @ v.co).z for v in mesh.verts)
                
                top_middle = Vector((0, 0, top_z))
                top_middle.x = (max((obj.matrix_world @ v.co).x for v in mesh.verts) + min((obj.matrix_world @ v.co).x for v in mesh.verts)) / 2
                top_middle.y = (max((obj.matrix_world @ v.co).y for v in mesh.verts) + min((obj.matrix_world @ v.co).y for v in mesh.verts)) / 2

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.scene.cursor.location = top_middle
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                obj.location.z = 0.0
                obj.rotation_euler = (0.0, 0.0, 0.0)
                obj.scale = (1.0, 1.0, 1.0)
                
                self.report({'INFO'}, f"Origin set to top and {obj.name} placed over grid")
        
        return {'FINISHED'}

class OBJECT_OT_SetOriginMiddleZeroTransforms(bpy.types.Operator):
    bl_idname = "object.set_origin_middle_zero_transforms"
    bl_label = "Middle"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                
                obj.location.z = 0.0
                obj.location.x = 0.0
                obj.location.y = 0.0
                obj.rotation_euler = (0.0, 0.0, 0.0)
                obj.scale = (1.0, 1.0, 1.0)
                
                self.report({'INFO'}, f"Origin set to middle and {obj.name} placed over grid")
        
        return {'FINISHED'}

class OBJECT_OT_SetOriginBottomZeroTransforms(bpy.types.Operator):
    bl_idname = "object.set_origin_bottom_zero_transforms"
    bl_label = "Bottom"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                mesh.verts.ensure_lookup_table()

                bottom_z = min(v.co.z for v in mesh.verts)
                
                bottom_middle = Vector((0, 0, bottom_z))
                bottom_middle.x = (max(v.co.x for v in mesh.verts) + min(v.co.x for v in mesh.verts)) / 2
                bottom_middle.y = (max(v.co.y for v in mesh.verts) + min(v.co.y for v in mesh.verts)) / 2

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.scene.cursor.location = obj.matrix_world @ bottom_middle
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                obj.location.z = 0.0
                obj.rotation_euler = (0.0, 0.0, 0.0)
                obj.scale = (1.0, 1.0, 1.0)
                
                self.report({'INFO'}, f"Origin set to bottom and {obj.name} placed over grid")
        
        return {'FINISHED'}

# Material Tools Operators
class OBJECT_OT_DeleteAllMaterials(bpy.types.Operator):
    bl_idname = "object.delete_all_materials"
    bl_label = "Delete All Materials from Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()
                self.report({'INFO'}, f"Deleted all materials from {obj.name}")
        
        return {'FINISHED'}

class OBJECT_OT_DeleteAllMaterialsScene(bpy.types.Operator):
    bl_idname = "object.delete_all_materials_scene"
    bl_label = "Delete All Materials from Scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()
        self.report({'INFO'}, "Deleted all materials from the entire scene")
        
        return {'FINISHED'}

# Backdrop and Lighting Operators
def create_open_box(width, depth, height, angle, subsurf_level):
    vertices = [
        (width / 2, depth / 2, 0),  # Bottom vertices
        (width / 2, -depth / 2, 0),
        (-width / 2, -depth / 2, 0),
        (-width / 2, depth / 2, 0),
        (width / 2, depth / 2, height),   # Top vertices
        (width / 2, -depth / 2, height),
        (-width / 2, -depth / 2, height),
        (-width / 2, depth / 2, height)
    ]
    
    faces = [
        (3, 2, 1, 0),  # Bottom face
        (3, 0, 4, 7)   # +Y face
    ]

    mesh = bpy.data.meshes.new(name="OpenBoxMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name="OpenBox", object_data=mesh)
    bpy.context.collection.objects.link(obj)

    subsurf_modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf_modifier.levels = subsurf_level
    subsurf_modifier.render_levels = subsurf_level
    subsurf_modifier.subdivision_type = 'SIMPLE'

    bevel_modifier = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel_modifier.width = 0.25
    bevel_modifier.segments = 4

    empty = bpy.data.objects.new("Rotation", None)
    empty.location = (0, 0, 0)
    empty.rotation_euler[2] = -3.14159  # Rotate -180 degrees around Z-axis
    bpy.context.collection.objects.link(empty)

    simple_deform_modifier = obj.modifiers.new(name="SimpleDeform", type='SIMPLE_DEFORM')
    simple_deform_modifier.deform_axis = 'Z'
    simple_deform_modifier.deform_method = 'BEND'
    simple_deform_modifier.angle = angle
    simple_deform_modifier.origin = empty

    obj.location.z = 0

    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    material = bpy.data.materials.new(name="GreyMaterial")
    material.diffuse_color = (0.6549, 0.6549, 0.6549, 1)  # A7A7A7 in RGB
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

def point_light_at_object(light, target_location):
    direction = target_location - light.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    light.rotation_euler = rot_quat.to_euler()
    light.rotation_euler.rotate_axis('X', math.radians(180))

def create_three_point_lighting_around_object(obj, key_light_strength=1000, fill_light_strength=500, back_light_strength=800):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT':
            obj.select_set(True)
    bpy.ops.object.delete()

    location = obj.location

    bpy.ops.object.light_add(type='AREA', location=(location.x + 4, location.y - 4, location.z + 6))
    key_light = bpy.context.object
    key_light.data.energy = key_light_strength
    key_light.data.size = 2
    key_light.name = "Key_Light"
    point_light_at_object(key_light, location)

    bpy.ops.object.light_add(type='AREA', location=(location.x - 4, location.y - 4, location.z + 2))
    fill_light = bpy.context.object
    fill_light.data.energy = fill_light_strength
    fill_light.data.size = 2
    fill_light.name = "Fill_Light"
    point_light_at_object(fill_light, location)

    bpy.ops.object.light_add(type='AREA', location=(location.x - 4, location.y + 4, location.z + 6))
    back_light = bpy.context.object
    back_light.data.energy = back_light_strength
    back_light.data.size = 2
    back_light.name = "Back_Light"
    point_light_at_object(back_light, location)

class OBJECT_OT_CreateOpenBox(bpy.types.Operator):
    bl_idname = "object.create_open_box"
    bl_label = "Create Open Box"
    bl_options = {'REGISTER', 'UNDO'}

    width: bpy.props.FloatProperty(name="Width", default=4.0)
    depth: bpy.props.FloatProperty(name="Depth", default=3.0)
    height: bpy.props.FloatProperty(name="Height", default=3.0)
    angle: bpy.props.FloatProperty(name="Angle", default=1.5708)  # Default to 90 degrees in radians
    subsurf_level: bpy.props.IntProperty(name="Subdivision Level", default=3)  # Default to 3

    def execute(self, context):
        create_open_box(self.width, self.depth, self.height, self.angle, self.subsurf_level)
        return {'FINISHED'}

class OBJECT_OT_CreateThreePointLighting(bpy.types.Operator):
    bl_idname = "object.create_three_point_lighting"
    bl_label = "Create Three-Point Lighting"
    bl_options = {'REGISTER', 'UNDO'}
    
    key_light_strength: bpy.props.FloatProperty(name="Key Light Strength", default=1000, min=0)
    fill_light_strength: bpy.props.FloatProperty(name="Fill Light Strength", default=500, min=0)
    back_light_strength: bpy.props.FloatProperty(name="Back Light Strength", default=800, min=0)

    def execute(self, context):
        obj = context.active_object
        if obj is not None:
            create_three_point_lighting_around_object(
                obj,
                key_light_strength=self.key_light_strength,
                fill_light_strength=self.fill_light_strength,
                back_light_strength=self.back_light_strength
            )
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}

# Function to create materials based on object names for selected objects
def create_materials_for_selected_objects(prefix="", ignore_prefix="", add_suffix=True):
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        if obj.type == 'MESH':
            obj_name = obj.name
            if ignore_prefix and obj_name.startswith(ignore_prefix):
                obj_name = obj_name[len(ignore_prefix):]

            material_name = f"{prefix}{obj_name}"
            if add_suffix:
                material_name += "_Material"

            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            for node in nodes:
                nodes.remove(node)

            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = 0, 0

            material_output = nodes.new(type='ShaderNodeOutputMaterial')
            material_output.location = 200, 0

            links = mat.node_tree.links
            links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

            random_color = (random.random(), random.random(), random.random(), 1)
            bsdf.inputs['Base Color'].default_value = random_color

            print(f"Created material '{material_name}' and assigned to '{obj.name}'")

class OBJECT_OT_CreateMaterials(bpy.types.Operator):
    bl_label = "Create Materials for Selected"
    bl_idname = "object.create_materials"
    bl_description = "Create materials for selected objects based on their names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_materials_for_selected_objects(add_suffix=False)
        return {'FINISHED'}

class OBJECT_OT_CreateMaterialsPrefixed(bpy.types.Operator):
    bl_label = "Create Materials with Prefix"
    bl_idname = "object.create_materials_prefixed"
    bl_description = "Create materials for selected objects with a custom prefix, ignoring 'SM_' prefix in object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        custom_prefix = context.scene.custom_material_prefix or "M_"
        create_materials_for_selected_objects(prefix=custom_prefix, ignore_prefix="SM_", add_suffix=False)
        return {'FINISHED'}

# Toggle Face Orientation Operator
def turn_off_face_orientation():
    bpy.context.space_data.overlay.show_face_orientation = False
    bpy.ops.object.report_message('INVOKE_DEFAULT', message="Face Orientation turned off.")
    return None  # Stops the timer

class OBJECT_OT_ToggleFaceOrientation(bpy.types.Operator):
    bl_idname = "object.toggle_face_orientation"
    bl_label = "Toggle Face Orientation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        current_state = bpy.context.space_data.overlay.show_face_orientation
        bpy.context.space_data.overlay.show_face_orientation = not current_state
        
        if not current_state:
            bpy.app.timers.register(turn_off_face_orientation, first_interval=10.0)
        
        return {'FINISHED'}

# Check Scale Operator
class OBJECT_OT_CheckScale(bpy.types.Operator):
    bl_idname = "object.check_scale"
    bl_label = "Check Scale"
    bl_options = {'REGISTER', 'UNDO'}
    
    incorrect_scale_objs = []

    def execute(self, context):
        self.incorrect_scale_objs.clear()

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if not (obj.scale.x == 1.0 and obj.scale.y == 1.0 and obj.scale.z == 1.0):
                    self.incorrect_scale_objs.append(obj.name)
        
        if self.incorrect_scale_objs:
            self.report({'WARNING'}, f"Objects with wrong scale: {', '.join(self.incorrect_scale_objs)}")
            bpy.context.window_manager.popup_menu(self.draw_result, title="Scale Check", icon='ERROR')
        else:
            self.report({'INFO'}, "All mesh objects have a scale of (1, 1, 1).")
            bpy.context.window_manager.popup_menu(self.draw_result, title="Scale Check", icon='INFO')
        
        return {'FINISHED'}

    def draw_result(self, menu, context):
        layout = menu.layout
        if self.incorrect_scale_objs:
            layout.label(text="Wrong Scale:")
            for obj_name in self.incorrect_scale_objs:
                layout.label(text=obj_name)
        else:
            layout.label(text="Scale Status: Correct")

# Toggle UV Checker Operator
class OBJECT_OT_ToggleUVChecker(bpy.types.Operator):
    bl_idname = "object.toggle_uv_checker"
    bl_label = "Toggle UV Checker"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        checker_material = bpy.data.materials.get("UVChecker")
        if not checker_material:
            checker_material = bpy.data.materials.new(name="UVChecker")
            checker_material.use_nodes = True
            nodes = checker_material.node_tree.nodes
            links = checker_material.node_tree.links

            for node in nodes:
                nodes.remove(node)

            checker_texture = nodes.new(type='ShaderNodeTexChecker')
            checker_texture.inputs['Scale'].default_value = 10.0

            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            material_output = nodes.new(type='ShaderNodeOutputMaterial')

            links.new(checker_texture.outputs['Color'], bsdf.inputs['Base Color'])
            links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        toggle_off = all("UVChecker" in [mat.name for mat in obj.data.materials] for obj in bpy.data.objects if obj.type == 'MESH')
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if toggle_off:
                    obj.data.materials.clear()
                else:
                    if "UVChecker" not in [mat.name for mat in obj.data.materials]:
                        obj.data.materials.append(checker_material)

        return {'FINISHED'}

# Report Message Operator
class OBJECT_OT_ReportMessage(bpy.types.Operator):
    bl_idname = "object.report_message"
    bl_label = "Report Message"
    bl_options = {'INTERNAL'}
    
    message: bpy.props.StringProperty()
    
    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

# Check Unassigned Polygons Operator
class MESH_OT_CheckUnassigned(bpy.types.Operator):
    """Check mesh for unassigned polygons"""
    bl_idname = "mesh.check_unassigned"
    bl_label = "Check Unassigned"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        mesh = obj.data
        vertex_groups = obj.vertex_groups

        if not vertex_groups:
            self.report({'INFO'}, "Mesh has no vertex groups")
            return {'FINISHED'}

        # Create a set of vertices that are in vertex groups
        vertices_in_groups = set()
        for v in mesh.vertices:
            if v.groups:
                vertices_in_groups.add(v.index)

        # Check unassigned polygons
        unassigned_faces = [f.index for f in mesh.polygons if all(vert not in vertices_in_groups for vert in f.vertices)]

        if unassigned_faces:
            # Select unassigned polygons
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            for face_index in unassigned_faces:
                mesh.polygons[face_index].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            self.report({'INFO'}, f"Unassigned Polygons: {len(unassigned_faces)}")
        else:
            self.report({'INFO'}, "All polygons are assigned to vertex groups")

        return {'FINISHED'}

# Unified Panel
class OBJECT_PT_LovesTools(bpy.types.Panel):
    bl_label = "Love's Tools"
    bl_idname = "OBJECT_PT_loves_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Love's Tools"
    
    def draw(self, context):
        layout = self.layout
        
        # Origin and Transform Tools
        layout.label(text="Origin and Transform Tools")
        row = layout.row()
        row.operator("object.set_origin_top_zero_transforms", text="Top")
        row = layout.row()
        row.operator("object.set_origin_middle_zero_transforms", text="Middle")
        row = layout.row()
        row.operator("object.set_origin_bottom_zero_transforms", text="Bottom")
        
        layout.separator()
        
        # Material Tools
        layout.label(text="Material Tools")
        row = layout.row()
        row.operator("object.delete_all_materials", text="Delete All Materials from Selected")
        row = layout.row()
        row.operator("object.delete_all_materials_scene", text="Delete All Materials from Scene")
        
        layout.separator()
        
        # Backdrop Tools
        layout.label(text="Backdrop Tools")
        col = layout.column()
        operator = col.operator("object.create_open_box", text="Backdrop 4x3x3")
        operator.width = 4.0
        operator.depth = 3.0
        operator.height = 3.0
        operator.angle = 1.5708  # 90 degrees in radians
        operator.subsurf_level = 3
        
        operator = col.operator("object.create_open_box", text="Backdrop 6x3x3")
        operator.width = 6.0
        operator.depth = 3.0
        operator.height = 3.0
        operator.angle = 1.5708  # 90 degrees in radians
        operator.subsurf_level = 3
        
        operator = col.operator("object.create_open_box", text="Backdrop 8x5x5")
        operator.width = 8.0
        operator.depth = 5.0
        operator.height = 5.0
        operator.angle = 3.14159  # 180 degrees in radians
        operator.subsurf_level = 5
        
        operator = col.operator("object.create_open_box", text="Backdrop 10x5x5")
        operator.width = 10.0
        operator.depth = 5.0
        operator.height = 5.0
        operator.angle = 3.14159  # 180 degrees in radians
        operator.subsurf_level = 5
        
        col.operator("object.create_three_point_lighting", text="Three-Point Lighting")

        layout.separator()

        # Material Creator Tools
        layout.label(text="Material Creator")
        row = layout.row()
        row.operator("object.create_materials", text="Create Materials for Selected")
        row = layout.row()
        row.operator("object.create_materials_prefixed", text="Create Materials with Prefix")
        row = layout.row()
        row.prop(context.scene, "custom_material_prefix", text="Custom Prefix")

        layout.separator()

        # Face Orientation Toggle
        row = layout.row()
        row.operator("object.toggle_face_orientation", text="Toggle Face Orientation")

        # Scale Checker
        row = layout.row()
        row.operator("object.check_scale", text="Check Scale")

        # UV Checker
        row = layout.row()
        row.operator("object.toggle_uv_checker", text="Toggle UV Checker")

        # Check Unassigned Polygons
        row = layout.row()
        row.operator("mesh.check_unassigned", text="Check Unassigned Polygons")

# Register and Unregister Classes
def register():
    bpy.utils.register_class(OBJECT_OT_SetOriginTopZeroTransforms)
    bpy.utils.register_class(OBJECT_OT_SetOriginMiddleZeroTransforms)
    bpy.utils.register_class(OBJECT_OT_SetOriginBottomZeroTransforms)
    bpy.utils.register_class(OBJECT_OT_DeleteAllMaterials)
    bpy.utils.register_class(OBJECT_OT_DeleteAllMaterialsScene)
    bpy.utils.register_class(OBJECT_OT_CreateOpenBox)
    bpy.utils.register_class(OBJECT_OT_CreateThreePointLighting)
    bpy.utils.register_class(OBJECT_OT_CreateMaterials)
    bpy.utils.register_class(OBJECT_OT_CreateMaterialsPrefixed)
    bpy.utils.register_class(OBJECT_OT_ToggleFaceOrientation)
    bpy.utils.register_class(OBJECT_OT_CheckScale)
    bpy.utils.register_class(OBJECT_OT_ToggleUVChecker)
    bpy.utils.register_class(OBJECT_OT_ReportMessage)
    bpy.utils.register_class(MESH_OT_CheckUnassigned)
    bpy.utils.register_class(OBJECT_PT_LovesTools)
    bpy.types.Scene.custom_material_prefix = bpy.props.StringProperty(
        name="Custom Material Prefix",
        description="Prefix to add to material names",
        default="M_"
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_SetOriginTopZeroTransforms)
    bpy.utils.unregister_class(OBJECT_OT_SetOriginMiddleZeroTransforms)
    bpy.utils.unregister_class(OBJECT_OT_SetOriginBottomZeroTransforms)
    bpy.utils.unregister_class(OBJECT_OT_DeleteAllMaterials)
    bpy.utils.unregister_class(OBJECT_OT_DeleteAllMaterialsScene)
    bpy.utils.unregister_class(OBJECT_OT_CreateOpenBox)
    bpy.utils.unregister_class(OBJECT_OT_CreateThreePointLighting)
    bpy.utils.unregister_class(OBJECT_OT_CreateMaterials)
    bpy.utils.unregister_class(OBJECT_OT_CreateMaterialsPrefixed)
    bpy.utils.unregister_class(OBJECT_OT_ToggleFaceOrientation)
    bpy.utils.unregister_class(OBJECT_OT_CheckScale)
    bpy.utils.unregister_class(OBJECT_OT_ToggleUVChecker)
    bpy.utils.unregister_class(OBJECT_OT_ReportMessage)
    bpy.utils.unregister_class(MESH_OT_CheckUnassigned)
    bpy.utils.unregister_class(OBJECT_PT_LovesTools)
    del bpy.types.Scene.custom_material_prefix

if __name__ == "__main__":
    register()
