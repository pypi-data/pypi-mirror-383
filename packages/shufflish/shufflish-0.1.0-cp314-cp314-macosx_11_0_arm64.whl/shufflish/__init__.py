from __future__ import annotations

from typing import Generator, Iterable, Sequence, Tuple
from abc import ABC, abstractmethod

import array
import random
import warnings
from math import isqrt, comb, prod
from itertools import islice, combinations, chain, product
try:
    from itertools import batched
except ImportError:
    def batched(iterable, n):
        """
        Reimplementation of itertools.batched for Python < 3.12.
        """
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while batch := tuple(islice(iterator, n)):
            yield batch
from weakref import WeakValueDictionary

from ._version import __version__, __version_tuple__
from ._affine import AffineCipher


__all__ = (
    "permutation",
    "local_shuffle",
)


PRIMES = (
    18446744073709551557, 18446744073709551533, 18446744073709551521,
    18446744073709551437, 18446744073709551427, 18446744073709551359,
    18446744073709551337, 18446744073709551293, 18446744073709551263,
    18446744073709551253, 18446744073709551191, 18446744073709551163,
    18446744073709551113, 18446744073709550873, 18446744073709550791,
    18446744073709550773, 18446744073709550771, 18446744073709550719,
    18446744073709550717, 18446744073709550681, 18446744073709550671,
    18446744073709550593, 18446744073709550591, 18446744073709550539,
    18446744073709550537, 18446744073709550381, 18446744073709550341,
    18446744073709550293, 18446744073709550237, 18446744073709550147,
    18446744073709550141, 18446744073709550129, 18446744073709550111,
    18446744073709550099, 18446744073709550047, 18446744073709550033,
    18446744073709550009, 18446744073709549951, 18446744073709549861,
    18446744073709549817, 18446744073709549811, 18446744073709549777,
    18446744073709549757, 18446744073709549733, 18446744073709549667,
    18446744073709549621, 18446744073709549613, 18446744073709549583,
    18446744073709549571, 18446744073709549519, 18446744073709549483,
    18446744073709549441, 18446744073709549363, 18446744073709549331,
    18446744073709549327, 18446744073709549307, 18446744073709549237,
    18446744073709549153, 18446744073709549123, 18446744073709549067,
    18446744073709549061, 18446744073709549019, 18446744073709548983,
    18446744073709548899, 18446744073709548887, 18446744073709548859,
    18446744073709548847, 18446744073709548809, 18446744073709548703,
    18446744073709548599, 18446744073709548587, 18446744073709548557,
    18446744073709548511, 18446744073709548503, 18446744073709548497,
    18446744073709548481, 18446744073709548397, 18446744073709548391,
    18446744073709548379, 18446744073709548353, 18446744073709548349,
    18446744073709548287, 18446744073709548271, 18446744073709548239,
    18446744073709548193, 18446744073709548119, 18446744073709548073,
    18446744073709548053, 18446744073709547821, 18446744073709547797,
    18446744073709547777, 18446744073709547731, 18446744073709547707,
    18446744073709547669, 18446744073709547657, 18446744073709547537,
    18446744073709547521, 18446744073709547489, 18446744073709547473,
    18446744073709547471,
)
"""
The default set of primes used by :func:`permutation` and :class:`Permutations`.
They are the 100 largest primes that can be represented by a 64bit unsigned integer.
"""


def _modular_prime_combinations(domain, primes, k):
    """
    Generate all ``k``-combinations of the given primes that are unique mod ``domain``.
    Only considers primes that are coprime with ``domain``.
    """
    if domain == 1:
        yield 1
        return
    primes = list(dict.fromkeys(p % domain for p in primes if domain % p != 0))
    seen = set()
    ones = (1,) * (k-1)
    for p1, p2, p3 in combinations(chain(ones, primes), k):
        p = p1 * p2 * p3 % domain
        if p in seen:
            continue
        yield p
        seen.add(p)


