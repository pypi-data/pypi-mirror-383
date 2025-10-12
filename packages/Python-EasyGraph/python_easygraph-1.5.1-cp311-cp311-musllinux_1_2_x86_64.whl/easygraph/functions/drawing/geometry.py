import math

from math import pi


def radian_from_atan(x, y):
    if x == 0:
        return pi / 2 if y > 0 else 3 * pi / 2
    if y == 0:
        return 0 if x > 0 else pi
    r = math.atan(y / x)
    if x > 0 and y > 0:
        return r
    elif x > 0 and y < 0:
        return r + 2 * pi
    elif x < 0 and y > 0:
        return r + pi
    else:
        return r + pi


def vlen(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def common_tangent_radian(r1, r2, d):
    value = abs(r2 - r1) / d
    alpha = math.acos(value)
    alpha = alpha if r1 > r2 else pi - alpha
    return alpha


def polar_position(r, theta, start_point):
    import numpy as np

    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return np.array([x, y]) + start_point


def rad_2_deg(rad):
    return rad * 180 / pi
