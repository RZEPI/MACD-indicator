import pandas as pd
import matplotlib.pyplot as plplot

EMA26_PERIOD = 26
EMA12_PERIOD = 12
SIGNAL9_PERIOD = 9

def get_data_from_csv_file(fileName):   
    df = pd.read_csv(fileName)
    df['Date'] = pd.to_datetime(df['Date'])
    return(df)

def calculate_alpha(period):
    alpha = 2/(period+1)
    return alpha

def calculate_EMA_factor(period):
    alpha = calculate_alpha(period)
    factor = 0
    for i in range(0,period+1):
        factor += (1-alpha)**i
    return factor

def copy_slice_of_list_and_remove_dollar(list):
    newList = []
    for item in list:
        item = item[1:len(item)]
        item = float(item)
        newList.append(item)
    return newList

def copy_slice_of_list(list):
    newList = []
    for item in list:
        newList.append(item)
    return newList

def calculate_EMA(period, samples):
    ema = 0
    alpha = calculate_alpha(period)
    factor = calculate_EMA_factor(period)
    for i in range(period-1, 0, -1):
        ema = samples[i]*(1-alpha)**i
    ema += samples[0]
    ema /= factor
    return ema

def copy_and_reverse_list(list):
    newList = []
    for item in list:
        newList.append(item)
    newList = newList[::-1]
    return newList    

dataList = get_data_from_csv_file("data.csv")
sampleList = dataList["Low"]
MACD = []
signal = []
for i in range(EMA26_PERIOD, len(dataList)):
    ema26 = calculate_EMA(EMA26_PERIOD, copy_slice_of_list_and_remove_dollar(sampleList[i-EMA26_PERIOD:i]))
    ema12 = calculate_EMA(EMA12_PERIOD, copy_slice_of_list_and_remove_dollar(sampleList[i-EMA12_PERIOD:i]))
    MACD.append(ema12 - ema26)

for i in range(SIGNAL9_PERIOD, len(MACD)):
    signal.append(calculate_EMA(SIGNAL9_PERIOD, copy_slice_of_list(MACD[i-SIGNAL9_PERIOD:i])))

signal = signal[::-1]
fig, ax = plplot.subplots()

x = copy_and_reverse_list(dataList["Date"][EMA26_PERIOD:len(dataList)])
y = MACD[::-1]
ax.plot(x,y)
ax.plot(x[9:], signal)
plplot.show()