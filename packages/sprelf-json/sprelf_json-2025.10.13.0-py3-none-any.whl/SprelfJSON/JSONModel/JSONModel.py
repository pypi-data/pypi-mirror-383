from __future__ import annotations

from abc import ABCMeta, ABC, abstractmethod
from typing import Any, Hashable, Self, Mapping, dataclass_transform, TypeAlias
from types import resolve_bases, new_class, GenericAlias
import typing
import itertools
import inspect

import typing_inspect

from SprelfJSON import JSONArrayLike
from SprelfJSON.JSONModel.ModelElem import ModelElem, ModelElemError, SupportedTypeMap, AlternateModelElem
from SprelfJSON.JSONDefinitions import JSONObject, JSONType, JSONConvertible, JSONContainerLike, JSONValueLike, \
    JSONContainer, JSONValue, JSONLike, JSONObjectLike, JSONArray
from SprelfJSON.JSONModel.JSONModelError import JSONModelError
from SprelfJSON.Helpers import ClassHelpers


#


@dataclass_transform(kw_only_default=True, field_specifiers=(ModelElem,))
class JSONModelMeta(ABCMeta):
    _ANNO = '__annotations__'
    _FIELDS = "_fields"
    _JSON_MODEL = "__json_model__"
    _DEFAULTS = "__defaults__"
    __json_model__: dict[str, ModelElem]
    __name_field__: str = "__name"
    __name_field_required__: bool = False
    __include_name_in_json_output__: bool = False
    __allow_null_json_output__: bool = False
    __include_defaults_in_json_output__: bool = False
    __allow_extra_fields__: bool = False
    __exclusions__: list[str] = []
    __eval_context__ = {**globals(),
                        **SupportedTypeMap,
                        **typing.__dict__,
                        ModelElem.__name__: ModelElem,
                        AlternateModelElem.__name__: AlternateModelElem}
    __annotation_conversions__ = {JSONObject: JSONObjectLike,
                                  JSONArray: JSONArrayLike,
                                  JSONType: JSONLike,
                                  JSONContainer: JSONContainerLike,
                                  JSONValue: JSONValueLike}

    @classmethod
    def _eval(cls, s: Any, context: dict):
        if s is None or inspect.isclass(s) or typing_inspect.is_generic_type(s) or typing_inspect.is_union_type(s) or \
                typing_inspect.is_optional_type(s) or isinstance(s, ModelElem) or type(s) == GenericAlias:
            return s
        try:
            return eval(s, context)
        except:
            if c := ClassHelpers.locate_class(s):
                return c
            raise JSONModelError(f"Unable to evaluate '{s}' as a type; has it been instantiated yet?  Be sure "
                                 f"nested classes are defined before the classes they're nested in, and "
                                 f"avoid circular references.")

    #

    def __new__(mcls: type[JSONModelMeta],
                name: str,
                bases: tuple[type, ...],
                namespace: dict[str, Any],
                **kwargs) -> type:
        _super = super()

        def BUILD(_name, _bases, _namespace):
            # There are a lot of ways to consider building the object; some options are commented out.
            # return type.__new__(mcls, _name, _bases, _namespace)
            # return ABCMeta.__new__(mcls, _name, _bases, _namespace)
            # return new_class(_name, _bases,
            #                  exec_body=lambda ns: ns.update({**_namespace}))
            _bases = resolve_bases(_bases)
            return _super.__new__(mcls, _name, _bases, _namespace)

        #

        if name == "JSONModel":
            new_cls = BUILD(name, bases, namespace)
            return new_cls

        #
        # Retrieve all annotated values and defaults for the class being created and its parents
        #
        given_anno: dict[str, Any] = {}
        defaults: dict[str, Any] = {}

        for base in reversed(bases):
            if hasattr(base, mcls._ANNO):
                given_anno.update(base.__annotations__)
                defaults.update(getattr(base, mcls._DEFAULTS, {}))
            if base == ABC:
                namespace["__name_field_required__"] = True
                namespace["__include_name_in_json_output__"] = True

        given_anno.update(namespace.get(mcls._ANNO, {}))

        defaults.update({key: namespace[key] for key in given_anno.keys() if key in namespace})
        defaults.update({key: elem.default for key, elem in given_anno.items()
                         if isinstance(elem, ModelElem) and elem.has_default()})
        given_anno = {k: v for k, v in given_anno.items() if not k.startswith("_")}
        defaults = {k: v for k, v in defaults.items() if not k.startswith("_")}

        for field in given_anno.keys():
            if hasattr(mcls, field):
                defaults[field] = getattr(mcls, field)

        #
        # Fill in the namespace and build
        #
        namespace = {
            **namespace,
            mcls._DEFAULTS: defaults
        }

        new_cls = BUILD(name, bases, namespace)

        #
        # Parse the annotated strings to get actual types to enforce
        #
        eval_context = {**JSONModelMeta.__eval_context__,
                        **locals(),
                        **{k: v for frame in reversed(inspect.stack()) for k, v in frame.frame.f_locals.items()},
                        new_cls.__name__: new_cls,
                        **{sc.__name__: sc for sc in ClassHelpers.all_subclasses(JSONModel)}}

        evaluated_anno = {k: mcls._eval(v, eval_context)
                          for k, v in given_anno.items()}
        evaluated_anno = {k: mcls.__annotation_conversions__.get(v, v)
                          for k, v in evaluated_anno.items()}

        def _build_model_elem(k, v) -> ModelElem:
            if isinstance(v, ModelElem):
                return v
            d = defaults.get(k, ())
            _orig, _gener = ClassHelpers.analyze_type(v)
            if inspect.isclass(_orig) and any(issubclass(_orig, x) for x in (list, dict, set)):
                if len(d) == 0:
                    return ModelElem(v, default_factory=_orig)
                else:
                    return ModelElem(v, default_factory=lambda: _orig(d))
            return ModelElem(v, default=d)

        full_anno: dict[str, ModelElem] = \
            {k: _build_model_elem(k, v)
             for k, v in evaluated_anno.items()}
        clean_anno = {k: v.annotated_type for k, v in full_anno.items()}
        required = [n for n in full_anno.keys() if n not in defaults]
        setattr(new_cls, mcls._FIELDS, tuple(given_anno.keys()))
        setattr(new_cls, mcls._ANNO, given_anno)
        setattr(new_cls, mcls._JSON_MODEL, full_anno)
        setattr(new_cls, "__resolved_anno__", clean_anno)
        setattr(new_cls, "__slots__", required)

        return new_cls

    #

    #

    #


