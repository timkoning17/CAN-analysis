import numpy as np
import pandas as pd
import lib
import matplotlib.pyplot as plt
from datetime import datetime

# filename = "./logs/1106/motorright-JStopright.csv"
# filename = "./logs/1106/JSstop.csv"
# filename = "./logs/1106/motorright-byte2-ak1.csv"
filename = "./logs/1306/encoders.csv"
df = pd.read_csv(filename)

### Data manipulation

time_zero = datetime.strptime(df["Time (abs)"].iloc[0], "%H:%M:%S.%f").replace(datetime.now().year).timestamp() # replace the year with current year to avoid OS timestamp errors
time_relative = lib.create_relative_time(df, time_zero)
df["Time"] = time_relative

# split dataframe per ID
# print(df.head())

drive_right = df[df["ID (hex)"] == 202]
drive_left = df[df["ID (hex)"] == 201]
raw_values = df[df["ID (hex)"] == 185]
ipc_input = df[df["ID (hex)"] == 183]
speed_feedback_left = df[df["ID (hex)"] == 281]
speed_feedback_right = df[df["ID (hex)"] == 282]
encoder_l = df[df["ID (hex)"] == "1B2"]
encoder_r = df[df["ID (hex)"] == "1B3"]

# print(encoder_left.head())
######### extract velocity commands in context of TxPDO
timevec_r, speedvec_r, quickstop_r, halt_r, cont_r = lib.vel_cmnd(drive_right)
timevec_l, speedvec_l, quickstop_l, halt_l, cont_l = lib.vel_cmnd(drive_left)
timevec_speed_l,feedback_left = lib.speed_feedback(speed_feedback_left)
timevec_speed_r,feedback_right = lib.speed_feedback(speed_feedback_right)
timevec_encoder_left,encoder_left = lib.encoder_readout(encoder_l)
timevec_encoder_right,encoder_right = lib.encoder_readout(encoder_r)

speedvec_left, dtvec_left = lib.compute_encoder_speed(timevec_encoder_left,encoder_left)
speedvec_right, dtvec_right = lib.compute_encoder_speed(timevec_encoder_right,encoder_right)

########## raw stick values
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

plotting = 0
plotting1=1

if 0:
    plt.figure()
    plt.plot(timevec_speed_l,feedback_left, label = 'feedback')
    # plt.plot(timevec_speed_r,feedback_right)
    plt.plot(timevec_l, speedvec_l, label = 'vel cmd')
    plt.legend()

if plotting:
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
if plotting1:

    plt.figure()
    plt.title('encoder position absolute left')
    plt.plot(timevec_encoder_left,encoder_left)
    plt.figure()
    plt.title('encoder position absolute right')
    plt.plot(timevec_encoder_right,encoder_right,'-.')
    
    plt.figure()
    plt.title('speed [rpm]')
    plt.plot(speedvec_left, label='speed left encoder')
    plt.plot(speedvec_right, label = 'speed encoder right')
    plt.legend()

    plt.figure()
    plt.title('encoder dt')
    plt.plot(dtvec_left, label = 'dt left')
    plt.plot(dtvec_right, label = 'dt right')
    plt.legend()

if plotting:
    plt.figure()
    plt.plot(raw_timestamp, left_backwards, label='left backwards')
    plt.plot(raw_timestamp, right_backwards, label='right backwards')
    plt.legend()

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
