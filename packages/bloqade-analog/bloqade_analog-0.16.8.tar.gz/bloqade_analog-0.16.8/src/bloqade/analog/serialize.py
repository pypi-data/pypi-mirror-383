import pkgutil
import importlib
from typing import Any

import simplejson as json
from beartype import beartype
from beartype.typing import Dict, Type, Union, TextIO, Callable
from typing_extensions import dataclass_transform

__bloqade_package_loaded__ = False


def _import_submodules(package, recursive=True):
    """Import all submodules of a module, recursively,
    including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """

    if isinstance(package, str):
        package = importlib.import_module(package)

    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        try:
            importlib.import_module(full_name)
        except ModuleNotFoundError:
            continue
        if recursive and is_pkg:
            _import_submodules(full_name)


def load_bloqade():

    # call this function to load all modules in this package
    # required because if no other modules are imported, the
    # Various classes will not be registered with Serializer
    # and the serialization will fail. only need to call this
    # function once per process hence the flag to prevent
    # multiple calls

    if not __bloqade_package_loaded__:
        _import_submodules("bloqade.analog")

        globals()["__bloqade_package_loaded__"] = True


class Serializer(json.JSONEncoder):
    types = ()
    type_to_str = {}
    str_to_type = {}
    serializers = {}
    deserializers = {}

    @staticmethod
    @beartype
    @dataclass_transform()
    def register(cls: Type) -> Type:
        @beartype
        def _deserializer(d: Dict[str, Any]) -> cls:
            return cls(**d)

        @beartype
        def _serializer(obj: cls) -> Dict[str, Any]:
            return obj.__dict__

        @beartype
        def set_serializer(f: Callable):
            # TODO: check function signature
            setattr(cls, "__bloqade_serializer__", staticmethod(f))
            Serializer.serializers[cls] = cls.__bloqade_serializer__

        @beartype
        def set_deserializer(f: Callable):
            # TODO: check function signature
            setattr(cls, "__bloqade_deserializer__", staticmethod(f))
            Serializer.deserializers[cls] = cls.__bloqade_deserializer__

        type_name = f"{cls.__module__}.{cls.__name__}"
        Serializer.type_to_str[cls] = type_name
        Serializer.str_to_type[type_name] = cls
        Serializer.types += (cls,)
        setattr(cls, "set_serializer", staticmethod(beartype(set_serializer)))
        setattr(cls, "set_deserializer", staticmethod(beartype(set_deserializer)))
        cls.set_deserializer(_deserializer)
        cls.set_serializer(_serializer)

        return cls

    @classmethod
    def object_hook(cls, d: Any) -> Any:
        if isinstance(d, dict) and len(d) == 1:
            ((key, value),) = d.items()
            if key in cls.str_to_type:
                obj_cls = cls.str_to_type[key]
                deserialize = cls.deserializers.get(obj_cls)

                return deserialize(value)

        return d

    def default(self, o: Any) -> Any:
        if type(o) in self.serializers:
            cls = type(o)
            serializer = self.serializers.get(cls)

            return {self.type_to_str[cls]: serializer(o)}

        return super().default(o)


@beartype
def loads(s: str, use_decimal: bool = True, **json_kwargs):
    """Load object from string

    Args:
        s (str): the string to load
        use_decimal (bool, optional): use decimal.Decimal for numbers. Defaults to True.
        **json_kwargs: other arguments passed to json.loads

    Returns:
        Any: the deserialized object
    """
    load_bloqade()
    return json.loads(
        s, object_hook=Serializer.object_hook, use_decimal=use_decimal, **json_kwargs
    )


@beartype
def load(fp: Union[TextIO, str], use_decimal: bool = True, **json_kwargs):
    """Load object from file

    Args:
        fp (Union[TextIO, str]): the file path or file object
        use_decimal (bool, optional): use decimal.Decimal for numbers. Defaults to True.
        **json_kwargs: other arguments passed to json.load

    Returns:
        Any: the deserialized object
    """
    load_bloqade()
    if isinstance(fp, str):
        with open(fp, "r") as f:
            return json.load(
                f,
                object_hook=Serializer.object_hook,
                use_decimal=use_decimal,
                **json_kwargs,
            )
    else:
        return json.load(
            fp,
            object_hook=Serializer.object_hook,
            use_decimal=use_decimal,
            **json_kwargs,
        )


@beartype
def dumps(
    o: Any,
    use_decimal: bool = True,
    **json_kwargs,
) -> str:
    """Serialize object to string

    Args:
        o (Any): the object to serialize
        use_decimal (bool, optional): use decimal.Decimal for numbers. Defaults to True.
        **json_kwargs: other arguments passed to json.dumps

    Returns:
        str: the serialized object as a string
    """
    if not isinstance(o, Serializer.types):
        raise TypeError(
            f"Object of type {type(o)} is not JSON serializable. "
            f"Only {Serializer.types} are supported."
        )
    return json.dumps(o, cls=Serializer, use_decimal=use_decimal, **json_kwargs)


@beartype
def save(
    o: Any,
    fp: Union[TextIO, str],
    use_decimal=True,
    **json_kwargs,
) -> None:
    """Serialize object to file

    Args:
        o (Any): the object to serialize
        fp (Union[TextIO, str]): the file path or file object
        use_decimal (bool, optional): use decimal.Decimal for numbers. Defaults to True.
        **json_kwargs: other arguments passed to json.dump

    Returns:
        None
    """
    if not isinstance(o, Serializer.types):
        raise TypeError(
            f"Object of type {type(o)} is not JSON serializable. "
            f"Only {Serializer.types} are supported."
        )
    if isinstance(fp, str):
        with open(fp, "w") as f:
            json.dump(o, f, cls=Serializer, use_decimal=use_decimal, **json_kwargs)
    else:
        json.dump(o, fp, cls=Serializer, use_decimal=use_decimal, **json_kwargs)
