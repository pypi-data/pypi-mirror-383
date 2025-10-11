import uuid
import sys
import importlib.util

modules = {}


def import_by_path(path, name=None, module_name=None):
    module_name = module_name or f'abc_{uuid.uuid4().hex}'

    package_module = modules.get(module_name, None)
    if package_module is None:
        spec = importlib.util.spec_from_file_location(module_name, path)
        package_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = package_module
        spec.loader.exec_module(package_module)
        modules[module_name] = package_module
    if name is not None:
        return getattr(package_module, name)
    else:
        return package_module


def create_instance_by_classname(module, class_name, *args, **kwargs):
    """从模块中通过类名字符串创建实例"""
    cls = getattr(module, class_name, None)
    if cls is None:
        raise AttributeError(f"Class '{class_name}' not found in module {module.__name__}")
    if not callable(cls):
        raise TypeError(f"{class_name} is not a class")
    return cls(*args, **kwargs)


def call_method_by_name(instance, method_name, *args, **kwargs):
    """通过方法名字符串调用实例方法"""
    method = getattr(instance, method_name, None)
    if method is None:
        raise AttributeError(f"Method '{method_name}' not found in instance")
    return method(*args, **kwargs)


if __name__ == '__main__':
    a = import_by_path('log_setting.py')
    log3 = getattr(a, 'LoggerWriter')('DEBUG')
