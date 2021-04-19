# -*- coding: utf-8 -*-

"""
Copyright (C) 2021 Dante "laggycomputer" Dam

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sympy.ntheory import divisors


def purge_from_list(sequence, *items):
    for item in items:
        while item in sequence:
            del sequence[sequence.index(item)]


def ways_to_mul_to(n, limit):
    ret = []
    if limit > 2:
        for d in divisors(n):
            for way in ways_to_mul_to(int(n / d), limit - 1):
                ret.append(list(way) + [d])
    else:
        for d in divisors(n):
            ret.append([d, int(n / d)])

    return list(map(tuple, reversed(ret)))
