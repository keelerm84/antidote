from antidote.core import DependencyInstance, DependencyProvider


class DummyProvider(DependencyProvider):
    singleton = True

    def __init__(self, data=None):
        self.data = data

    def provide(self, dependency):
        try:
            return DependencyInstance(self.data[dependency],
                                      singleton=self.singleton)
        except KeyError:
            pass


class DummyFactoryProvider(DependencyProvider):
    singleton = True

    def __init__(self, data=None):
        self.data = data or dict()

    def provide(self, dependency):
        try:
            return DependencyInstance(self.data[dependency](),
                                      singleton=self.singleton)
        except KeyError:
            pass


class Service:
    def __init__(self, *args):
        pass


class AnotherService:
    def __init__(self, *args):
        pass


class YetAnotherService:
    def __init__(self, *args):
        pass


class ServiceWithNonMetDependency:
    def __init__(self, dependency):
        pass
