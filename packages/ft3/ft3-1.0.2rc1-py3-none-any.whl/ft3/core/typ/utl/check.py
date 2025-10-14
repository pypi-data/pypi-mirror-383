"""Type checking utility functions."""

__all__ = (
	'get_args',
	'get_checkable_types',
	'expand_types',
	'is_array',
	'is_array_of_object',
	'is_array_of_obj_type',
	'is_array_type',
	'is_bool_type',
	'is_date_type',
	'is_datetime_type',
	'is_field',
	'is_field_type',
	'is_immutable_type',
	'is_literal',
	'is_mapping',
	'is_mapping_type',
	'is_none_type',
	'is_number_type',
	'is_object',
	'is_object_type',
	'is_optional_union_of_literal',
	'is_params_type',
	'is_primitive',
	'is_serialized_mapping',
	'is_typed',
	'is_typevar',
	'is_union',
	'is_union_of_literal',
	'is_uuid_type',
	'is_variadic_array_type',
	'is_wrapper_type',
)

from .. import cfg
from .. import lib
from .. import obj

if lib.t.TYPE_CHECKING:  # pragma: no cover
	from .... import objects
	from .. import typ


class Constants(cfg.Constants):
	"""Constant values specific to this file."""


def get_args(tp: lib.t.Any) -> tuple[lib.t.Any, ...]:
	"""Wrapper for `lib.t.get_args`."""

	return lib.t.get_args(tp)


GET_TYPE_ARGS_CACHE: dict[int, tuple[lib.t.Any, ...]] = {}
"""Cache for `get_type_args`."""


@lib.t.overload
def get_type_args(
	tp: 'obj.SupportsParams[lib.Unpack[typ.ArgsType]]',
) -> 'tuple[lib.Unpack[typ.ArgsType]]': ...
@lib.t.overload
def get_type_args(tp: lib.t.Any) -> tuple[lib.t.Any, ...]: ...
def get_type_args(
	tp: 'obj.SupportsParams[lib.Unpack[typ.ArgsType]] | lib.t.Any',
) -> 'tuple[lib.Unpack[typ.ArgsType]] | tuple[lib.t.Any, ...]':
	"""
	Get generic arguments for `type[Any]`.

	---

	`Literals` will be returned as the types of their values.

	#### Examples

	```python
	get_type_args(Literal[1])
	(int, )

	get_type_args(tuple[str, int])
	(str, int, )

	```

	"""

	tp_key = hash(tp)

	if tp_key not in GET_TYPE_ARGS_CACHE:
		GET_TYPE_ARGS_CACHE[tp_key] = tuple(
			type(arg) if is_literal(tp) else arg for arg in get_args(tp)
		)

	return GET_TYPE_ARGS_CACHE[tp_key]


GET_CHECKABLE_TYPES_CACHE: dict[int, tuple[type, ...]] = {}
"""Cache for `get_checkable_types`."""


@lib.t.overload
def get_checkable_types(
	any_tp: 'type[typ.AnyType]',
) -> 'tuple[type[typ.AnyType] | type, ...]': ...
@lib.t.overload
def get_checkable_types(any_tp: lib.t.Any) -> tuple[type, ...]: ...
def get_checkable_types(
	any_tp: 'type[typ.AnyType] | type[lib.t.Any] | lib.t.Any',
) -> 'tuple[typ.AnyType | type, ...] | tuple[type, ...]':
	"""
    Get checkable origin lib.types, handling `Union` and `TypeVar` \
    expansions automatically.

    ---

    `Literals` will be returned as their values.

    `Annotated`, `ClassVar`, `Final`, and `InitVar` are expanded as \
    their parameter arguments.

    """

	if isinstance(any_tp, lib.t.ForwardRef):
		tp_key = hash(any_tp.__forward_arg__)
	else:
		tp_key = hash(any_tp)

	if tp_key in GET_CHECKABLE_TYPES_CACHE:
		return GET_CHECKABLE_TYPES_CACHE[tp_key]

	checkable_types = {
		otp
		for tp in expand_types(any_tp)
		if isinstance((otp := lib.t.get_origin(tp) or tp), type)
		and otp is not lib.t.Any
	}
	GET_CHECKABLE_TYPES_CACHE[tp_key] = tuple(checkable_types)

	return tuple(checkable_types)


