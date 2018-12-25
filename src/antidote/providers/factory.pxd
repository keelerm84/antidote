# cython: language_level=3, language=c++
# cython: boundscheck=False, wraparound=False
from antidote.core.container cimport DependencyInstance, DependencyProvider

cdef class FactoryProvider(DependencyProvider):
    cdef:
        dict _factories

    cpdef DependencyInstance provide(self, object dependency)

cdef class Build:
    cdef:
        readonly object wrapped
        readonly tuple args
        readonly dict kwargs
