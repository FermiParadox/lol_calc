# Ori

import champions.app_champions_base_stats as champ_stats_module
import pandas


# -----------------------------------------------------------------------------------
def round_closer_to_0(n):
    """
    Rounds values down when there is a tie.

    :return: (int)
    """

    decimals = n - int(n)
    # If 0 it's an int
    if not decimals:
        return n

    first_decimal_digit = int(decimals*10)

    if first_decimal_digit:
        None



def final_stat(base_stat, growth_stat, lvl):

    val = base_stat + growth_stat * (7/400*(lvl**2-1) + 267/400*(lvl-1))

    return val



# -----------------------------------------------------------------------------------

displayed_ad_lst = [40, 42, 44, 46, 48, 51,53,55,58,60,63,66,69,72,75,78,81,85]
inflicted_aa_lst = ['','','','','',50,52,'',57,'','',65,68,71,74,'','',84]
inflicted_aa_lst = [i if i!='' else 'same' for i in inflicted_aa_lst]



ori_stats = champ_stats_module.CHAMPION_BASE_STATS['orianna']
ori_ad_lvl_1 = ori_stats['ad']
ori_ad_per_lvl = ori_stats['ad_per_lvl']
ori_ad_per_lvl = ori_ad_per_lvl

calced = []

for i in range(1, 19):
    val = final_stat(base_stat=ori_ad_lvl_1, growth_stat=ori_ad_per_lvl, lvl=i)
    calced.append(val)



rounded = [round(i) for i in calced]
delta = [calced[i]-rounded[i] for i in range(0, 18)]
data_dct = {"exact AD": calced, 'rounded AD': rounded, 'delta': delta, 'AA dmg': inflicted_aa_lst}

df = pandas.DataFrame(data_dct, columns=['exact AD', 'rounded AD', 'delta', 'AA dmg'], index=range(1,19))

print(df)

ori_expected_ad_lst = []
for i in range(0, 18):
    per_lvl_val = ori_ad_per_lvl*i

    ad_val = ori_ad_lvl_1 + per_lvl_val
    ad_val = ad_val
    ori_expected_ad_lst.append(ad_val)

for i in range(0, 18):
    expected = round(calced[i], 4)
    displayed = displayed_ad_lst[i]
    delta = round(expected-displayed, 3)

    print(i+1, expected, displayed, delta, inflicted_aa_lst[i])

