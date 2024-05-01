import numpy as np
import pandas as pd

filename = "./logs/statusword-quickstopCorrect.csv"

df = pd.read_csv(filename)
data = df['Data (hex)'].astype(str)

vel_sp = []
for i in data:
    if len(i)==23:
        if (i[21] == '3') and (i[22] == '1'):
            vel_sp.append(bytes.fromhex(i[0:5]))

print(vel_sp)