def _modular_prime_combinations_with_repetition(domain, primes, k):
    """
    Generate all ``k``-combinations of the given primes mod ``domain``.
    Only considers primes that are coprime with ``domain``.
    May repeat values.
    """
    if domain == 1:
        yield 1
        return
    ones = (1,) * (k-1)
    primes = list(dict.fromkeys(p % domain for p in primes if domain % p != 0))
    for p1, p2, p3 in combinations(chain(ones, primes), k):
        yield p1 * p2 * p3 % domain


_COPRIME_CACHE = WeakValueDictionary()


class Permutations:
    """
    Create many permutations for the given ``domain``, i.e., a random shuffle
    of ``range(domain)``, with fixed settings.
    ``domain`` must be greater 0 and less than 2^63.
    The returned :class:`AffineCipher` is iterable, indexable, and sliceable::

        from shufflish import Permutations
        perms = Permutations(10)
        p = perms.get()

        for i in p:
            print(i)

        print(list(p))
        print(list(p[3:8]))
        print(p[3])

    See the :func:`permutation` function for details on how this works.

    .. note::
        This class can be a good choice to create many permutations in the same domain.
        It pre-calculates and stores all coprimes, so creating permutations is much
        faster than the :func:`permutation` function.
        Beware that, especially for larger than default values of ``num_primes``,
        this can occupy a *lot* of memory.
        The default settings use roughly 1.3 MiB.
    """

    def __init__(
        self,
        domain: int,
        num_primes=3,
        allow_repetition=False,
        primes: Sequence[int] = PRIMES,
    ):
        if domain <= 0:
            raise ValueError("domain must be > 0")
        if domain >= 2**63:
            raise ValueError("domain must be < 2**63")
        self.domain = domain
        # use ID of primes to avoid hashing large sequences,
        # and support unhasheable types like list
        cache_key = domain, id(primes), num_primes, allow_repetition
        self.coprimes = _COPRIME_CACHE.get(cache_key)
        if self.coprimes is None:
            if allow_repetition:
                gen = _modular_prime_combinations_with_repetition(domain, primes, num_primes)
            else:
                gen = _modular_prime_combinations(domain, primes, num_primes)
            # this step can take a little while; if another thread has added
            # the same coprimes into the cache since we last checked,
            # we should drop our array and use the cached object instead
            coprimes = array.array("Q", gen)
            self.coprimes = _COPRIME_CACHE.get(cache_key)
            if self.coprimes is None:
                _COPRIME_CACHE[cache_key] = coprimes
                self.coprimes = coprimes
        # remember number of combinations for later
        if not allow_repetition and primes is PRIMES:
            NUM_COMBINATIONS[domain] = len(self.coprimes)

    def get(self, seed=None) -> AffineCipher:
        """
        Get a permutation.
        ``seed`` determines which permutation is returned.
        A random ``seed`` is chosen if none is given.
        """
        if seed is None:
            seed = random.randrange(2**64)
        coprimes = self.coprimes
        prime = coprimes[seed % len(coprimes)]
        return _permutation(self.domain, seed, prime)

    __getitem__ = get


NUM_COMBINATIONS={}


def _select_prime(
    domain: int,
    seed: int,
    primes: Sequence[int],
    k: int,
) -> int:
    """
    Returns the ``seed``-th unique k-combiations of the given ``primes``.
    Only considers primes that are coprime with ``domain``.
    This can be quite slow.
    """
    if domain == 1:
        return 1
    gen = _modular_prime_combinations(domain, primes, k)
    num_comb = None
    if primes is PRIMES and domain in NUM_COMBINATIONS:
        num_comb = NUM_COMBINATIONS[domain]
        for _ in islice(gen, (seed % num_comb)):
            pass
        return next(gen)
    ps = list(gen)
    if primes is PRIMES:
        NUM_COMBINATIONS[domain] = len(ps)
    return ps[seed % len(ps)]


