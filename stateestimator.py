import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


def step(state, dtick_left, dtick_right):
    # constants
    q = 16384.0  # ticks per revolution
    r = 137.5  # encoder wheel diameter in mm
    s = 462  # wheelbase in mm

    ddistance_left = dtick_left * 2 * math.pi * r / q  # mm
    ddistance_right = dtick_right * 2 * math.pi * r / q  # mm
    dtheta = (ddistance_right - ddistance_left) / s  # radians
    ddistance_center = (ddistance_left + ddistance_right) / 2
    dLR = ddistance_right - ddistance_left

    # dx = ddistance_center * math.cos(state[2] + dtheta / 2)
    # dy = ddistance_center * math.sin(state[2] + dtheta / 2)
    theta_new = state[2] + dtheta
    phi = state[2] - math.pi / 2

    if dtheta != 0:
        dx = (ddistance_center / (2.2250738585072014e-308 + dtheta)) * (
            math.cos(phi + dtheta) - math.cos(phi)
        )
        dy = (ddistance_center / (2.2250738585072014e-308 + dtheta)) * (
            math.sin(phi + dtheta) - math.sin(phi)
        )
    else:
        dx = math.cos(state[2] + dtheta / 2) * ddistance_center
        dy = math.sin(state[2] + dtheta / 2) * ddistance_center

    state = state + np.array([dx, dy, dtheta])
    # state[0] += dx
    # state[1] += dy

    return state, ddistance_center, ddistance_left, ddistance_right, dx, dy, dtheta, dLR


def simulate(timevec_encoder_left, encoder_left, timevec_encoder_right, encoder_right):
    # state [x,y,theta]
    statevec = []
    state = np.array([0, 0, math.radians(0)])
    # state = np.array([0, 0, 0])
    dtick_left_vec = [0]
    dtick_right_vec = [0]
    distance_left_vec = [0]
    distance_right_vec = [0]
    distance_center_vec = [0]
    dx_vec = []
    dy_vec = []
    dtheta_vec = []
    ddistance_center_vec = []
    dLR_vec = []

    for i in range(min(len(encoder_left) - 1, len(encoder_right) - 1)):
        dtick_left = encoder_left[i + 1] - encoder_left[i]
        dtick_right = (
            encoder_right[i + 1] - encoder_right[i]
        ) * -1  # adjust for direction
        dtick_left_vec.append(dtick_left + dtick_left_vec[-1])
        dtick_right_vec.append(dtick_right + dtick_right_vec[-1])

        (
            state,
            ddistance_center,
            ddistance_left,
            ddistance_right,
            dx,
            dy,
            dtheta,
            dLR,
        ) = step(state, dtick_left, dtick_right)
        distance_left_vec.append(ddistance_left + distance_left_vec[-1])
        distance_right_vec.append(ddistance_right + distance_right_vec[-1])
        distance_center_vec.append(ddistance_center + distance_center_vec[-1])
        ddistance_center_vec.append(ddistance_center)
        dLR_vec.append(dLR)

        statevec.append(state)
        dx_vec.append(dx)
        dy_vec.append(dy)
        dtheta_vec.append(dtheta)

    return (
        statevec,
        distance_center_vec,
        distance_left_vec,
        distance_right_vec,
        dx_vec,
        dy_vec,
        dtheta_vec,
        ddistance_center_vec,
        dLR_vec,
    )
