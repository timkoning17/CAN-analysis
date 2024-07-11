import math
import numpy as np
import pandas as pd
import lib
import stateestimator
import matplotlib.pyplot as plt
from datetime import datetime

# filename = "./logs/1106/motorright-JStopright.csv"
# filename = "./logs/1106/JSstop.csv"
# filename = "./logs/1106/motorright-byte2-ak1.csv"
# filename = "./logs/1306/encoders.csv"
# filename = "./logs/raw_values_pump.csv"
# filename = "./logs/raw_values.csv"
# filename="./logs/0705/all_joystick_knobs.csv"
# filename = "./logs/full_rotation_leftright.csv"
# filename = "./logs/multiple_rotations_rightleft.csv"

# filename = "./logs/0807/videolog.csv"
# filename = "./logs/0807/horizontal2.csv"
# filename = "./logs/0807/square-3m.csv"
# filename = "./logs/0807/rotation.csv"
# filename = "./logs/0807/wheelrotationleft.csv"
# filename = "./logs/0807/horizontal3x.csv"
# filename = "./logs/0807/rot-3.csv"

# filename = "./logs/0907/manual_left-right1_x3.csv"
# filename = "./logs/0907/manual_left-right3x.csv"
# filename = "./logs/0907/verticalx3.csv"
# filename = "./logs/0907/horizontalx3_frontpointingright.csv"
# filename = "./logs/0907/horizontalx3_frontpointingleft.csv"
# filename = "./logs/0907/diagonalx3.csv"

# filename = "./logs/0907/horizontal_4.csv"
# filename = "./logs/0907/horizontalx3_3.csv"
# filename = "./logs/0907/free.csv"
# filename = "./logs/0907/square.csv"

# filename = "./logs/0907/horizontal_5.csv"
# filename = "./logs/0907/vertical_2.csv"
# filename = "./logs/0907/free_3.csv"
# filename = "./logs/0907/square.csv"

# filename = "./logs/0907/horizontal_fast.csv"
# filename = "./logs/0907/100hz.csv"
# filename = "./logs/0907/manual-100hz-3turns.csv"
# filename = "./logs/0907/horizontal-100hz.csv"
# filename = "./logs/0907/vertical-100hz.csv"

# filename = "./logs/1007/20rotationsmanually.csv"
# filename = "./logs/1007/8rotationsfloor_360mmleft.csv"

# filename = "./logs/1007/8rotationsbackforth.csv"
# filename = "./logs/1007/8rotationsbackforth_2.csv"
# filename = "./logs/1007/8rotationsfloor_360mmleft.csv"
# filename = "./logs/1007/free_2.csv"
filename = "./logs/1007/circle.csv"
# filename = "./logs/1007/backforth.csv"

df = pd.read_csv(filename)

### Data manipulation

time_zero = (
    datetime.strptime(df["Time (abs)"].iloc[0], "%H:%M:%S.%f")
    .replace(datetime.now().year)
    .timestamp()
)  # replace the year with current year to avoid OS timestamp errors
time_relative = lib.create_relative_time(df, time_zero)
df["Time (rel)"] = time_relative

# split dataframe per ID
drive_right = df[df["ID (hex)"] == "202"]
drive_left = df[df["ID (hex)"] == "201"]
raw_values = df[df["ID (hex)"] == "185"]
ipc_input = df[df["ID (hex)"] == "183"]
speed_feedback_left = df[df["ID (hex)"] == "281"]
speed_feedback_right = df[df["ID (hex)"] == "282"]
# encoder_l = df[df["ID (hex)"] == "1B2"]
# encoder_r = df[df["ID (hex)"] == "1B3"]
encoder_l = df[df["ID (hex)"] == "1B3"]
encoder_r = df[df["ID (hex)"] == "1B2"]

######### extract CAN commands
timevec_r, speedvec_r, quickstop_r, halt_r, cont_r = lib.vel_cmnd(drive_right)
timevec_l, speedvec_l, quickstop_l, halt_l, cont_l = lib.vel_cmnd(drive_left)

timevec_speed_l, feedback_left = lib.speed_feedback(speed_feedback_left)
timevec_speed_r, feedback_right = lib.speed_feedback(speed_feedback_right)

df_encoder_left = lib.encoder_readout(encoder_l)
df_encoder_right = lib.encoder_readout(encoder_r)
timevec_encoder_left = df_encoder_left["Time (rel)"]
timevec_encoder_right = df_encoder_right["Time (rel)"]
# encoder_left = [x - encoder_left[0] for x in encoder_left]
# encoder_right = [x - encoder_right[0] for x in encoder_right]

(
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
) = stateestimator.simulate(df_encoder_left, df_encoder_right)

x = []
y = []
theta = []
theta_deg = []

for state in statevec:
    x.append(state[0])
    y.append(state[1])
    theta.append(state[2])
    theta_deg.append(state[2] * 360 / (2 * math.pi))

# plt.plot(velocity_left_vec)
# plt.plot(velocity_right_vec)

########## RC raw stick values
raw_timestamp, bytes = lib.raw_stick_str_to_hexstr(raw_values)
raw_left = bytes[0]
raw_right = bytes[1]
raw_drive_speed = bytes[2]
raw_swing_arm_speed = bytes[3]
raw_drive_adjust = bytes[4]

(
    activate,
    DI_right,
    DI_left,
    swing_on,
    swing_overrule,
    step_slow,
    step_fast,
    pump,
    winch_left,
    winch_right,
    winch_up,
    winch_down,
    winch_selector1,
    winch_selector2,
    left_backwards,
    right_backwards,
    actuator_up,
    actuator_down,
    light,
) = lib.bitmask_decode(bytes)


