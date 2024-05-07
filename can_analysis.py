import numpy as np
import pandas as pd
import lib
import matplotlib.pyplot as plt
from datetime import datetime

# filename = "./logs/raw_values.csv"
filename = "./logs/raw_values.csv"
# filename = "./logs/raw_values_light_overrule.csv"
# filename = "./logs/statusword-quickstopCorrect.csv"
df = pd.read_csv(filename)

### Data manipulation
time_zero = datetime.strptime(df["Time (abs)"].iloc[0], "%H:%M:%S.%f").timestamp()
time_relative = lib.create_relative_time(df, time_zero)
df["Time"] = time_relative

# print(df.columns)

# split dataframe per ID
drive_right = df[df["ID (hex)"] == 202]
drive_left = df[df["ID (hex)"] == 201]
raw_values = df[df["ID (hex)"] == 185]


######### extract velocity commands
timevec_r, speedvec_r, quickstop_r, halt_r, cont_r = lib.vel_cmnd(drive_right)
timevec_l, speedvec_l, quickstop_l, halt_l, cont_l = lib.vel_cmnd(drive_left)

plt.figure()
plt.plot(timevec_l, speedvec_l)
plt.vlines(quickstop_l, 0, 10000, colors="r")
plt.vlines(halt_l, 0, 10000, colors="b")
plt.vlines(cont_l, 0, 10000, colors="k")
plt.title("Left drive")
plt.figure()
plt.plot(timevec_r, speedvec_r)
plt.vlines(quickstop_r, 0, 10000, colors="r")
plt.vlines(halt_r, 0, 10000, colors="b")
plt.vlines(cont_r, 0, 10000, colors="k")
plt.title("Right drive")


# ######### raw stick values + plot
raw_timestamp, bytes = lib.raw_stick_str_to_hexstr(raw_values)

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
    actuator_up,
    actuator_down,
    light,
) = lib.bitmask_decode(bytes)


if True:
    plt.figure()
    plt.plot(raw_timestamp, bytes[0], label="Left analog")
    plt.plot(raw_timestamp, DI_left, "*b", markersize=2, label="DI left")
    plt.plot(raw_timestamp, bytes[1], label="Right analog")
    plt.plot(raw_timestamp, DI_right, ".r", markersize=1, label="DI right")
    plt.xlabel("Time [s]")
    plt.legend()
    plt.title("Left and Right motor drives")

if True:
    plt.figure()
    plt.plot(swing_on, ".-", label="swing on")
    plt.plot(swing_overrule, label="swing overrule")
    plt.plot(raw_timestamp, step_fast, label="step timer fast")
    plt.plot(raw_timestamp, step_slow, label="step timer slow")
    plt.plot(pump, label="pump")
    plt.xlabel("Time [s]")
    plt.title("Swing arm, step timer & pump")
    plt.legend()

if True:
    plt.figure()
    plt.plot(winch_left, label="winch left")
    plt.plot(winch_right, label="winch right")
    plt.plot(winch_up, label="winch up")
    plt.plot(winch_down, label="winch down")
    plt.plot(winch_selector1, label="winch selector 1")
    plt.plot(winch_selector2, label="winch selector 2")
    plt.xlabel("Time [s]")
    plt.title("Winch control")
    plt.legend()

if True:
    plt.figure()
    plt.title("actuator up/down & light")
    plt.plot(actuator_down, label="actuator down")
    plt.plot(actuator_up, label="actuator up")
    plt.plot(light, label="light")
    plt.xlabel("Time [s]")
    plt.legend()


plt.show()
