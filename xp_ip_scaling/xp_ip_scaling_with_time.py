import pandas as pd
import matplotlib.pyplot as plt
import pylab


csv_path = '/home/black/Dev/PycharmProjects/WhiteProject/xp_ip_scaling/stored_games_data'
csv_path_2 = '/home/black/Downloads/lolxp.ods'
df = pd.read_csv(csv_path, comment='#')


def mm_ss_to_minutes(given_str):
    """
    Converts "MM:SS" to minutes.

    :return: (int)
    """
    minutes_in_str, seconds_in_str = given_str.split(':')
    return int(minutes_in_str) + int(seconds_in_str)/60


# Converts mm:ss to minutes inside dataframe.
for index_num in range(len(df['game-time'])):
    old_val = df['game-time'][index_num]
    new_val = mm_ss_to_minutes(given_str=old_val)
    df.loc[index_num, 'game-time'] = new_val


def columns_of_specific_outcome(column_name, game_outcome):
    """
    Returns a list that contains values only from games that had the chosen outcome.

    :param column_name: (str)
    :param game_outcome: (str) 'w', 'l' for win or loss.
    :return: (list)
    """

    lst_returned = []

    num_of_games_stored = len(df)
    # Checks each game.
    for game_num in range(num_of_games_stored):

        if df['outcome'][game_num] == game_outcome:
            lst_returned.append(df[column_name][game_num])

    return lst_returned


# Fitting data with 1st degree polynomial
def plot_points_and_fit(column_name, game_outcome):

    x_vals = columns_of_specific_outcome(column_name='game-time', game_outcome=game_outcome)
    y_vals = columns_of_specific_outcome(column_name=column_name, game_outcome=game_outcome)

    # PRINTS
    print('Game outcome: {}'.format(game_outcome))
    a, b, *_ = pylab.polyfit(x_vals, y_vals, 1)
    print('a: {}\nb: {}\n'.format(a, b))

    # Point plot
    plt.scatter(x_vals, y_vals)

    # Fit plot
    x_vals_of_fit = [i/10 for i in range(100, 600)]
    y_vals_of_fit = [a*i+b for i in x_vals_of_fit]
    plt.plot(x_vals_of_fit, y_vals_of_fit)
    plt.title(column_name)

    return a, b

stat_tracked = 'total-xp'
print('\n{}\n'.format(stat_tracked))
win_a, win_b = plot_points_and_fit(column_name=stat_tracked, game_outcome='w')
loss_a, loss_b = plot_points_and_fit(column_name=stat_tracked, game_outcome='l')


def average_xp_per_minute(average_game_duration, win_ratio, coef):
    win_xp = average_game_duration * win_a + win_b
    loss_xp = average_game_duration * loss_a + loss_b

    average = win_xp * win_ratio + loss_xp * (1-win_ratio)

    return average * coef / average_game_duration


normal_average_xp_per_minute = average_xp_per_minute(average_game_duration=35, win_ratio=0.60, coef=1)
coop_average_xp_per_minute = average_xp_per_minute(average_game_duration=25, win_ratio=0.98, coef=0.75)


print('Average xp/minute normal: {:.3g}'.format(normal_average_xp_per_minute))
print('Average xp/minute Coop vs AI: {:.3g}\n'.format(coop_average_xp_per_minute))

print('normal/coop: {:.0%}'.format(normal_average_xp_per_minute/coop_average_xp_per_minute-1))


plt.show()