########### Plotting
plotting = 0
plotting1 = 1

if plotting1:

    plt.figure()
    plt.title("x and y distances")
    plt.plot(x, label="x")
    plt.plot(y, label="y")
    plt.legend()

    plt.figure()
    # plt.xlim([-310,1200])
    # plt.ylim([-310,1200])
    plt.title("Global x y coordinates")
    plt.plot(x, y, ".")

    ax = plt.gca()
    # ax.set_ylim([-50, 50])
    ax.set_aspect("equal")
    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")

    plt.figure()
    plt.title("distance left right and center")
    plt.plot(distance_center_vec, label="d center")
    plt.plot(distance_left_vec, label="d left")
    plt.plot(distance_right_vec, label="d right")
    plt.legend()

    plt.figure()
    plt.title("Angle with respect to start position")
    plt.plot(theta_deg, label="theta [deg]")
    plt.xlabel("")
    plt.ylabel("theta [rad]")
    plt.grid()

    plt.figure()
    plt.plot(dx_vec, label="dx")
    plt.plot(dy_vec, label="dy")
    plt.grid()
    plt.legend()

    plt.figure()
    plt.title("encoder position absolute left")
    plt.plot(timevec_encoder_left, df_encoder_left["data"])
    plt.figure()
    plt.title("encoder position absolute right")
    plt.plot(timevec_encoder_right, df_encoder_right["data"], "-.")


if plotting:  # speed and feedback
    plt.figure()

    plt.plot(timevec_speed_l, feedback_left, label="feedback left")
    plt.plot(timevec_speed_r, feedback_right, label="feedback right")
    plt.plot(timevec_l, speedvec_l, label="vel cmd left")
    plt.plot(timevec_r, speedvec_r, label="vel cmd right")
    plt.legend()

    plt.figure()  # speed command drive left
    plt.plot(timevec_l, speedvec_l)
    plt.plot(raw_timestamp, DI_left, ".r", markersize=1, label="DI left")
    plt.vlines(quickstop_l, 0, 3000, colors="r")
    plt.vlines(halt_l, 0, 3000, colors="b")
    plt.vlines(cont_l, 0, 3000, colors="k")
    plt.xlabel("Time [s]")
    plt.ylabel("Velocity command [RPM]")
    plt.title("Left drive")

    plt.figure()  # speed command drive right
    plt.plot(timevec_r, speedvec_r)
    plt.plot(raw_timestamp, DI_right, ".r", markersize=1, label="DI right")
    plt.vlines(quickstop_r, 0, 3000, colors="r")
    plt.vlines(halt_r, 0, 3000, colors="b")
    plt.vlines(cont_r, 0, 3000, colors="k")
    plt.xlabel("Time [s]")
    plt.ylabel("Velocity command [RPM]")
    plt.title("Right drive")

if plotting:  # byte 2, byte 3, byte 4
    plt.figure()
    plt.plot(raw_timestamp, raw_drive_speed, label="drive speed")
    plt.plot(raw_timestamp, raw_swing_arm_speed, label="swing arm speed")
    plt.plot(raw_timestamp, raw_drive_adjust, label="drive adjust")
    plt.legend()
    plt.title("Drive speed, swing arm speed & drive adjust")
    plt.xlabel("Time [s]")
    plt.ylabel("POTmeter out [8 bit]")

if plotting:  # byte 0, byte 1
    plt.figure()
    plt.plot(raw_timestamp, raw_left, label="Left analog")
    plt.plot(raw_timestamp, DI_left, "*b", markersize=2, label="DI left")
    plt.plot(raw_timestamp, raw_right, label="Right analog")
    plt.plot(raw_timestamp, DI_right, ".r", markersize=1, label="DI right")
    plt.xlabel("Time [s]")
    plt.ylabel("POTmeter out [8 bit]")
    plt.legend()
    plt.title("Left and Right motor drives")

if plotting:
    plt.figure()
    plt.plot(raw_timestamp, activate, label="activate")
    plt.plot(raw_timestamp, swing_on, ".-", label="swing on")
    plt.plot(raw_timestamp, swing_overrule, label="swing overrule")
    plt.plot(raw_timestamp, pump, label="pump")
    plt.xlabel("Time [s]")
    plt.title("Swing arm, step timer & pump")
    plt.legend()

if plotting:
    plt.figure()
    plt.plot(raw_timestamp, step_fast, label="step timer fast")
    plt.plot(raw_timestamp, step_slow, label="step timer slow")
    plt.xlabel("Time [s]")
    plt.title("Step timer")
    plt.legend()

if plotting:
    plt.figure()
    plt.plot(raw_timestamp, winch_left, label="winch left")
    plt.plot(raw_timestamp, winch_right, label="winch right")
    plt.plot(raw_timestamp, winch_up, label="winch up")
    plt.plot(raw_timestamp, winch_down, label="winch down")
    plt.plot(raw_timestamp, winch_selector1, label="winch selector 1")
    plt.plot(raw_timestamp, winch_selector2, label="winch selector 2")
    plt.xlabel("Time [s]")
    plt.title("Winch control")
    plt.legend()

if plotting:
    plt.figure()
    plt.title("actuator up/down & light")
    plt.plot(raw_timestamp, actuator_down, label="actuator down")
    plt.plot(raw_timestamp, actuator_up, label="actuator up")
    plt.plot(raw_timestamp, light, label="light")
    plt.xlabel("Time [s]")
    plt.legend()

plt.show()
