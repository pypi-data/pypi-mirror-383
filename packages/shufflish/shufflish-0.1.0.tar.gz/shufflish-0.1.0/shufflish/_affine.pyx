# cython: language_level=3
# cython: binding=False
# cython: embedsignature=False
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: cdivision_warnings=False
# cython: cpow=True
# cython: initializedcheck=False
# cython: nonecheck=False
# cython: overflowcheck=False
# cython: emit_code_comments=False
# cython: linetrace=False
# cython: freethreading_compatible=True


import cython
from cpython.slice cimport PySlice_Unpack, PySlice_AdjustIndices
from libc.stdint cimport *
from ._affine_cipher cimport *


cdef inline int64_t mod_inverse(int64_t prime, int64_t domain) noexcept:
    """
    Return the multiplicative inverse prime modulo domain,
    assuming prime and domain are coprime.
    """
    cdef int64_t iprime, x, n
    iprime = 1
    x = 0
    n = domain
    while prime > 1:
        iprime, x = x, iprime - (prime // n) * x
        prime, n = n, prime % n
    while iprime < 0:
        iprime += domain
    return iprime


cdef inline Py_ssize_t slice_len(Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step) noexcept:
    if step < 0:
        if stop < start:
            return (start - stop - 1) / -step + 1
    else:
        if start < stop:
            return (stop - start - 1) / step + 1
    return 0


cdef inline Py_ssize_t sign(Py_ssize_t x) noexcept:
    return (x > 0) - (x < 0)


cdef class AffineCipher:
    """
    AffineCipher(domain: int, prime: int, pre_offset: int, post_offset: int)

    The base class returned by :func:`permutation` and :class:`Permutations`.
    Produces indices from a permutation of ``range(domain)``.
    You can iterate over all indices, get a range, or access randomly::

        from shufflish import AffineCipher
        p = AffineCipher(10, 7, 6, 3)

        for i in p:
            print(i)

        print(list(p))
        print(list(p[3:8]))
        print(p[3])

    Internally, it maps an index ``i`` to
    ``((i + pre_offset) * prime + post_offset) % domain``.
    This produces a permutation of ``range(domain)`` if the following are true:

    * ``prime`` and ``domain`` are coprime, i.e., ``gcd(domain, prime) = 1``
    * ``prime, pre_offset, post_offset < domain``
    * ``0 < domain < 2**63`` to avoid division by zero and overflows.

    The advantage is that there is no setup time, an instance occupies just 80 bytes,
    and it runs 20 times faster than :func:`random.shuffle` and twice as fast
    as :func:`numpy.random.shuffle`.
    It is also ten times faster than :func:`random.randrange`, which obviously
    does not produce a permutation.

    .. warning::
        This class only performs numerical overflow checks during initialization.
        If you choose to create instances yourself instead of through the
        :func:`permutation` function or :class:`Permutations` class,
        you need to ensure that the parameters fulfill the listed requirements.
    """

    cdef affineCipherParameters params
    cdef Py_ssize_t start, stop, step
    cdef uint64_t iprime

    def __init__(
        self,
        Py_ssize_t domain,
        Py_ssize_t prime,
        Py_ssize_t pre_offset,
        Py_ssize_t post_offset,
    ):
        if domain <= 0:
            raise ValueError("domain must be > 0")
        if prime <= 0:
            raise ValueError("prime must be > 0")
        if pre_offset < 0:
            raise ValueError("pre_offset must be >= 0")
        if post_offset < 0:
            raise ValueError("post_offset must be >= 0")
        fillAffineCipherParameters(
            &self.params,
            <uint64_t> domain,
            <uint64_t> prime,
            <uint64_t> pre_offset,
            <uint64_t> post_offset,
        )
        self.start = 0
        self.stop = domain
        self.step = 1
        self.iprime = 0

    def __iter__(self):
        cdef Py_ssize_t i = self.start
        if self.step > 0:
            while i < self.stop:
                yield affineCipher(&self.params, i)
                i += self.step
        else:
            while i > self.stop:
                yield affineCipher(&self.params, i)
                i += self.step

    def __getitem__(self, item):
        cdef Py_ssize_t i, start, stop, step, n
        cdef AffineCipher ac
        if isinstance(item, slice):
            PySlice_Unpack(item, &start, &stop, &step)

            # Determining start should be relatively easy, and we calculate
            # stop ourselves later, so we could technically avoid calling
            # PySlice_AdjustIndices, but to quote the code:
            #     "this is harder to get right than you might think"
            # It needs the current slice length and returns the new length
            n = slice_len(self.start, self.stop, self.step)
            n = PySlice_AdjustIndices(n, &start, &stop, step)

            # Combine step sizes and calculate the new start position
            step *= self.step
            start = self.start + start * self.step

            # Set the stopping point such that subsequent slicing operations
            # behave the same as tuple et al.
            #
            # Example 1:
            #     (0,1,2,3,4,5)[::2] == (0,2,4), so stop should be 5
            #     After adjust n=3, start=0, stop=6, step=2.
            #     We calculate stop = 0 + 2 * (3-1) + 1 = 5
            # Example 2:
            #     (0,1,2,3,4,5)[::-2] == (5,3,1), so stop should be 0
            #     After adjust n=3, start=5, stop=-1, step=-2.
            #     We calculate stop = 5 + (-2) * (3-1) - 1 = 0
            #
            # There are n-1 steps in the slice; n overshoots by step-1:
            # (0,1,2,3,4,5)[::3] == (0, 3) -> n * step = 2 * 3 = 6
            # actual stop should be 4, i.e., the first exluded index:
            # add 1 if step>0 => sign(step)=1
            # subtract 1 if step<0 => sign(step)=-1
            stop = start + (n-1) * step + sign(step)

            ac = AffineCipher.__new__(AffineCipher)
            ac.params = self.params
            ac.start = start
            ac.stop = stop
            ac.step = step
            ac.iprime = self.iprime
            return ac
        else:
            i = item
            i *= self.step
            if i < 0:
                i += self.stop - self.start
            if i < 0 or i >= self.stop - self.start:
                raise IndexError("index out of range")
            return affineCipher(&self.params, i + self.start)

    def __repr__(self):
        return f"<AffineCipher domain={self.params.domain} prime={self.params.prime} pre={self.params.pre_offset} post={self.params.post_offset} slice=({self.start},{self.stop},{self.step})>"

    def __hash__(self):
        return hash((
            self.params.domain,
            self.params.prime,
            self.params.pre_offset,
            self.params.post_offset,
            self.start,
            self.stop,
            self.step,
        ))

    def __eq__(self, other):
        if not isinstance(other, AffineCipher):
            return False
        cdef AffineCipher other_ = other
        cdef affineCipherParameters oparams = other_.params
        cdef int eq = self.params.domain == oparams.domain \
           and self.params.prime == oparams.prime \
           and self.params.pre_offset == oparams.pre_offset \
           and self.params.post_offset == oparams.post_offset \
           and self.start == other_.start \
           and self.stop == other_.stop \
           and self.step == other_.step
        return eq != 0

    def __len__(self):
        return slice_len(self.start, self.stop, self.step)

    def __contains__(self, item):
        if not isinstance(item, int) or item < 0:
            return False
        cdef uint64_t v = item

        # determine index i for value v
        if self.iprime == 0:
            self.iprime = <uint64_t> mod_inverse(self.params.prime, self.params.domain)
        cdef affineCipherParameters params
        fillAffineCipherParameters(
            &params,
            self.params.domain,
            self.iprime,
            self.params.domain - self.params.post_offset,
            self.params.domain - self.params.pre_offset,
        )
        # result must be >= 0 and < domain, which is Py_ssize_t in __init__
        cdef Py_ssize_t i = <Py_ssize_t> affineCipher(&params, v)

        # contains test
        if self.step > 0:
            if i >= self.start and i < self.stop and (i - self.start) % self.step == 0:
                return True
        elif self.step < 0:
            if i > self.stop and i <= self.start and (i - self.start) % self.step == 0:
                return True
        return False

    def index(self, uint64_t value):
        """
        Return the index of value.

        Raises :class:`ValueError` if the value is not present.
        """
        # determine index i for value
        if self.iprime == 0:
            self.iprime = <uint64_t> mod_inverse(self.params.prime, self.params.domain)
        cdef affineCipherParameters params
        fillAffineCipherParameters(
            &params,
            self.params.domain,
            self.iprime,
            self.params.domain - self.params.post_offset,
            self.params.domain - self.params.pre_offset,
        )
        # result must be >= 0 and < domain, which is Py_ssize_t in __init__
        cdef Py_ssize_t i = <Py_ssize_t> affineCipher(&params, value)

        # contains test + calculate slice index
        if self.step > 0:
            if i >= self.start and i < self.stop and (i - self.start) % self.step == 0:
                return (i - self.start) / self.step
        elif self.step < 0:
            if i > self.stop and i <= self.start and (i - self.start) % self.step == 0:
                return (i - self.start) / self.step
        raise ValueError(f'{value} is not in slice')

    def parameters(self):
        """
        Returns the affine parameters as tuple
        ``(domain, prime, pre_offset, post_offset)``.
        """
        return (
            self.params.domain,
            self.params.prime,
            self.params.pre_offset,
            self.params.post_offset,
        )

    def extents(self) -> slice:
        """
        Returns the extents (start, stop, step) of this instance as a :class:`slice`.

        .. note::
            ``stop`` may not be the exact value you expect.
            E.g., for a cipher ``p`` and slice ``p[:10::2]`` you might expect 10,
            but you will get 9 instead.
            That is because this slice ends at index 8 and stop always points to
            the next index (or previous if iterating backwards).
            This is necessary to make ``p[:10::2][::-1]`` and similar behave like
            a tuple or list in the same situation.
        """
        return slice(self.start, self.stop, self.step)

    def invert(self) -> AffineCipher:
        """
        Returns the inverse of this affine cipher, i.e.,
        if ``p`` is an :class:`AffineCipher` and ``ip = p.invert()``,
        then ``ip[p[x]] = x`` for all valid inputs ``x``.

        .. note::
            Slices cannot be inverted currently.
            Use :meth:`AffineCipher.expand` to obtain the full permutation first.
        """
        # for now, slices cannot be inverted
        # domain is originally a Py_ssize_t in __init__
        if self.start > 0 \
        or self.stop < <Py_ssize_t> self.params.domain \
        or self.step != 1:
            raise RuntimeError(
                'cannot invert a slice, use expand() to obtain the full permutation'
            )
        if self.iprime == 0:
            self.iprime = <uint64_t> mod_inverse(self.params.prime, self.params.domain)
        cdef AffineCipher ac = AffineCipher.__new__(AffineCipher)
        fillAffineCipherParameters(
            &ac.params,
            self.params.domain,
            self.iprime,
            self.params.domain - self.params.post_offset,
            self.params.domain - self.params.pre_offset,
        )
        ac.start = 0
        # domain is originally a Py_ssize_t in __init__
        ac.stop = <Py_ssize_t> self.params.domain
        ac.step = 1
        ac.iprime = self.params.prime
        return ac

    def is_slice(self) -> bool:
        """
        Returns ``True`` if this cipher represents a slice,
        and ``False`` if it covers the full permutation.
        """
        # domain is originally a Py_ssize_t in __init__
        cdef int ret = self.start > 0 \
            or self.stop < <Py_ssize_t> self.params.domain \
            or self.step != 1
        return ret != 0

    def expand(self) -> AffineCipher:
        """
        Return a new cipher with the same parameters, but slice extents are
        set to their initial values ``(0, domain, 1)``.
        """
        cdef AffineCipher ac = AffineCipher.__new__(AffineCipher)
        ac.params = self.params
        ac.start = 0
        # domain is originally a Py_ssize_t in __init__
        ac.stop = <Py_ssize_t> self.params.domain
        ac.step = 1
        ac.iprime = self.iprime
        return ac
