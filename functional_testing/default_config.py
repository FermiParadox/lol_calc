import user_instance_settings

import cProfile
import pstats
import copy


ALL_DATA = dict(

    selected_champions_dct=dict(
        player='jax',
        enemy_1='jax',
        enemy_2='jax',
        enemy_3='jax'),

    champion_lvls_dct=dict(
        player=18,
        enemy_1=18,
        enemy_2=17,
        enemy_3=16
    ),

    ability_lvls_dct=dict(
        q=5,
        w=5,
        e=5,
        r=3),

    max_targets_dct={},

    max_combat_time=10,

    rotation_lst=['e', 'r', 'q', 'AA', 'w', 'AA', 'AA', 'hextech_gunblade', 'AA', 'AA', 'AA', 'AA', 'AA', 'w', 'AA',
                  'AA', 'AA', 'AA', 'w', 'AA', 'q'],
    items_lst=['hextech_gunblade', 'hextech_gunblade'],

    selected_runes=dict(
        red=dict(
            ad_per_lvl=dict(
                additive=6))),

    selected_masteries_dct=dict(archmage=3))


def all_data_deepcopy():
    return copy.deepcopy(ALL_DATA)


def _combat_loop_instance(data_dct):
    """
    Creates a combat loop instance and returns it after the combat.

    :return:
    """
    user_instance = user_instance_settings.UserSession(test_and_display_mode=True)

    combat_instance = user_instance.combat_class(data_dct)
    combat_instance.combat_loop()

    return combat_instance


def __test_time(repetitions):
    """
    Creates a user instance and then lots of combat instances so that module and class variables are reused.

    :param repetitions: (int)
    :return: (None)
    """
    user_instance = user_instance_settings.UserSession(test_and_display_mode=True)

    combat_instance = user_instance.combat_class(all_data_deepcopy())
    combat_instance.combat_loop()

    for i in range(repetitions - 1):
        temp_inst = user_instance.combat_class(all_data_deepcopy())
        temp_inst.combat_loop()


def test_time(repetitions):

    executed_str = '__test_time({})'.format(repetitions)

    cProfile.run(executed_str, 'cprof_results', sort='cumtime')

    results_run = pstats.Stats('cprof_results').sort_stats('cumtime')
    results_run.strip_dirs().sort_stats('cumtime').print_stats(5)
    # print(results_run.strip_dirs().sort_stats('cumtime').stats)





if 1:
    pass


# TIME
if 1:
    test_time(100)
