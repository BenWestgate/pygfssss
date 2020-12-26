#!/usr/bin/env python
#
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
# -*- coding: utf-8 -*-

import random

from pyssss.GF256elt import GF256elt
from pyssss.PGF256 import PGF256
from pyssss.PGF256Interpolator import PGF256Interpolator


def pickRandomPolynomial(degree, value):
  """Pick a random PGF256 polynomial P such that P(0) = value"""

  coeffs = []

  # Set f(0)
  coeffs.append(value)

  # Pick coefficients for x^n with n <= degree

  for c in range(1,degree+1):
    coeffs.append(GF256elt(random.randint(0,255)))

  return PGF256(coeffs)


def encodeByte(byte,n,k,picks):
  # Pick a random polynomial
  P = pickRandomPolynomial(k-1, GF256elt(byte))

  # Generate the keys
  keys = [bytearray() for i in range(0,n)]

  for i in range(0,n):
    X = GF256elt(picks[i])
    Y = P.f(X)

    keys[i] += bytes([int(X)])
    keys[i] += bytes([int(Y)])

  return keys


def encode(stream, outputs, k):

  n = len(outputs)

  # Allocate array to track duplicates
  picked = [False for i in range(0,256)]

  picks = []

  for i in range(0,n):

    # Pick a not yet picked X value in [1,255],

    while True:
      pick = random.randint(1, 255)
      if not picked[pick]:
        break

    # Keep track of the value we just picked
    picked[pick] = True

    picks.append(pick)

  # Loop through the chars
  while True:
    data = stream.read(1)
    if 0 == len(data):
      break
    byte = data[0]

    keys = encodeByte(byte,n,k,picks)

    for i in range(0,n):
      outputs[i].write(keys[i])


def decode(keys,output):

  interpolator = PGF256Interpolator()
  zero = GF256elt(0)

  # End Of Key
  end_of_key = False

  while not end_of_key:
    points = []
    for i in range(0,len(keys)):
      b = keys[i].read(1)
      if 0 == len(b):
        end_of_key = True
        break

      X = ord(b)

      # Extract X/Y
      Y = ord(keys[i].read(1))

      # Push point
      points.append((GF256elt(X),GF256elt(Y)))

    if end_of_key:
      if 0 != i:
        raise Exception('Unexpected EOF while reading key %d' % i)
      break

    # Decode next byte
    byte = interpolator.interpolate(points).f(zero)

    output.write(bytes([int(byte)]))


if __name__ == "__main__":

  from io import BytesIO
  input = BytesIO(b"Too many secrets, Marty!")
  outputs = []
  n = 5
  k = 3
  for i in range(n):
    outputs.append(BytesIO())

  encode(input,outputs,k)

  for i in range(n):
    print (outputs[i].getvalue().hex())

  inputs = []
  for i in range(k):
    inputs.append(outputs[i+1])

  for i in range(k):
    inputs[i].seek(0)

  output = BytesIO()
  decode(inputs,output)
  print (output.getvalue())
