import math


def calc_tau_omega(u, v, xi, eta, phi):
    delta = normalize_angle(u - v)
    A = math.sin(u) - math.sin(delta)
    B = math.cos(u) - math.cos(delta) - 1.0
    t1 = math.atan2(eta * A - xi * B, xi * A + eta * B)
    t2 = 2.0 * (math.cos(delta) - math.cos(v) - math.cos(u)) + 3.0
    tau = 0.0
    if t2 < 0:
        tau = normalize_angle(t1 + math.pi)
    else:
        tau = normalize_angle(t1)
    omega = normalize_angle(tau - u + v - phi)
    return tau, omega


def normalize_angle(angle):
    a = math.fmod(angle + math.pi, 2.0 * math.pi)
    if a < 0.0:
        a += 2.0 * math.pi
    return a


def cartesian_to_polar(x, y):
    r = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)
    return r, theta


def compute_string_index(x_grid, y_grid, phi_grid):
    return x_grid + "_" + y_grid + "_" + phi_grid