EXPAND_TYPES_CACHE: dict[int, tuple[lib.t.Any, ...]] = {}
"""Cache for `expand_types`."""


@lib.t.overload
def expand_types(
	any_tp: 'type[typ.AnyType]',
) -> 'tuple[type[typ.AnyType] | type[lib.t.Any], ...]': ...
@lib.t.overload
def expand_types(any_tp: lib.t.Any) -> 'tuple[type[lib.t.Any], ...]': ...
def expand_types(
	any_tp: 'type[typ.AnyType] | lib.t.Any',
) -> lib.t.Union[
	'tuple[type[typ.AnyType] | type[lib.t.Any], ...]',
	tuple[type[lib.t.Any], ...],
]:
	"""
    Recursively get valid subtypes into flattened `tuple` from a \
    passed `type`, `Union`, or `TypeVar`.

    ---

    `Literals` will be returned as their values.

    `Annotated`, `ClassVar`, `Final`, and `InitVar` are expanded as \
    their parameter arguments.

    """

	if isinstance(any_tp, lib.t.ForwardRef):
		tp_key = hash(any_tp.__forward_arg__)
	elif isinstance(any_tp, type):
		tp_key = hash(any_tp)
	else:
		tp_key = hash(repr(any_tp))

	if tp_key in EXPAND_TYPES_CACHE:
		return EXPAND_TYPES_CACHE[tp_key]
	elif is_union(any_tp) or is_wrapper_type(any_tp):
		tps = tuple(
			tp
			for tp in set(
				lib.itertools.chain.from_iterable(
					expand_types(sub_tp) for sub_tp in get_type_args(any_tp)
				)
			)
		)
	elif is_typevar(any_tp):
		if any_tp.__constraints__:
			tps = tuple(
				tp
				for tp in set(
					lib.itertools.chain.from_iterable(
						expand_types(sub_tp)
						for sub_tp in any_tp.__constraints__
					)
				)
			)
		elif any_tp.__bound__:
			tps = expand_types(any_tp.__bound__)
		else:
			tps = (object,)
	elif is_literal(any_tp):
		tps = (type(get_args(any_tp)[0]),)
	else:
		tps = (any_tp,)

	EXPAND_TYPES_CACHE[tp_key] = tps

	return tps


def is_nullable(tp: lib.t.Any) -> bool:
	"""Returns `True` if `tp` can be `None`."""

	return any(
		any(is_none_type(sub_tp) for sub_tp in get_checkable_types(arg_tp))
		for arg_tp in get_type_args(tp)
	)


@lib.t.overload
def is_params_type(
	tp: 'obj.SupportsParams[lib.Unpack[typ.ArgsType]]',
) -> lib.t.TypeGuard['obj.SupportsParams[lib.Unpack[typ.ArgsType]]']: ...
@lib.t.overload
def is_params_type(
	tp: lib.t.Any | type[lib.t.Any],
) -> lib.t.TypeGuard[
	'obj.SupportsParams[lib.Unpack[tuple[lib.t.Any, ...]]]'
]: ...
def is_params_type(
	tp: 'obj.SupportsParams[lib.Unpack[typ.ArgsType]] | lib.t.Any',
) -> lib.t.TypeGuard[
	lib.t.Union[
		'obj.SupportsParams[lib.Unpack[typ.ArgsType]]',
		'obj.SupportsParams[lib.Unpack[tuple[lib.t.Any, ...]]]',
	]
]:
	"""Return `True` if `tp` has type args."""

	return bool(get_args(tp))


def is_typevar(obj: lib.t.Any) -> lib.t.TypeGuard[lib.t.TypeVar]:
	"""Return `True` if obj is a `TypeVar`."""

	return isinstance(obj, lib.t.TypeVar)


IS_UNION_OF_LITERAL_CACHE: dict[int, bool] = {}
"""Cache for `is_union_of_literal`."""


