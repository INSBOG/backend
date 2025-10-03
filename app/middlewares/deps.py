

from functools import wraps


def load_dependencies(*clases):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            instances = []

            for cls in clases:
                if isinstance(cls, tuple):
                    cls_to_instantiate = cls[0]
                    dependencies = [dep() for dep in cls[1:][0]]
                    instance = cls_to_instantiate(*dependencies)
                else:
                    instance = cls()

                instances.append(instance)

            return f(*[instance for instance in instances], *args, **kwargs)
        return wrapper
    return decorator