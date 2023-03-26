import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

EMA26_PERIOD = 26
EMA12_PERIOD = 12
SIGNAL9_PERIOD = 9
START_MONEY = 1000


def get_data_from_csv_file(fileName):
    df = pd.read_csv(fileName)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def calculate_alpha(period):
    alpha = 2/(period+1)
    return alpha


def calculate_EMA_factor(period):
    alpha = calculate_alpha(period)
    factor = 0
    for i in range(0, period+1):
        factor += (1-alpha)**i
    return factor


def copy_slice_of_list(list):
    newList = []
    for item in list:
        item = float(item)
        newList.append(item)
    return newList


def calculate_EMA(period, samples):
    ema = 0
    alpha = calculate_alpha(period)
    factor = calculate_EMA_factor(period)
    for i in range(period, -1, -1):
        ema += samples[i] * (1-alpha)**(period-i)
    ema /= factor
    return ema


def sell_actions(money, actions, action_cost):
    money += actions * action_cost
    actions = 0
    return money, actions


def buy_actions(money, actions, action_cost):
    actions += money // action_cost
    money = money - actions*action_cost
    return money, actions


def check_how_intersect(macd, signal, index):
    if macd[index-1] < signal[index-11] and macd[index] > signal[index-10]:
        action = sell_actions
        return action
    elif macd[index-1] > signal[index-11] and macd[index] < signal[index-10]:
        action = buy_actions
        return buy_actions
    else:
        return None
    

def generate_plot(data_list, macd, signal, title, time_start, time_stop,  fig_width=7, fig_height=7):
    fig, ax = plt.subplots(2)
    
    fig.set_figwidth(fig_width)
    fig.set_figheight(fig_height)

    x = data_list["Date"][time_start:time_stop]
    y = data_list["Open"][time_start:time_stop]

    line0, = ax[0].plot(x, y, label="Value")
    if fig_width == 7:
        date_format = mdates.DateFormatter('%Y-%m-%d')
        ax[0].xaxis.set_major_formatter(date_format)
        ax[1].xaxis.set_major_formatter(date_format)
        ax[0].xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax[1].xaxis.set_major_locator(mdates.DayLocator(interval=7))

    ax[0].legend(handles=[line0])
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Value")

    ax[0].sharex(ax[1])

    x = data_list["Date"][time_start:time_stop]
    y = macd[time_start:time_stop]
    y_signal = signal[time_start:time_stop]

    line1, = ax[1].plot(x, y, label="MACD")
    line2, = ax[1].plot(x, y_signal, label="Signal")

    ax[1].legend(handles=[line1, line2])
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("MACD")
    fig.suptitle(title, fontsize=15)
    plt.show()


max_money = -10
max_actions = -10
max_money_date = ""
max_actions_date = ""
money = START_MONEY
actions = 0
data_list = get_data_from_csv_file("MSFT.csv")
sample_list = data_list["Open"]
macd = []
signal = []
for i in range(EMA26_PERIOD+1, len(data_list)):
    ema26 = calculate_EMA(EMA26_PERIOD, copy_slice_of_list(
        sample_list[i-EMA26_PERIOD-1:i]))
    ema12 = calculate_EMA(EMA12_PERIOD, copy_slice_of_list(
        sample_list[i-EMA12_PERIOD-1:i]))
    macd.append(ema12 - ema26)

for i in range(SIGNAL9_PERIOD+1, len(macd)):
    signal.append(calculate_EMA(SIGNAL9_PERIOD, macd[i-SIGNAL9_PERIOD-1:i]))
    action = check_how_intersect(macd, signal, i)
    if action:
        money, actions = action(money, actions, float(sample_list[i]))
        if money > max_money:
            max_money = money
            max_money_date = i
        if actions > max_actions:
            max_actions = actions
            max_actions_date = i

nones = []
for _ in range(EMA26_PERIOD+1):
    nones.append(None)
macd = nones + macd
for _ in range(SIGNAL9_PERIOD+1):
    nones.append(None)
signal = nones + signal

max_actions_date += EMA26_PERIOD
max_money_date += EMA26_PERIOD

money_in_actions = float(sample_list[len(sample_list)-1]) * actions
income = money_in_actions + money - START_MONEY
income = round(income, 2)
if income > 0:
    print("The income is " + str(income))
else:
    print("The loss is " + str(income))

generate_plot(data_list, macd, signal, "Actions values and MACD indicator for period of 1000 days", 0, len(sample_list), 12, 7)
generate_plot(data_list, macd, signal, "Best transaction - sell", max_money_date-10, max_money_date+10)
generate_plot(data_list, macd, signal,"Best transaction - buy", max_actions_date-10, max_actions_date+10)

