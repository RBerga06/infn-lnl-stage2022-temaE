import cython
cdef:
    bint FORCE_UPROOT
    bint ROOT


@cython.locals(
    data=list,
    vals=dict,
    f=object,
    t=object,
    x=object,
    raw_data=dict,
    branches=dict,
    attr=str,
    i=cython.long,
)
cdef list[object] _read(
    object file,
    type cls,
    str tree,
    list attributes,
    list list_conv,
)
