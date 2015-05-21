import pandas as pd
import matplotlib.pyplot as plt
import pylab


df = pd.read_csv('/home/black/Dev/PycharmProjects/WhiteProject/xp_ip_scaling/stored_games_data', comment='#')


def convert_mm_ss_to_minutes(given_str):
    """
    Converts "MM:SS" to minutes.

    :param given_str:
    :return: (str)
    """

    minutes_in_str, seconds_in_str = given_str.split(':')

    return int(minutes_in_str) + int(seconds_in_str)/60


# Converts mm:ss to minutes inside dataframe.
for index_num in range(len(df['time'])):
    old_val = df['time'][index_num]
    new_val = convert_mm_ss_to_minutes(given_str=old_val)
    df.loc[index_num, 'time'] = new_val


# Fitting data with 1st degree polynomial
def plot_points_and_fit(column_name):
    a, b, *_ = pylab.polyfit(list(df['time']), list(df[column_name]), 1)
    print('a: {}\nb: {}'.format(a, b))

    # Point plot
    plt.scatter(df['time'], df['xp'])

    # Fit plot
    x_vals_of_fit = [i/10 for i in range(100, 600)]
    y_vals_of_fit = [a*i+b for i in x_vals_of_fit]
    plt.plot(x_vals_of_fit, y_vals_of_fit)


plot_points_and_fit(column_name='xp')

plt.show()
print(df)
