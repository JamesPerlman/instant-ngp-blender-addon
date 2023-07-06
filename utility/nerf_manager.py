import bpy

from pathlib import Path

from turbo_nerf.constants import NERF_ITEM_IDENTIFIER_ID
from .dotdict import dotdict
from .pylib import PyTurboNeRF as tn

class NeRFManager():

    _bridge = None
    _manager = None
    _runtime_check_result = None

    @classmethod
    def pylib_version(cls):
        return tn.__version__
    
    @classmethod
    def required_pylib_version(cls):
        return "0.0.14"

    @classmethod
    def is_pylib_compatible(cls):
        return cls.pylib_version() == cls.required_pylib_version()
    
    @classmethod
    def check_runtime(cls):
        if cls._runtime_check_result is not None:
            return cls._runtime_check_result
        
        rm = tn.RuntimeManager()
        cls._runtime_check_result = rm.check_runtime()
        return cls._runtime_check_result

    @classmethod
    def bridge(cls):
        if cls._bridge is None:
            cls._bridge = tn.BlenderBridge()

        return cls._bridge

    @classmethod
    def import_dataset(cls, dataset_path):
        dataset = tn.Dataset(file_path=dataset_path)
        dataset.load_transforms()

        nerf = cls.bridge().create_nerf(dataset)

        return nerf.id

    @classmethod
    def clone(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cloned_nerf = cls.bridge().clone_nerf(nerf)
        return cloned_nerf.id
    
    @classmethod
    def destroy(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.bridge().destroy_nerf(nerf)

    @classmethod
    def load_snapshot(cls, path: Path):
        nerf = cls.mgr.load(str(path.absolute()))
        return cls.add_nerf(nerf)

    @classmethod
    def save_snapshot(cls, nerf_obj: bpy.types.Object, path: Path):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.mgr().save(nerf, str(path.absolute()))

    @classmethod
    def get_all_nerfs(cls):
        return cls.bridge().get_nerfs()
    
    @classmethod
    def is_training(cls):
        return cls.bridge().is_training()

    @classmethod
    def get_training_step(cls):
        return cls.bridge().get_training_step()

    @classmethod
    def can_any_nerf_train(cls):
        return cls.bridge().can_any_nerf_train()
    
    @classmethod
    def is_image_data_loaded(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        return nerf.is_image_data_loaded()

    @classmethod
    def can_load_images(cls, nerf_obj: bpy.types.Object):
        # TODO: need a better way to check if a dataset is loadable
        # return cls.bridge().can_load_images()

        return not cls.is_image_data_loaded(nerf_obj)
    
    @classmethod
    def load_training_images(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)        
        cls.bridge().load_training_images(nerf)
    
    @classmethod
    def start_training(cls):
        cls.bridge().start_training()
    
    @classmethod
    def stop_training(cls):
        cls.bridge().stop_training()

    @classmethod
    def unload_training_images(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.bridge().unload_training_images(nerf)

    @classmethod
    def enable_training(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.bridge().enable_training(nerf)
    
    @classmethod
    def disable_training(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.bridge().disable_training(nerf)
    
    @classmethod
    def reset_training(cls, nerf_obj: bpy.types.Object):
        nerf = cls.get_nerf_for_obj(nerf_obj)
        cls.bridge().reset_training(nerf)

    @classmethod
    def toggle_training(cls):
        if cls.is_training():
            cls.stop_training()
        else:
            cls.start_training()
    @classmethod
    def get_nerf_by_id(cls, nerf_id: int) -> tn.NeRF:
        return cls.bridge().get_nerf(nerf_id)
    
    @classmethod
    def get_nerf_for_obj(cls, nerf_obj: bpy.types.Object) -> tn.NeRF:
        nerf_id = nerf_obj[NERF_ITEM_IDENTIFIER_ID]
        return cls.get_nerf_by_id(nerf_id)
    
    @classmethod
    def set_bridge_object_property(cls, object_name, property_name, value):
        obj = getattr(cls.bridge(), object_name, None)
        if obj is None:
            return

        setattr(obj, property_name, value)
    
    @classmethod
    def get_bridge_object_property(cls, object_name, property_name, default=None):
        obj = getattr(cls.bridge(), object_name, None)
        if obj is None:
            return default

        return getattr(obj, property_name, default)
    
    @classmethod
    def bridge_obj_prop_setter(cls, obj_name, prop_name):
        def setter(self: bpy.types.PropertyGroup, value):
            cls.set_bridge_object_property(obj_name, prop_name, value)
        
        return setter
    
    @classmethod
    def bridge_obj_prop_getter(cls, obj_name, prop_name, default):
        def getter(self: bpy.types.PropertyGroup):
            return cls.get_bridge_object_property(obj_name, prop_name, default)
        
        return getter
