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
    ddistance_center = (ddistance_left + ddistance_right) / 2

    dtheta = (ddistance_right - ddistance_left) / s  # radians
    dx = ddistance_center * math.cos(state[2] + dtheta / 2)
    dy = ddistance_center * math.sin(state[2] + dtheta / 2)

    velocity_left = 2 * math.pi * (dtick_left / q) / 0.001
    velocity_right = 2 * math.pi * (dtick_right / q) / 0.001
    phi = state[2] - math.pi / 2

    # if dtheta != 0:
    #     dx = (ddistance_center / (2.2250738585072014e-308 + dtheta)) * (
    #         math.cos(phi + dtheta) - math.cos(phi)
    #     )
    #     dy = (ddistance_center / (2.2250738585072014e-308 + dtheta)) * (
    #         math.sin(phi + dtheta) - math.sin(phi)
    #     )
    # else:
    #     dx = math.cos(state[2] + dtheta / 2) * ddistance_center
    #     dy = math.sin(state[2] + dtheta / 2) * ddistance_center

    state = state + np.array([dx, dy, dtheta])

    return (
        state,
        ddistance_center,
        ddistance_left,
        ddistance_right,
        dx,
        dy,
        dtheta,
        velocity_left,
        velocity_right,
    )


def simulate(df_l, df_r):
    # interpolate data at fixed timestamps

    statevec = []  # state vector [x,y,theta]
    state = np.array([0, 0, math.radians(0)])

    dtick_left_vec = [0]
    dtick_right_vec = [0]
    distance_left_vec = [0]
    distance_right_vec = [0]
    distance_center_vec = [0]
    velocity_left_vec = []
    velocity_right_vec = []
    dx_vec = []
    dy_vec = []
    dtheta_vec = []
    ddistance_center_vec = []
    encoder_left = df_l["data"].tolist()
    encoder_right = df_r["data"].tolist()

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
            velocity_left,
            velocity_right,
        ) = step(state, dtick_left, dtick_right)

        distance_left_vec.append(ddistance_left + distance_left_vec[-1])
        distance_right_vec.append(ddistance_right + distance_right_vec[-1])
        distance_center_vec.append(ddistance_center + distance_center_vec[-1])
        ddistance_center_vec.append(ddistance_center)
        velocity_left_vec.append(velocity_left)
        velocity_right_vec.append(velocity_right)

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
        velocity_left_vec,
        velocity_right_vec,
    )


def compute_encoder_speed(df):
    timevec = df["Time (rel)"]
    encodervec = df["data"]
    encoderspeedvec = []
    dtvec = []

    for i in range(len(encodervec) - 1):
        dt = timevec.iloc[i + 1] - timevec.iloc[i]
        dtvec.append(dt)
        dx = (encodervec.iloc[i + 1] - encodervec.iloc[i]) * (60 / 3600)  # rpm
        encoderspeed = dx / dt
        encoderspeedvec.append(encoderspeed)
    return encoderspeedvec, dtvec