def is_union_of_literal(
	obj: lib.t.Any,
) -> lib.t.TypeGuard[lib.lib.types.UnionType]:
	"""
	Return `True` if obj is a `UnionType` of all same typed `Literal`.

	"""

	tp_key = hash(obj)

	if tp_key not in IS_UNION_OF_LITERAL_CACHE:
		IS_UNION_OF_LITERAL_CACHE[tp_key] = (
			is_union(obj)
			and all(is_literal(tp) for tp in get_args(obj))
			and len(set(get_checkable_types(obj))) == 1
		)

	return IS_UNION_OF_LITERAL_CACHE[tp_key]


IS_OPTIONAL_UNION_OF_LITERAL_CACHE: dict[int, bool] = {}
"""Cache for `is_optional_union_of_literal`."""


def is_optional_union_of_literal(
	obj: lib.t.Any,
) -> lib.t.TypeGuard[lib.lib.types.UnionType]:
	"""
    Return `True` if obj is a `Optional[UnionType]` of all same typed \
    `Literal`.

    """

	tp_key = hash(obj)

	if tp_key not in IS_OPTIONAL_UNION_OF_LITERAL_CACHE:
		IS_OPTIONAL_UNION_OF_LITERAL_CACHE[tp_key] = (
			is_union(obj)
			and len(tps := set(get_checkable_types(obj))) == 2
			and all(is_literal(tp) or is_none_type(tp) for tp in get_args(obj))
			and any(is_none_type(tp) for tp in tps)
		)

	return IS_OPTIONAL_UNION_OF_LITERAL_CACHE[tp_key]


IS_UNION_CACHE: dict[int, bool] = {}
"""Cache for `is_union`."""


def is_union(obj: lib.t.Any) -> lib.t.TypeGuard[lib.lib.types.UnionType]:
	"""Return `True` if obj is a `UnionType`."""

	from .. import typ

	if isinstance(obj, lib.t.ForwardRef):
		tp_key = hash(obj.__forward_arg__)
	else:
		tp_key = hash(obj.__class__.__name__)

	if tp_key not in IS_UNION_CACHE:
		IS_UNION_CACHE[tp_key] = isinstance(
			obj,
			(
				typ.OptionalGenericAlias,
				typ.UnionGenericAlias,
				lib.types.UnionType,
			),
		)

	return IS_UNION_CACHE[tp_key]


@lib.t.overload
def is_bool_type(
	tp: 'type[typ.AnyType]',
) -> 'lib.t.TypeGuard[type[typ.AnyType]]': ...
@lib.t.overload
def is_bool_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[type[bool]]: ...
def is_bool_type(
	tp: 'type[typ.AnyType] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[bool] | type[typ.AnyType]]':
	"""Return `True` if `tp` is `type[bool]`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], bool)
	else:
		return False


@lib.t.overload
def is_number_type(
	tp: 'type[typ.NumberType]',
) -> 'lib.t.TypeGuard[type[typ.NumberType]]': ...
@lib.t.overload
def is_number_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[type[lib.numbers.Number]]: ...
def is_number_type(
	tp: 'type[typ.NumberType] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[lib.numbers.Number] | type[typ.NumberType]]':
	"""Return `True` if tp is `numbers.Number`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], get_checkable_types(lib.numbers.Number))
	else:
		return False


def is_ellipsis(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[lib.types.EllipsisType]:
	"""Return `True` if `tp` is `[...]`."""

	otps = get_checkable_types(type(tp))

	if otps:
		return issubclass(otps[0], lib.types.EllipsisType)
	else:  # pragma: no cover
		return False


IS_LITERAL_CACHE: dict[int, bool] = {}
"""Cache for `is_literal`."""


def is_literal(
	tp: type[lib.t.Any] | lib.t.Any,
) -> 'lib.t.TypeGuard[typ.Literal]':
	"""Return `True` if `tp` is a `Literal`."""

	if isinstance(tp, lib.t.ForwardRef):
		tp_key = hash(tp.__forward_arg__)
	else:
		tp_key = hash(tp.__class__.__name__)

	if tp_key not in IS_LITERAL_CACHE:
		otp = lib.t.get_origin(tp) or tp

		IS_LITERAL_CACHE[tp_key] = getattr(otp, '__name__', '') == 'Literal'

	return IS_LITERAL_CACHE[tp_key]


def is_date_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[type[lib.datetime.date]]:
	"""Return `True` if `tp` is `datetime.date`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], lib.datetime.date)
	else:
		return False


def is_datetime_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[type[lib.datetime.datetime]]:
	"""Return `True` if `tp` is `datetime.datetime`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], lib.datetime.datetime)
	else:
		return False


