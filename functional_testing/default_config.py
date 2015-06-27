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

    combat_instance = user_instance.instance_after_combat(data_dct)
    combat_instance.run_combat()

    return combat_instance


def __test_time(repetitions):
    """
    Creates a user instance and then lots of combat instances so that module and class variables are reused.

    :param repetitions: (int)
    :return: (None)
    """
    user_instance = user_instance_settings.UserSession(test_and_display_mode=True)

    combat_instance = user_instance.instance_after_combat(ALL_DATA)
    combat_instance.run_combat()

    for i in range(repetitions - 1):
        temp_inst = user_instance.instance_after_combat(ALL_DATA)
        temp_inst.run_combat()


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

    def run_combat_and_represent_results(self, data_dct=None):

        data_dct = self.__data_dct(given_dct=data_dct)

        user_instance = user_instance_settings.UserSession(test_and_display_mode=True)
        combat_instance = user_instance.create_instance_and_represent_results(input_dct=data_dct)

        return combat_instance

    def naked_lvl_1(self, rotation):

        data_dct = self.__data_dct(given_dct=rotation)

        instance = self.run_combat_and_represent_results(data_dct=data_dct)
        print(instance.selected_runes)


if 0:
    dct = all_data_deepcopy()
    inst = TestCases().run_combat_and_represent_results(data_dct=dct)

# TIME
if 1:
    test_time(100)


# dps: 333.7, 2463 movement, 2.9sec / 100 rotations (masteries used)
