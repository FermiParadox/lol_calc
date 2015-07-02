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

    rotation_lst=None,
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

    combat_instance = user_instance.instance_after_combat(data_dct)

    return combat_instance


def __test_time(repetitions):
    """
    Creates a user instance and then lots of combat instances so that module and class variables are reused.

    :param repetitions: (int)
    :return: (None)
    """
    lst = []

    user_instance = user_instance_settings.UserSession(test_and_display_mode=False)

    for i in range(repetitions):
        lst.append(user_instance.instance_after_combat(ALL_DATA))


def test_time(repetitions):

    executed_str = '__test_time({})'.format(repetitions)

    cProfile.run(executed_str, 'cprof_results', sort='cumtime')

    results_run = pstats.Stats('cprof_results').sort_stats('cumtime')
    results_run.strip_dirs().sort_stats('cumtime').print_stats(5)
    # print(results_run.strip_dirs().sort_stats('cumtime').stats)


class TestCases(object):

    @property
    def __data_deepcopy(self):
        return all_data_deepcopy()

    def __data_dct(self, given_dct):
        """
        Returns given dict or sets it equal to deepcopy if None.

        :param given_dct: (dict) (None)
        :return: (dict) Dict with initial combat instance setup.
        """
        if given_dct:
            pass
        else:
            given_dct = self.__data_deepcopy

        return given_dct

    @staticmethod
    def __set_all_initial_lvls_to(initial_lvls_val, given_data_dct):
        """
        Modifies given dict by setting all lvls to chosen value.

        :param initial_lvls_val: (int) 1-18
        :param given_data_dct:
        :return: (None)
        """

        for i in given_data_dct['champion_lvls_dct']:
            given_data_dct['champion_lvls_dct'][i] = initial_lvls_val

    def run_combat_and_represent_results(self, data_dct=None):

        data_dct = self.__data_dct(given_dct=data_dct)

        user_instance = user_instance_settings.UserSession(test_and_display_mode=True)
        post_combat_instance = user_instance.create_instance_and_represent_results(input_dct=data_dct)

        return post_combat_instance

    def naked_combat_and_results(self, rotation_lst, all_champs_lvls):

        data_dct = self.__data_deepcopy
        data_dct['rotation_lst'] = rotation_lst
        data_dct['selected_runes'] = None
        data_dct['selected_masteries_dct'] = None
        data_dct['items_lst'] = None
        self.__set_all_initial_lvls_to(initial_lvls_val=all_champs_lvls, given_data_dct=data_dct)

        post_combat_instance = self.run_combat_and_represent_results(data_dct=data_dct)

        return post_combat_instance


if 1:
    dct = all_data_deepcopy()
    inst = TestCases().run_combat_and_represent_results(data_dct=dct)

if 0:
    TestCases().naked_combat_and_results(rotation_lst=['AA'], all_champs_lvls=1)

# TIME
if 1:
    test_time(100)


# dps: 333.7, 2463 movement, 2.2sec / 100 rotations (masteries used)
# dps: 336.3, dmg: 3132, 2464 movement, 2.2sec / 100 rotations (rounding changed)
# dps: 336.3, dmg: 3132, 2464 movement, 2.4sec / 100 rotations (death application doesnt remove other buffs)