IS_NONE_CACHE: dict[int, bool] = {}
"""Cache for `is_none_type`."""


def is_none_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> 'lib.t.TypeGuard[type[typ.NoneType]]':
	"""Return `True` if `tp` is `NoneType`."""

	if isinstance(tp, type):
		tp_key = hash(tp)
	else:
		tp_key = hash(tp.__class__.__name__)

	if tp_key not in IS_NONE_CACHE:
		otps = get_checkable_types(tp)

		if otps:
			IS_NONE_CACHE[tp_key] = issubclass(otps[0], None.__class__)
		else:
			IS_NONE_CACHE[tp_key] = False

	return IS_NONE_CACHE[tp_key]


IS_PRIMITIVE_CACHE: dict[int, bool] = {}
"""Cache for `is_primitve`."""


def is_primitive(obj: lib.t.Any) -> 'lib.t.TypeGuard[typ.Primitive]':
	"""Return `True` if `obj` is a `Primitive`."""

	from .. import typ

	if isinstance(obj, type):
		tp_key = hash(obj)
	else:
		tp_key = hash(obj.__class__.__name__)

	if tp_key not in IS_PRIMITIVE_CACHE:
		IS_PRIMITIVE_CACHE[tp_key] = isinstance(
			obj, get_checkable_types(typ.Primitive)
		)

	return IS_PRIMITIVE_CACHE[tp_key]


IS_SERIALIZED_MAPPING_CACHE: dict[int, bool] = {}
"""Cache for `is_serialized_mapping`."""


def is_serialized_mapping(
	obj: lib.t.Any | type[lib.t.Any],
) -> 'lib.t.TypeGuard[typ.Mapping[typ.Primitive, typ.Serial]]':
	"""
	Return `True` if `obj` is `MappingProto[typ.Primitive, typ.Serial]`.

	"""

	from .. import typ

	if is_mapping(obj):
		tp_key = hash(str(v) for v in obj.values())
	else:
		tp_key = hash(obj.__class__.__name__)

	if tp_key not in IS_SERIALIZED_MAPPING_CACHE:
		IS_SERIALIZED_MAPPING_CACHE[tp_key] = isinstance(
			obj, lib.t.Mapping
		) and all(
			(
				is_primitive(k)
				and isinstance(v, get_checkable_types(typ.Serial))
			)
			for k, v in obj.items()
		)

	return IS_SERIALIZED_MAPPING_CACHE[tp_key]


IS_MAPPING_CACHE: dict[int, bool] = {}
"""Cache for `is_mapping`."""


def is_mapping(
	obj: 'typ.MappingType | lib.t.Any',
) -> lib.t.TypeGuard['typ.MappingType | typ.Mapping[lib.t.Any, lib.t.Any]']:
	"""Return `True` if `obj` is `Mapping[lib.t.Any, lib.t.Any]`."""

	if isinstance(obj, type):
		tp_key = hash(obj)
	else:
		tp_key = hash(obj.__class__.__name__)

	if tp_key not in IS_MAPPING_CACHE:
		IS_MAPPING_CACHE[tp_key] = isinstance(obj, lib.t.Mapping)

	return IS_MAPPING_CACHE[tp_key]


