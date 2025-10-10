import typing
import inspect
from types import BuiltinFunctionType, FunctionType, MethodType
from collections.abc import AsyncGenerator, Awaitable, Generator
from contextlib import AbstractAsyncContextManager, AbstractContextManager

from fundi.types import R, CallableInfo, Parameter, TypeResolver
from fundi.util import is_configured, get_configuration, normalize_annotation


def _transform_parameter(parameter: inspect.Parameter) -> Parameter:
    positional_varying = parameter.kind == inspect.Parameter.VAR_POSITIONAL
    positional_only = parameter.kind == inspect.Parameter.POSITIONAL_ONLY
    keyword_varying = parameter.kind == inspect.Parameter.VAR_KEYWORD
    keyword_only = parameter.kind == inspect.Parameter.KEYWORD_ONLY

    default = parameter.default
    has_default = default is not inspect.Parameter.empty
    from_: CallableInfo[typing.Any] | None = None
    resolve_by_type = False

    if isinstance(default, CallableInfo):
        has_default = False
        from_ = typing.cast(CallableInfo[typing.Any], default)

    annotation = parameter.annotation
    if isinstance(annotation, TypeResolver):
        annotation = annotation.annotation
        resolve_by_type = True

    elif typing.get_origin(annotation) is typing.Annotated and from_ is None:
        args = typing.get_args(annotation)

        if TypeResolver in args:
            resolve_by_type = True
        else:
            presence: tuple[CallableInfo[typing.Any]] | tuple[()] = tuple(
                filter(lambda x: isinstance(x, CallableInfo), args)
            )
            if presence:
                from_ = presence[0]

    parameter_ = Parameter(
        parameter.name,
        annotation,
        from_=from_,
        default=default if has_default else None,
        has_default=has_default,
        resolve_by_type=resolve_by_type,
        positional_varying=positional_varying,
        positional_only=positional_only,
        keyword_varying=keyword_varying,
        keyword_only=keyword_only,
    )

    if from_ is not None and from_.graphhook is not None:
        from_copy = from_.copy(deep=True)
        from_.graphhook(from_copy, parameter_.copy())

        return parameter_.copy(from_=from_copy)

    return parameter_


def _is_context(call: typing.Any):
    if isinstance(call, type):
        return issubclass(call, AbstractContextManager)
    else:
        return isinstance(call, AbstractContextManager)


def _is_async_context(call: typing.Any):
    if isinstance(call, type):
        return issubclass(call, AbstractAsyncContextManager)
    else:
        return isinstance(call, AbstractAsyncContextManager)


def scan(
    call: typing.Callable[..., R],
    caching: bool = True,
    async_: bool | None = None,
    generator: bool | None = None,
    context: bool | None = None,
    use_return_annotation: bool = True,
) -> CallableInfo[R]:
    """
    Get callable information

    :param call: callable to get information from
    :param caching:  whether to use cached result of this callable or not
    :param async_: Override "async_" attriubute value
    :param generator: Override "generator" attriubute value
    :param context: Override "context" attriubute value
    :param use_return_annotation: Whether to use call's return
        annotation to define it's type

    :return: callable information
    """

    if hasattr(call, "__fundi_info__"):
        info = typing.cast(CallableInfo[typing.Any], getattr(call, "__fundi_info__"))

        overrides = {"use_cache": caching}
        if async_ is not None:
            overrides["async_"] = async_

        if generator is not None:
            overrides["generator"] = generator

        if context is not None:
            overrides["context"] = context

        return info.copy(**overrides)

    if not callable(call):
        raise ValueError(
            f"Callable expected, got {type(call)!r}"
        )  # pyright: ignore[reportUnreachable]

    truecall = call.__call__
    if isinstance(call, (FunctionType, BuiltinFunctionType, MethodType, type)):
        truecall = call

    signature = inspect.signature(truecall)

    return_: type[typing.Any] = type
    if signature.return_annotation is not signature.empty:
        annotation = normalize_annotation(signature.return_annotation)[0]

        if not isinstance(annotation, type):
            return_ = type(return_)
        else:
            return_ = annotation

    # WARNING: over-engineered logic!! :3

    _generator: bool = inspect.isgeneratorfunction(truecall)
    _agenerator: bool = inspect.isasyncgenfunction(truecall)
    _context: bool = _is_context(call)
    _acontext: bool = _is_async_context(call)

    # Getting "generator" using return typehint or __code__ flags
    if generator is None:
        generator = (
            use_return_annotation
            and (issubclass(return_, Generator) or issubclass(return_, AsyncGenerator))
        ) or (_generator or _agenerator)

    # Getting "context" using return typehint or callable type
    if context is None:
        context = (
            use_return_annotation
            and (issubclass(return_, (AbstractContextManager, AbstractAsyncContextManager)))
        ) or (_context or _acontext)

    # Getting "async_" using return typehint or __code__ flags or defined above variables
    if async_ is None:
        async_ = (
            use_return_annotation
            and issubclass(return_, (AsyncGenerator, AbstractAsyncContextManager, Awaitable))
        ) or (_agenerator or _acontext or inspect.iscoroutinefunction(truecall))

    parameters = [_transform_parameter(parameter) for parameter in signature.parameters.values()]
    hooks = getattr(call, "__fundi_hooks__", {})

    info = CallableInfo(
        call=call,
        use_cache=caching,
        async_=async_,
        context=context,
        graphhook=hooks.get("graph"),
        generator=generator,
        parameters=parameters,
        return_annotation=signature.return_annotation,
        configuration=get_configuration(call) if is_configured(call) else None,
    )

    try:
        setattr(call, "__fundi_info__", info)
    except (AttributeError, TypeError):
        pass

    return info
