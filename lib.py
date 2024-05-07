from dateutil.parser import *
import pandas as pd
from datetime import datetime


def raw_stick_str_to_hexstr(df):
    byte0 = []
    byte1 = []
    byte2 = []
    byte3 = []
    byte4 = []
    byte5 = []
    byte6 = []
    byte7 = []
    timestamp = []
    for i in range(df.shape[0]):
        hexlist = df.iloc[i]["Data (hex)"].split()
        byte0.append(int("0x" + hexlist[0], base=16))  # drive left
        byte1.append(int("0x" + hexlist[1], base=16))  # drive right
        byte2.append(int("0x" + hexlist[2], base=16))  # drive speed
        byte3.append(int("0x" + hexlist[3], base=16))  # swing arm speed
        byte4.append(int("0x" + hexlist[4], base=16))  # drive adjust
        byte5.append(
            int("0x" + hexlist[5], base=16)
        )  # bit 0 = activate, 1 = DI joystick left, 2 = DI joystick right, 3 = swing arm on, 4 = swing arm overrule, 5 = step timer slow, 6 = step timer fast, 7 = pump on
        byte6.append(
            int("0x" + hexlist[6], base=16)
        )  # bit 0 = winch js left, 1 = winch js right, 2 = winch js up, 3 = winch js down, 4 = winch selector 1, 5 = winch selector 2
        byte7.append(
            int("0x" + hexlist[7], base=16)
        )  # bit 0 = actuator up, bit 1 = actuator down, bit 2 = light
        timestamp.append(df.iloc[i]["Time"])
    bytes = [byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7]
    return timestamp, bytes


def bitmask_decode(bytes):
    activate = []
    DI_left = []
    DI_right = []
    swing_on = []
    swing_overrule = []
    pump = []
    step_slow = []
    step_fast = []

    light = []
    actuator_up = []
    actuator_down = []

    winch_left = []
    winch_right = []
    winch_up = []
    winch_down = []
    winch_selector1 = []
    winch_selector2 = []

    # byte 5
    mask_activate = 1 << 0
    mask_DI_left = 1 << 1
    mask_DI_right = 1 << 2
    mask_swing_on = 1 << 3
    mask_swing_overrule = 1 << 4
    mask_step_slow = 1 << 5
    mask_step_fast = 1 << 6
    mask_pump = 1 << 7

    # byte 6
    mask_winch_left = 1 << 0
    mask_winch_right = 1 << 1
    mask_winch_up = 1 << 2
    mask_winch_down = 1 << 3
    mask_winch_selector1 = 1 << 4
    mask_winch_selector2 = 1 << 5

    # byte 7
    mask_actuator_up = 1 << 0
    mask_actuator_down = 1 << 1
    mask_light = 1 << 2
    for i in range(len(bytes[0])):
        # byte 5
        print()
        activate.append(bool(bytes[5][i] & mask_activate))
        DI_right.append((bool(bytes[5][i] & mask_DI_right) * 100 + 125))
        DI_left.append(bool(bytes[5][i] & mask_DI_left) * 100 + 125)
        swing_on.append(bool(bytes[5][i] & mask_swing_on))
        swing_overrule.append(bool(bytes[5][i] & mask_swing_overrule))
        step_slow.append(bool(bytes[5][i] & mask_step_slow))
        step_fast.append(bool(bytes[5][i] & mask_step_fast))
        pump.append(bool(bytes[5][i] & mask_pump))

        # byte 6
        winch_left.append(bool(bytes[6][i] & mask_winch_left))
        winch_right.append(bool(bytes[6][i] & mask_winch_right))
        winch_up.append(bool(bytes[6][i] & mask_winch_up))
        winch_down.append(bool(bytes[6][i] & mask_winch_down))
        winch_selector1.append(bool(bytes[6][i] & mask_winch_selector1))
        winch_selector2.append(bool(bytes[6][i] & mask_winch_selector2))

        # byte 7
        actuator_up.append(bool(bytes[7][i] & mask_actuator_up))
        actuator_down.append(bool(bytes[7][i] & mask_actuator_down))
        light.append(bool(bytes[7][i] & mask_light))

        byte5 = [
            activate,
            DI_right,
            DI_left,
            swing_on,
            swing_overrule,
            step_slow,
            step_fast,
            pump,
        ]
        byte6 = [
            winch_left,
            winch_right,
            winch_up,
            winch_down,
            winch_selector1,
            winch_selector2,
        ]
        byte7 = [actuator_up, actuator_down, light]
    return (
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
    )


def vel_cmnd(df):
    timevec = []
    speedvec = []
    quickstop = []
    halt = []
    cont = []

    for i in range(df.shape[0]):
        hexlist = df.iloc[i]["Data (hex)"].split()
        if len(hexlist) == 8:
            if hexlist[-1] == "31":
                vel_cmnd = int("0x" + hexlist[1] + hexlist[0], base=16)
                timevec.append(df.iloc[i]["Time"])
                speedvec.append(vel_cmnd)
            elif hexlist[-1] == "02":  # quickstop
                quickstop.append(df.iloc[i]["Time"])
            elif hexlist[-1] == "03":  # halt
                halt.append(df.iloc[i]["Time"])
            elif hexlist[-1] == "04":  # continue
                cont.append(df.iloc[i]["Time"])
        # print(vel_cmnd)
    return timevec, speedvec, quickstop, halt, cont


def create_relative_time(df, time_zero):
    time_rel = []
    for i in range(len(df)):
        time_rel.append(
            datetime.strptime(df["Time (abs)"].iloc[i], "%H:%M:%S.%f").timestamp()
            - time_zero
        )
    return time_rel