def is_mapping_type(
	tp: 'type[typ.MappingType] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[typ.MappingType]]':
	"""Return `True` if `tp` is `type[Mapping[lib.t.Any, lib.t.Any]]`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], lib.t.Mapping)
	else:
		return False


IS_ARRAY_CACHE: dict[int, bool] = {}
"""Cache for `is_array`."""


@lib.t.overload
def is_array(
	obj: 'typ.Array[typ.AnyType]',
) -> 'lib.t.TypeGuard[typ.Array[typ.AnyType]]': ...
@lib.t.overload
def is_array(
	obj: lib.t.Any,
) -> 'lib.t.TypeGuard[typ.Array[lib.t.Any]]': ...
def is_array(
	obj: 'typ.Array[typ.AnyType | lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[typ.Array[typ.AnyType | lib.t.Any]]':
	"""Return `True` if `obj` is `Array[lib.t.Any]`."""

	if isinstance(obj, type):
		tp_key = hash(obj)
	else:
		tp_key = hash(obj.__class__.__name__)

	if tp_key not in IS_ARRAY_CACHE:
		IS_ARRAY_CACHE[tp_key] = isinstance(
			obj, lib.t.Collection
		) and not isinstance(obj, (str, lib.t.Mapping, lib.enum.EnumMeta))

	return IS_ARRAY_CACHE[tp_key]


def is_array_of_object(
	obj: lib.t.Any,
) -> 'lib.t.TypeGuard[typ.Array[typ.Object]]':
	"""Return `True` if `obj` is `Array[Object]`."""

	return is_array_type(type(obj)) and bool(obj) and is_object(obj[0])


def is_object(
	obj_: 'obj.ObjectLike | type[lib.t.Any] | lib.t.Any',
) -> lib.t.TypeGuard['obj.ObjectLike']:
	"""Return `True` if `obj_` is an `Object`."""

	return is_object_type(obj_)


IS_OBJECT_TYPE_CACHE: dict[int, bool] = {}
"""Cache for `is_object_type`."""


def is_object_type(tp: lib.t.Any) -> lib.t.TypeGuard[type['objects.Object']]:
	"""Return `True` if `tp` is an `Object`."""

	if isinstance(tp, type):
		tp_key = hash(tp)
	elif is_mapping(tp):
		tp_key = hash(str(v) for v in tp.values())
	else:
		tp_key = hash(tp.__class__.__name__)

	if tp_key not in IS_OBJECT_TYPE_CACHE:
		if isinstance(tp, type):
			otp = lib.t.get_origin(tp) or tp
		else:
			otp = type(tp)

		from .... import objects

		IS_OBJECT_TYPE_CACHE[tp_key] = issubclass(otp, objects.Object)

	return IS_OBJECT_TYPE_CACHE[tp_key]


def is_field(
	obj_: 'typ.AnyField[typ.AnyType] | lib.t.Any',
) -> lib.t.TypeGuard['typ.AnyField[typ.AnyType] | typ.AnyField[lib.t.Any]']:
	"""Return `True` if `obj_` typ AnyField[Any]`."""

	obj_tp = obj_ if isinstance(obj_, type) else type(obj_)

	return is_field_type(obj_tp)


IS_FIELD_TYPE_CACHE: dict[int, bool] = {}
"""Cache for `is_field_type`."""


def is_field_type(
	tp: 'type[typ.AnyField[typ.AnyType]] | lib.t.Any',
) -> lib.t.TypeGuard[
	'type[typ.AnyField[typ.AnyType]] | type[typ.AnyField[lib.t.Any]]'
]:
	"""Return `True` if `tp` is `typ[AnyField[Any]]`."""

	if isinstance(tp, lib.t.ForwardRef):
		tp_key = hash(tp.__forward_arg__)
	else:
		tp_key = hash(tp)

	if tp_key not in IS_FIELD_TYPE_CACHE:
		if isinstance(tp, lib.t.ForwardRef):
			IS_FIELD_TYPE_CACHE[tp_key] = bool(
				obj.FieldPattern.match(tp.__forward_arg__)
			)
		elif isinstance(tp, str):
			IS_FIELD_TYPE_CACHE[tp_key] = bool(obj.FieldPattern.match(tp))
		else:
			otp = lib.t.get_origin(tp) or tp

			from .... import objects

			IS_FIELD_TYPE_CACHE[tp_key] = getattr(
				otp, '__name__', ''
			) == 'Field' and not issubclass(otp, objects.typ.Field)

	return IS_FIELD_TYPE_CACHE[tp_key]


IS_WRAPPER_TYPE_CACHE: dict[int, bool] = {}
"""Cache for `is_wrapper_type`."""


def is_wrapper_type(
	tp: 'typ.Wrapper | type[lib.t.Any] | lib.t.Any',
) -> lib.t.TypeGuard['typ.Wrapper']:
	"""Return `True` if `tp` is `Annotated | ClassVar | Final | InitVar`."""

	if isinstance(tp, lib.t.ForwardRef):
		tp_key = hash(tp.__forward_arg__)
	elif is_mapping(tp):
		tp_key = hash(str(v) for v in tp.values())
	else:
		tp_key = hash(tp)

	if tp_key not in IS_WRAPPER_TYPE_CACHE:
		if isinstance(tp, lib.t.ForwardRef):
			IS_WRAPPER_TYPE_CACHE[tp_key] = bool(
				obj.WrapperPattern.match(tp.__forward_arg__)
			)
		elif isinstance(tp, str):  # pragma: no cover
			IS_WRAPPER_TYPE_CACHE[tp_key] = bool(obj.WrapperPattern.match(tp))
		else:
			otp = lib.t.get_origin(tp) or tp

			IS_WRAPPER_TYPE_CACHE[tp_key] = getattr(otp, '__name__', '') in {
				'Annotated',
				'ClassVar',
				'Final',
				'InitVar',
			}

	return IS_WRAPPER_TYPE_CACHE[tp_key]


def is_uuid_type(
	tp: type[lib.t.Any] | lib.t.Any,
) -> lib.t.TypeGuard[lib.uuid.UUID]:
	"""Return `True` if `tp` is `UUID`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], lib.uuid.UUID)
	else:
		return False


IS_TYPED_CACHE: dict[int, bool] = {}
"""Cache for `is_typed`."""


def is_typed(
	any: 'type[typ.Typed] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[typ.Typed]]':
	"""Return `True` if `any` is type-hinted."""

	if isinstance(any, type):
		tp_key = hash(any)
	else:
		tp_key = hash(any.__class__.__name__)

	if tp_key not in IS_TYPED_CACHE:
		IS_TYPED_CACHE[tp_key] = (
			getattr(any, '__annotations__', False)
			and not isinstance(any, lib.t.ForwardRef)
			and not isinstance(
				any, (lib.types.FunctionType, lib.types.MethodType)
			)
		)

	return IS_TYPED_CACHE[tp_key]


def is_array_of_obj_type(
	tp: type[lib.t.Any],
) -> 'lib.t.TypeGuard[type[typ.Array[typ.Object]]]':
	"""Return `True` if `tp` is `type[typ.Array[typ.Object]]`."""

	return (
		bool(otps := get_checkable_types(tp))
		and issubclass(otps[0], lib.t.Collection)
		and not issubclass(otps[0], lib.t.Mapping)
		and not is_object_type(otps[0])
		and bool(argtps := get_type_args(tp))
		and is_object_type(argtps[0])
	)


def is_array_type(
	tp: 'type[typ.ArrayType] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[typ.ArrayType]]':
	"""Return `True` if `tp` is `type[Array[lib.t.Any]]`."""

	otps = get_checkable_types(tp)

	if otps:
		return (
			issubclass(otps[0], lib.t.Collection)
			and not issubclass(otps[0], (str, lib.t.Mapping))
			and not is_object_type(otps[0])
		)
	else:
		return False


def is_variadic_array_type(
	tp: 'type[typ.VariadicArrayType] | type[lib.t.Any] | lib.t.Any',
) -> 'lib.t.TypeGuard[type[typ.VariadicArrayType]]':
	"""Return `True` if `tp` is `type[VariadicArray]`."""

	otps = get_checkable_types(tp)

	if otps:
		return issubclass(otps[0], tuple)
	else:
		return False


def is_immutable_type(
	tp: type[lib.t.Any],
) -> 'lib.t.TypeGuard[type[typ.Immutable]]':
	"""Return `True` if tp is an immutable standardlib type."""

	from .. import typ

	for sub_tp in expand_types(tp):
		if all(
			issubclass(sub_otp, get_checkable_types(typ.Immutable))
			for sub_otp in get_checkable_types(sub_tp)
		):
			if is_params_type(sub_tp):
				if all(
					is_immutable_type(arg_tp) or is_ellipsis(arg_tp)
					for arg_tp in get_type_args(sub_tp)
				):
					return True
			else:
				return True

	return False
