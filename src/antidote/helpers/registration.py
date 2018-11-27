from typing import Any, Callable, Iterable, Mapping, Sequence, Union, cast

from .._internal.helpers import prepare_callable, prepare_class
from ..container import DependencyContainer
from ..providers import FactoryProvider, GetterProvider, Provider
from ..providers.tags import Tag, TagProvider
from .._internal.container import get_global_container


def register(class_: type = None,
             *,
             singleton: bool = True,
             auto_wire: Union[bool, Iterable[str]] = True,
             arg_map: Union[Mapping, Sequence] = None,
             use_names: Union[bool, Iterable[str]] = None,
             use_type_hints: Union[bool, Iterable[str]] = None,
             tags: Iterable[Union[str, Tag]] = None,
             container: DependencyContainer = None
             ) -> Union[Callable, type]:
    """Register a dependency by its class.

    Args:
        class_: Class to register as a dependency. It will be instantiated
            only when requested.
        singleton: If True, the class will be instantiated only once,
            further will receive the same instance.
        auto_wire: Injects automatically the dependencies of the methods
            specified, or only of :code:`__init__()` if True.
        arg_map: Custom mapping of the arguments name to their respective
            dependency id. A sequence of dependencies can also be
            specified, which will be mapped to the arguments through their
            order. Annotations are overridden.
        use_names: Whether the arguments name should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments. Annotations are
            overridden, but not the arg_map.
        use_type_hints: Whether the type hints should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments.
        tags: Iterable of tags to be applied. Those must be either strings
            (the tags name) or :py:class:`~.providers.tags.Tag`. All
            dependencies with a specific tag can then be retrieved with
            a :py:class:`~.providers.tags.Tagged`.
        container: :py:class:~.container.base.DependencyContainer` to which the
            dependency should be attached. Defaults to the global container if
            it is defined.

    Returns:
        The class or the class decorator.

    """
    container = container or get_global_container()

    def register_class(cls):
        cls = prepare_class(cls,
                            auto_wire=auto_wire,
                            arg_map=arg_map,
                            use_names=use_names,
                            use_type_hints=use_type_hints,
                            container=container)

        factory_provider = cast(FactoryProvider, container.providers[FactoryProvider])
        factory_provider.register(dependency_id=cls, factory=cls,
                                  singleton=singleton)

        if tags is not None:
            tag_provider = cast(TagProvider, container.providers[TagProvider])
            tag_provider.register(cls, tags)

        return cls

    return class_ and register_class(class_) or register_class


def factory(func: Callable = None,
            *,
            dependency_id: Any = None,
            auto_wire: Union[bool, Iterable[str]] = True,
            singleton: bool = True,
            arg_map: Union[Mapping, Sequence] = None,
            use_names: Union[bool, Iterable[str]] = None,
            use_type_hints: Union[bool, Iterable[str]] = None,
            build_subclasses: bool = False,
            tags: Iterable[Union[str, Tag]] = None,
            container: DependencyContainer = None
            ) -> Callable:
    """Register a dependency providers, a factory to build the dependency.

    Args:
        func: Callable which builds the dependency.
        dependency_id: Id of the dependency. Defaults to the return type of
            :code:`func` if specified.
        singleton: If True, `func` will only be called once. If not it is
            called at each injection.
        auto_wire: If :code:`func` is a function, its dependencies are
            injected if True. Should :code:`func` be a class with
            :py:func:`__call__`, dependencies of :code:`__init__()` and
            :code:`__call__()` will be injected if True. One may also
            provide an iterable of method names requiring dependency
            injection.
        arg_map: Custom mapping of the arguments name to their respective
            dependency id. A sequence of dependencies can also be
            specified, which will be mapped to the arguments through their
            order. Annotations are overridden.
        use_names: Whether the arguments name should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments. Annotations are
            overridden, but not the arg_map.
        use_type_hints: Whether the type hints should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments.
        build_subclasses: If True, subclasses will also be build with this
            factory. If multiple factories are defined, the first in the
            MRO is used.
        tags: Iterable of tags to be applied. Those must be either strings
            (the tags name) or :py:class:`~.providers.tags.Tag`. All
            dependencies with a specific tag can then be retrieved with
            a :py:class:`~.providers.tags.Tagged`.
        container: :py:class:~.container.base.DependencyContainer` to which the
            dependency should be attached. Defaults to the global container if
            it is defined.

    Returns:
        object: The dependency_provider

    """
    container = container or get_global_container()

    def register_factory(obj):
        nonlocal dependency_id
        obj, factory_, return_type_hint = prepare_callable(
            obj,
            auto_wire=auto_wire,
            arg_map=arg_map,
            use_names=use_names,
            use_type_hints=use_type_hints,
            container=container
        )

        dependency_id = dependency_id or return_type_hint
        factory_provider = cast(FactoryProvider, container.providers[FactoryProvider])
        factory_provider.register(factory=factory_,
                                  singleton=singleton,
                                  dependency_id=dependency_id,
                                  build_subclasses=build_subclasses)

        if tags is not None:
            tag_provider = cast(TagProvider, container.providers[TagProvider])
            tag_provider.register(dependency_id, tags)

        return obj

    return func and register_factory(func) or register_factory


