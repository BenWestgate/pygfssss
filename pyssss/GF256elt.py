#!/usr/bin/env python
#
#  Copyright 2020 Nimrod Zimerman
#  Copyright 2010 Mathias Herberts
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

class GF256elt:
    """A class for representing GF256 (GF(2^8)) elements.
   Those elements are representations of polynomials over GF(2) with
   each bit being the coefficient of x^k for k an integer in [0,7].
   The log/exp tables are generated by generate_logexp_tables or generate_pplogexp_tables."""

    __logtable = []
    __exptable = []

    def __init__(self, value):
        self.__bytevalue = value % 256

    def __add__(self, other):
        if isinstance(other, GF256elt):
            return GF256elt(self.__bytevalue ^ other.__bytevalue)
        else:
            raise Exception()

    def __sub__(self, other):
        """In GF256 (and more generally in GF(2^n)) a + b = a - b so just call __add__"""
        if isinstance(other, GF256elt):
            return self.__add__(other)
        else:
            raise Exception()

    def __mul__(self, other):
        if not isinstance(other, GF256elt):
            raise Exception()

        # If one of the terms is 0, return 0
        if self.__bytevalue == 0 or other.__bytevalue == 0:
            return GF256elt(0)

        # Extract the log of each term then determine the new power

        p = (self.log() + other.log()) % 255

        return GF256elt(GF256elt.__exptable[p])

    def __truediv__(self, other):
        if not isinstance(other, GF256elt):
            raise Exception()

        # If second term is 0, raise an exception
        if other.__bytevalue == 0:
            raise Exception()

        # If first term is 0, return 0
        if self.__bytevalue == 0:
            return GF256elt(0)

        # Compute the new power from the logs of the operands

        p = (self.log() - other.log()) % 255

        if p < 0:
            p += 255

        return GF256elt(GF256elt.__exptable[p])

    def log(self):
        """Compute the power n so that x^n is equivalent to self in GF256."""

        if self.__bytevalue == 0:
            raise Exception()

        # Use the lookup table for faster computations
        return GF256elt.__logtable[self.__bytevalue]

    def __hex__(self):
        return "%02x" % self.__bytevalue

    def __int__(self):
        return self.__bytevalue

    def __str__(self):
        return str(self.__bytevalue)

    def __eq__(self, other):
        return self.__bytevalue == other.__bytevalue

    @staticmethod
    def generate_pplogexp_tables(prime_poly):
        """Generate logarithm and exponential tables for Gf(256) with a prime
       polynomial whose value is 'prime_poly'."""

        gf_order = 256

        GF256elt.__logtable = [0] * gf_order
        GF256elt.__exptable = [0] * gf_order

        GF256elt.__logtable[0] = (1 - gf_order) & 0xff
        GF256elt.__exptable[0] = 1

        for i in range(1, gf_order):
            GF256elt.__exptable[i] = GF256elt.__exptable[i - 1] * 2
            if GF256elt.__exptable[i] >= gf_order:
                GF256elt.__exptable[i] ^= prime_poly

            GF256elt.__exptable[i] &= 0xff
            GF256elt.__logtable[GF256elt.__exptable[i]] = i

    @staticmethod
    def generate_logexp_tables():
        """Generate logarithm and exponential tables for the GF(256) generator 0x03
        and the modulo polynomial x^8 + x^4 + x^3 + x + 1 (0x11b) as defined
        in Rijndael.
        This method generates the same tables as Logtable and Alogtable that can be
        found in file boxes-ref.dat in the reference implementation of Rijndael v2.2.

        see U{http://www.samiam.org/galois.html}."""

        GF256elt.__logtable = [0] * 256
        GF256elt.__exptable = [0] * 256

        # First exponential is 0x03 to the 0th power
        exp = 1

        for exponent in range(255):
            exp &= 0xff
            GF256elt.__exptable[exponent] = exp
            # Multiply exp by three
            d = exp & 0x80
            exp <<= 1

            if d == 0x80:
                exp ^= 0x1b

            exp ^= GF256elt.__exptable[exponent]

            GF256elt.__logtable[GF256elt.__exptable[exponent]] = exponent

        GF256elt.__exptable[255] = GF256elt.__exptable[0]
        GF256elt.__logtable[0] = 0

    @staticmethod
    def dump_tables():
        print(GF256elt.__exptable)
        print(GF256elt.__logtable)


#
# Generate log/exp tables based on a prime polynomial
#
# Possible values of PP are 285 299 301 333 351 355 357 361 369 391 397 425 451 463 487 501
#
#

#
# For Rijndael compatibility (0x11b prime polynomial and 0x03 as generator)
#
# GF256elt.generate_logexp_tables()

#
# For buttsoft/QR Code/gfshare compatibility (0x11d prime polynomial)
#
GF256elt.generate_pplogexp_tables(0x11d)