def _select_prime_with_repetition(
    domain: int,
    seed: int,
    primes: Sequence[int],
    k: int,
) -> int:
    """
    Use combinatorial unranking to determine the ``seed``-th
    ``k``-combination of the given ``primes``.
    Return the product of this combination mod domain.
    This is reasonably fast, but does not account for reptitions mod domain.
    """
    if domain == 1:
        return 1
    ones = (1,) * (k-1)
    primes = list(chain(ones, dict.fromkeys(p % domain for p in primes if domain % p != 0)))
    np = len(primes)
    seed %= comb(np, k)
    combination = []

    np -= 1
    i = 0
    while k > 0:
        # assuming the ith prime is contained in the combination,
        # calculate the number of length k-1 combinations with remaining primes
        binom = comb(np - i, k - 1)
        if seed < binom:
            # if seed is less than binom, the ith element is in the combination
            combination.append(primes[i])
            k -= 1
        else:
            # remove binom combinations from seed
            seed -= binom
        i += 1

    return prod(combination) % domain


def permutation(
    domain: int,
    seed: int | None = None,
    num_primes=3,
    allow_repetition=False,
    primes: Sequence[int] = PRIMES,
) -> AffineCipher:
    """
    Return a permutation for the given ``domain``, i.e.,
    a random shuffle of ``range(domain)``.
    ``domain`` must be greater 0 and less than 2^63.
    ``seed`` determines which permutation is returned.
    A random ``seed`` is chosen if none is given.

    The returned :class:`AffineCipher` is iterable, indexable, and sliceable::

        from shufflish import permutation
        p = permutation(10)

        for i in p:
            print(i)

        print(list(p))
        print(list(p[3:8]))
        print(p[3])

    Note the use of :class:`list`.
    Where multiple values can be returned, iterators are used to conserve memory.

    You can give a different set of ``primes`` to choose from,
    though the default set should work for most values of ``domain``,
    and the selection process is pretty robust:

    1. Remove primes that are not coprime, i.e., ``gcd(domain, prime) = 1``.
       Testing that ``prime`` is not a factor of ``domain`` is sufficient.
    2. Remove duplicates ``prime % domain``.
       In modular arithmetic, multiplication with ``prime`` and
       ``prime % domain`` produces the same result, so we use only one
       prime from each congruence class to improve uniqueness of permutations.
    3. Select the ``seed``-th combination of ``num_primes`` primes.
       If ``allow_repetition=False`` (default), repeated combinations are skipped.

    .. note::
        If you can afford a tiny chance of repeated permutations, you can use
        ``allow_repetition=True`` to significantly speed up this function.
        Empirically, we find that the first repetition occurs at earliest after
        ``domain`` seeds.
        If you need a lot of permutations for the same domain and cannot afford
        repetitions, consider the :class:`Permutations` class, which generates
        all coprimes ahead of time.
    """
    if domain <= 0:
        raise ValueError("domain must be > 0")
    if domain >= 2**63:
        raise ValueError("domain must be < 2**63")
    if seed is None:
        seed = random.randrange(2**64)
    if allow_repetition:
        prime = _select_prime_with_repetition(domain, seed, primes, num_primes)
    else:
        prime = _select_prime(domain, seed, primes, num_primes)
    return _permutation(domain, seed, prime)


def _permutation(domain: int, seed: int, prime: int) -> AffineCipher:
    """
    Here we select a pre-offset, added to the index before multiplication
    with prime, and a post-offset, added after the multiplication.
    Theoretically, a post-offset would be sufficient, as adding ``prime``
    after the multiplication is equivalent to adding 1 to the index.
    However, this would limit us to just ``UINT64MAX // prime`` different seeds.
    Instead, we use ``seed % prime`` as post-offset and add ``seed // prime``
    to the index to restore the full range of possible seeds.
    Finally, we add sqrt(domain) to the pre-offset so index 0 does not map
    to output 0.
    """
    pre_offset = (seed // prime + isqrt(domain)) % domain
    post_offset = seed % prime
    return AffineCipher(domain, prime, pre_offset, post_offset)


def local_shuffle(iterable: Iterable, chunk_size: int = 2**14, seed=None) -> Generator[int]:
    """
    Retrieve chunks of the given ``chunk_size`` from ``iterable``,
    perform a true shuffle on them, and finally, yield individual
    values from the shuffled chunks.
    ``seed`` is used to seed the random generator for the shuffle operation.
    """
    rand = random.Random(seed)
    for batch in batched(iterable, chunk_size):
        batch = list(batch)
        rand.shuffle(batch)
        yield from batch