def provider(class_: type = None,
             *,
             auto_wire: Union[bool, Iterable[str]] = True,
             arg_map: Union[Mapping, Sequence] = None,
             use_names: Union[bool, Iterable[str]] = None,
             use_type_hints: Union[bool, Iterable[str]] = None,
             container: DependencyContainer = None):
    """Register a providers by its class.

    Args:
        class_: class to register as a provider. The class must have a
            :code:`__antidote_provide()` method accepting as first argument
            the dependency id. Variable keyword and positional arguments
            must be accepted as they may be provided.
        auto_wire: If True, the dependencies of :code:`__init__()` are
            injected. An iterable of method names which require dependency
            injection may also be specified.
        arg_map: Custom mapping of the arguments name to their respective
            dependency id. A sequence of dependencies can also be
            specified, which will be mapped to the arguments through their
            order. Annotations are overridden.
        use_type_hints: Whether the type hints should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments.
        use_names: Whether the arguments name should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments. Annotations are
            overridden, but not the arg_map.
        container: :py:class:~.container.base.DependencyContainer` to which the
            dependency should be attached. Defaults to the global container if
            it is defined.

    Returns:
        the providers's class or the class decorator.
    """
    container = container or get_global_container()

    def register_provider(cls):
        if not issubclass(cls, Provider):
            raise ValueError("A provider must be subclass of Provider.")

        cls = prepare_class(cls,
                            auto_wire=auto_wire,
                            arg_map=arg_map,
                            use_names=use_names,
                            use_type_hints=use_type_hints,
                            container=container)

        container.providers[cls] = cls()

        return cls

    return class_ and register_provider(class_) or register_provider


def getter(func: Callable[[str], Any] = None,
           *,
           singleton: bool = True,
           namespace: str = None,
           omit_namespace: bool = None,
           auto_wire: Union[bool, Iterable[str]] = True,
           arg_map: Union[Mapping, Sequence] = None,
           use_names: Union[bool, Iterable[str]] = None,
           use_type_hints: Union[bool, Iterable[str]] = None,
           container: DependencyContainer = None
           ) -> Callable:
    """
    Register a mapping of parameters and its associated parser.

    Args:
        func: Function used to retrieve a requested dependency which will
            be given as an argument. If the dependency cannot be provided,
            it should raise a :py:exc:`LookupError`.
        singleton: If True, `func` will only be called once. If not it is
            called at each injection.
        namespace: Used to identity which getter should be used with a
            dependency, as such they have to be mutually exclusive.
        omit_namespace: Whether or the namespace should be removed from the
            dependency name which is given to the getter. Defaults to False.
        auto_wire: If True, the dependencies of :code:`__init__()` are
            injected. An iterable of method names which require dependency
            injection may also be specified.
        arg_map: Custom mapping of the arguments name to their respective
            dependency id. A sequence of dependencies can also be
            specified, which will be mapped to the arguments through their
            order. Annotations are overridden.
        use_type_hints: Whether the type hints should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments.
        use_names: Whether the arguments name should be used to find for
            a dependency. An iterable of names may also be provided to
            restrict this to a subset of the arguments. Annotations are
            overridden, but not the arg_map.
        container: :py:class:~.container.base.DependencyContainer` to which the
            dependency should be attached. Defaults to the global container if
            it is defined.

    Returns:
        getter callable or decorator.
    """
    container = container or get_global_container()

    def register_getter(obj):
        nonlocal namespace, omit_namespace

        if namespace is None:
            namespace = obj.__name__ + ":"
            omit_namespace = omit_namespace if omit_namespace is not None else True

        omit_namespace = omit_namespace if omit_namespace is not None else False

        obj, getter_, _ = prepare_callable(obj,
                                           auto_wire=auto_wire,
                                           arg_map=arg_map,
                                           use_names=use_names,
                                           use_type_hints=use_type_hints,
                                           container=container)

        getter_provider = cast(GetterProvider, container.providers[GetterProvider])
        getter_provider.register(getter=getter_,
                                 namespace=namespace,
                                 omit_namespace=omit_namespace,
                                 singleton=singleton)

        return obj

    return func and register_getter(func) or register_getter
