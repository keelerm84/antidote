import pytest

from antidote import (
    DependencyDuplicateError, DependencyNotProvidableError
)
from antidote.providers.factories import DependencyFactory, FactoryProvider


class Service(object):
    def __init__(self, *args):
        pass


class ServiceSubclass(Service):
    pass


class AnotherService(object):
    def __init__(self, *args):
        pass


@pytest.fixture()
def provider():
    return FactoryProvider()


def test_dependency_factory():
    o = object()

    def test(*args, **kwargs):
        return o, args, kwargs

    df = DependencyFactory(test, True, False)

    assert repr(test) in repr(df)
    assert (o, (1,), {'param': 'none'}) == df(1, param='none')


def test_register(provider: FactoryProvider):
    provider.register(Service, Service)

    dependency = provider.__antidote_provide__(Service)
    assert isinstance(dependency.instance, Service)
    assert repr(Service) in repr(provider)


def test_register_factory_id(provider: FactoryProvider):
    provider.register(Service, lambda: Service())

    dependency = provider.__antidote_provide__(Service)
    assert isinstance(dependency.instance, Service)


def test_singleton(provider: FactoryProvider):
    provider.register(Service, Service, singleton=True)
    provider.register(AnotherService, AnotherService, singleton=False)

    assert provider.__antidote_provide__(Service).singleton is True
    assert provider.__antidote_provide__(AnotherService).singleton is False


def test_register_for_subclasses(provider: FactoryProvider):
    provider.register(Service, lambda cls: cls(), build_subclasses=True)

    assert isinstance(
        provider.__antidote_provide__(Service).instance,
        Service
    )
    assert isinstance(
        provider.__antidote_provide__(ServiceSubclass).instance,
        Service
    )

    with pytest.raises(DependencyNotProvidableError):
        provider.__antidote_provide__(AnotherService)


def test_register_not_callable_error(provider: FactoryProvider):
    with pytest.raises(ValueError):
        provider.register(1, 1)


def test_register_id_null(provider: FactoryProvider):
    with pytest.raises(ValueError):
        provider.register(None, Service)


def test_duplicate_error(provider: FactoryProvider):
    provider.register(Service, Service)

    with pytest.raises(DependencyDuplicateError):
        provider.register(Service, Service)

    with pytest.raises(DependencyDuplicateError):
        provider.register(Service, lambda: Service())