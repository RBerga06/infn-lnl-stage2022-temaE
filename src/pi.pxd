import cython

cdef:
    long K
    object SRC
    object L
    bint UNICODE_BOX


@cython.locals(
    BUG=bint,
    rargv=list,
)
cdef bint bug(bint default)


@cython.locals(_mode=int)
cdef int mode()


@cython.locals(
    s=str,
    j=int,
    c=str
)
cdef str style_pi(str pi, int i, str OK, str K0, str KO)


@cython.locals(
    width=int,
    title=str,
    BUG=bint,
    MODE=bint,
    TRG=object,
    LEN=int,
    N_in=int,
    x_in=list,
    x_out=list,
    y_in=list,
    y_out=list,
    pi_array=list,
    squares=list,
    i=int,
    x=int,
    y=int,
    pi=object,
    l=int,
    spi=str,
    sPI=str,
    digit=str,
    DIGIT=str,
    PI_STYLE=str,
    OK_STYLE=str,
    K0_STYLE=str,
    KO_STYLE=str,
    UL=str,
    UR=str,
    DL=str,
    DR=str,
    H=str,
    V=str,
)
cpdef void main()