class JSONModel(JSONConvertible, ABC, metaclass=JSONModelMeta):
    _MODEL_CACHE: dict[tuple[Hashable, JSONModelMeta], JSONModelMeta] = dict()

    def __init__(self, **kwargs):
        model = type(self).model()
        ignore_extra = kwargs.pop("_ignore_extra", type(self).__allow_extra_fields__)
        validated = type(self).validate_model(model=model, values=kwargs,
                                              ignore_extra=ignore_extra)
        for k, v in validated.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        parts = ",".join(f"{k}={getattr(self, k)!r}" for k in self.model().keys())
        return f"{type(self).__name__}({parts})"

    def __str__(self) -> str:
        return repr(self)

    @classmethod
    def model(cls) -> dict[str, ModelElem]:
        """
        Retrieves the JSON model definition for objects of this type.
        """
        return {k: v for k, v in getattr(cls, cls._JSON_MODEL, {}).items()
                if k not in cls.__exclusions__}

    @classmethod
    def from_json(cls, o: JSONObject, **kwargs) -> Self:
        """
        Parses the given JSON into an object of this type (or a subclass)
        """
        model = cls.model()
        copy = {k: v for k, v in o.items()
                if not (mt := model.get(k, None)) or not mt.ephemeral}
        subclass = cls._extract_subclass(copy)
        return subclass(**copy, **kwargs)

    def to_json(self, **kwargs) -> JSONObject:
        """
        Dumps the values in this object into a JSON-friendly dictionary
        """
        model = self.model()
        dumped = {k: elem.dump_value(getattr(self, k), key=k)
                  for k, elem in model.items()
                  if not elem.ignored and not elem.ephemeral}

        if not type(self).__include_defaults_in_json_output__:
            dumped = {k: v for k, v in dumped.items()
                      if not model[k].has_default() or v != model[k].default}
        if not type(self).__allow_null_json_output__:
            dumped = {k: v for k, v in dumped.items()
                      if v is not None}
        if type(self).__include_name_in_json_output__:
            dumped[type(self).__name_field__] = self.model_identity()
        return dumped

    #
    # This section is related to automatically parsing JSONModel subclasses
    # from a JSON object.  These fields are used to identify what subclass
    # it should be parsed as
    #

    @classmethod
    def model_identity(cls) -> JSONType:
        return cls.__name__

    @classmethod
    def _pop_name_from_name_field(cls, o: JSONObject) -> JSONType:
        name_field = cls.__name_field__
        if name_field not in o:
            if cls.__name_field_required__:
                raise JSONModelError(f"Object is missing name field '{name_field}'; cannot "
                                     f"determine class to instantiate.")
            return cls.model_identity()

        return o.pop(name_field)

    @classmethod
    def _subclass_match(cls, value: JSONType, subclass: type[Self]) -> bool:
        return value == subclass.model_identity()

    @classmethod
    def _extract_subclass(cls, o: JSONObject) -> type[Self]:
        name = cls._pop_name_from_name_field(o)
        return cls._extract_subclass_by_name(name)

    @classmethod
    def _extract_subclass_by_name(cls, name: str) -> type[Self]:
        if isinstance(name, Hashable):
            _id = (name, cls)
            if _id in JSONModel._MODEL_CACHE:
                return JSONModel._MODEL_CACHE[_id]

        for subclass in itertools.chain((cls,), ClassHelpers.all_subclasses(cls)):
            if cls._subclass_match(name, subclass):
                if isinstance(name, Hashable):
                    JSONModel._MODEL_CACHE[(name, cls)] = subclass
                return subclass

        raise JSONModelError(f"Unable to find suitable subclass for '{cls.__name__}' matching "
                             f"the name '{name}'; cannot parse JSONModel.")

    #
    # This section is for validating the contents of a model based on its contents.
    # This is generally performed internally, but this is exposed as a public class method
    # to be able to leverage its functionality externally, if needed.
    #

    @classmethod
    def validate_model(cls, model: Mapping[str, ModelElem],
                       values: Mapping[str, Any],
                       ignore_extra: bool = False) -> dict[str, Any]:
        return cls._validate_model(model, values, ignore_extra)

    @classmethod
    def _validate_model(cls, model: Mapping[str, ModelElem],
                        values: Mapping[str, Any],
                        ignore_extra: bool) -> dict[str, Any]:
        result: dict[str, Any] = dict()
        values = {**values}
        for k, m in model.items():
            if m.ignored:
                values.pop(k, None)
                continue
            if k not in values:
                if not m.has_default():
                    raise JSONModelError(f"Missing required key '{k}' on '{cls.__name__}'.")
                val = m.default
            else:
                val = values.pop(k)
            try:
                val = m.validate(val, key=k)
            except ModelElemError as e:
                raise JSONModelError(f"Model error on key '{k}' of '{cls.__name__}': {str(e)}")

            result[k] = val

        if not ignore_extra and any(k for k in values.keys() if k not in cls.__exclusions__):
            raise JSONModelError(f"The following keys are not found in the model for '{cls.__name__}': "
                                 f"{','.join(values.keys())}")

        return result
