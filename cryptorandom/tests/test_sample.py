"""Unit tests for cryptorandom sampling functions."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import numpy as np
from ..sample import *
from nose.tools import assert_raises, raises


class fake_generator():
    """
    This generator just cycles through the numbers 0,...,9.
    """
    def __init__(self):
        self.counter = 0

    def next(self):
        """
        Get the next number
        """
        self.counter += 1
        if self.counter > 9:
            self.counter = self.counter % 10

    def random(self, size=None):
        """
        Generate floats. They go from 0, 0.1, ..., 0.9 and then wrap back.
        size controls the number generated. If size=None, just one is produced.
        """
        if size == None:
            self.next()
            return self.counter/10
        else:
            rand = []
            for i in range(size):
                self.next()
                rand.append(self.counter/10)
            return rand

    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated.
        If size=None, just one is produced.
        """
        assert a <= b, "lower and upper limits are switched"

        if size == None:
            return int(a + (self.random()*10) % (b-a))
        else:
            return np.reshape(np.array([int(a + (self.random()*10) % (b-a)) \
                for i in np.arange(np.prod(size))]), size)


def test_fake_generator():
    """
    Make sure the fake generator works as expected
    """

    ff = fake_generator()
    out = ff.randint(0, 10, 10)
    expected = np.concatenate([np.arange(1, 10), np.zeros(1)])
    assert (out == expected).all()
    assert ff.random() == (expected[-1]+1)/10

    ff = fake_generator()
    out = ff.randint(1, 11, 10)
    assert (out == expected+1).all()

    ff = fake_generator()
    out = ff.randint(0, 20, 10)
    assert (out == expected).all()

    ff = fake_generator()
    out = ff.random(2)
    assert out == [0.1, 0.2]


@raises(AssertionError)
def test_random_sample_bad_N():
    randomSample(-2, 2)


@raises(ValueError)
def test_random_sample_bad_a():
    randomSample(2.5, 2)


@raises(AssertionError)
def test_random_sample_bad_p():
    randomSample(5, 2, p=[0.25]*4)


@raises(AssertionError)
def test_random_sample_bad_size():
    randomSample(2, 5)


@raises(TypeError)
def test_random_sample_bad_method1():
    randomSample(5, 2, method="Exponential")


@raises(ValueError)
def test_random_sample_bad_method2():
    randomSample(5, 2, replace=True, method="PIKK")


def test_fykd():
    """
    Test Fisher-Yates shuffle for random samples, fykd_sample
    """
    ff = fake_generator()
    sam = fykd_sample(5, 2, prng=ff)
    assert sam == [1, 2]

    ff = fake_generator()
    sam = randomSample(5, 2, method="Fisher-Yates", prng=ff)
    assert (sam+1 == [1, 2]).all() # shift to 1-index


def test_PIKK():
    """
    Test PIKK
    """
    ff = fake_generator()
    sam = PIKK(5, 2, prng=ff)
    assert (sam == [1, 2]).all()

    ff = fake_generator()
    sam = randomSample(5, 2, method="PIKK", prng=ff)
    assert (sam+1 == [1, 2]).all() # shift to 1-index


def test_Cormen():
    """
    Test Cormen et al recursive Random_Sample
    """
    ff = fake_generator()
    sam = Random_Sample(5, 2, prng=ff)
    assert sam == [2, 3]

    ff = fake_generator()
    sam = randomSample(5, 2, method="Cormen", prng=ff)
    assert (sam+1 == [2, 3]).all() # shift to 1-index


@raises(RuntimeError)
def test_cormen_recursion_depth():
    Random_Sample(2000, 1500)


def test_Waterman_R():
    """
    Test Waterman's algorithm R
    """
    ff = fake_generator()
    sam = Algorithm_R(5, 2, prng=ff)
    assert sam == [1, 3]

    ff = fake_generator()
    sam = randomSample(5, 2, method="Waterman_R", prng=ff)
    assert (sam+1 == [1, 3]).all() # shift to 1-index


def test_sbi():
    """
    Test sample_by_index
    """
    ff = fake_generator()
    sam = sample_by_index(5, 2, prng=ff)
    assert sam == [2, 3]

    ff = fake_generator()
    sam = randomSample(5, 2, method="sample_by_index", prng=ff)
    assert (sam+1 == [2, 3]).all() # shift to 1-index


def test_Vitter_Z():
    """
    Test Vitter's algorithm Z
    """
    ff = fake_generator()
    sam = Algorithm_Z(5, 2, prng=ff)
    assert sam == [4, 2]

    ff = fake_generator()
    sam = randomSample(5, 2, method="Vitter_Z", prng=ff)
    assert (sam+1 == [4, 2]).all() # shift to 1-index

    ff = fake_generator()
    sam = Algorithm_Z(500, 2, prng=ff)
    assert sam == [420, 265]

    ff = fake_generator()
    sam = randomSample(500, 2, method="Vitter_Z", prng=ff)
    assert (sam+1 == [420, 265]).all() # shift to 1-index


def test_elimination_sample():
    """
    Test elimination_sample
    """
    ff = fake_generator()
    sam = elimination_sample(2, [0.2]*5, prng=ff)
    assert (sam == [1, 1]).all()

    ff = fake_generator()
    sam = elimination_sample(2, [0.2]*5, replace=False, prng=ff)
    assert (sam == [1, 2]).all()

    ff = fake_generator()
    sam = randomSample(5, 2, p=[0.2]*5, replace=True, method="Elimination", prng=ff)
    assert (sam+1 == [1, 1]).all() # shift to 1-index

    ff = fake_generator()
    sam = randomSample(5, 2, p=[0.2]*5, replace=False, method="Elimination", prng=ff)
    assert (sam+1 == [1, 2]).all() # shift to 1-index


def test_exponential_sample():
    """
    Test elimination_sample
    """
    ff = fake_generator()
    sam = exponential_sample(2, [0.2]*5, prng=ff)
    assert (sam == [5, 4]).all()

    ff = fake_generator()
    sam = randomSample(5, 2, p=[0.2]*5, replace=False, method="Exponential", prng=ff)
    assert (sam+1 == [5, 4]).all() # shift to 1-index