import user_instance_settings
import functional_testing.default_config as default_config

import cProfile
import pstats
import pandas


def _combat_loop_instance(data_dct):
    """
    Creates a combat loop instance and returns it after the combat.

    :return:
    """
    user_instance = user_instance_settings.UserSession(test_and_display_mode=True)

    combat_instance = user_instance.instance_after_combat(data_dct)

    return combat_instance


def _multiple_combat_instances_lst(repetitions):
    """
    Creates a user instance and then lots of combat instances so that module and class variables are reused.

    :param repetitions: (int)
    :return: (list) List of instances.
    """

    combat_instances_lst = []

    user_instance = user_instance_settings.UserSession(test_and_display_mode=False)

    for i in range(repetitions):
        combat_instances_lst.append(user_instance.instance_after_combat(default_config.ALL_DATA))

    return combat_instances_lst


def test_run_duration(repetitions):

    executed_str = '_multiple_user_instances_lst({})'.format(repetitions)

    cProfile.run(executed_str, 'cprof_results', sort='cumtime')

    results_run = pstats.Stats('cprof_results').sort_stats('cumtime')
    results_run.strip_dirs().sort_stats('cumtime').print_stats(5)
    # print(results_run.strip_dirs().sort_stats('cumtime').stats)


class TestCases(object):

    @property
    def __data_deepcopy(self):
        return default_config.all_data_deepcopy()

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

    def run_combat_and_show_results(self, data_dct=None):

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

        post_combat_instance = self.run_combat_and_show_results(data_dct=data_dct)

        return post_combat_instance

    def combats_consistency_test(self, repetitions):
        """
        Runs multiple combat tests for a single user instance.

        :param repetitions:
        :return:
        """

        combat_instances_lst = _multiple_combat_instances_lst(repetitions=repetitions)

        enumerated_histories_dct = {}

        first_combat_instance_data = combat_instances_lst[0].combat_results['player']['pre_combat_stats']
        different_histories_dct = {0: first_combat_instance_data}

        for num, combat_instance in enumerate(combat_instances_lst):

            examined_history_dct = combat_instance.combat_results['player']['pre_combat_stats']
            enumerated_histories_dct.update({num: examined_history_dct})

            # Checks if history is different that existing histories.
            for stored_history in different_histories_dct.values():

                if stored_history == examined_history_dct:
                    break

            # If loop hasn't found a match.
            else:
                different_histories_dct.update({num: examined_history_dct})

        total_different_histories = len(different_histories_dct)

        print(total_different_histories)

    @staticmethod
    def compared_tar_pre_combat_stats(combat_instances_lst, tar_name):
        """
        Prints only stats that differ in instances.

        :param combat_instances_lst: (list)
        :return: (DataFrame)
        """

        all_stats_names = set()

        # Inserts all possible stats in dict, since some instances might not have that stat.
        for combat_instance in combat_instances_lst:
            combat_results_dct = combat_instance.combat_results
            tar_pre_combat_stats_dct = combat_results_dct[tar_name]['pre_combat_stats']

            all_stats_names |= set(tar_pre_combat_stats_dct.keys())

        diff_pre_combat_stats = {i: [] for i in all_stats_names}

        # Inserts stats' values for each instance.
        # Instances without the stat are stored as NaN.
        for combat_instance in combat_instances_lst:
            combat_results_dct = combat_instance.combat_results

            tar_pre_combat_stats_dct = combat_results_dct[tar_name]['pre_combat_stats']

            for stat_name in diff_pre_combat_stats:
                if stat_name in tar_pre_combat_stats_dct:
                    diff_pre_combat_stats[stat_name].append(tar_pre_combat_stats_dct[stat_name])
                else:
                    diff_pre_combat_stats[stat_name].append(None)

        # Filters out stats that remain the same.
        for stat_name in sorted(diff_pre_combat_stats):
            stat_vals_lst = diff_pre_combat_stats[stat_name]
            first_val = stat_vals_lst[0]

            for stat_val in stat_vals_lst:
                if stat_val != first_val:
                    break
            # (If loop doesn't break, then all values are equal and there is not point in displaying them.)
            else:
                del diff_pre_combat_stats[stat_name]

        return pandas.DataFrame(diff_pre_combat_stats).transpose()

    @staticmethod
    def compared_tar_pre_combat_bonuses(combat_instances_lst, tar_name):
        None

if __name__ == '__main__':
    if 0:
        inst = TestCases().run_combat_and_show_results()

    if 0:
        inst = TestCases().naked_combat_and_results(rotation_lst=['AA'], all_champs_lvls=1)

    # RUN DURATION
    if 0:
        test_run_duration(100)

    if 1:
        inst_lst = _multiple_combat_instances_lst(repetitions=7)
        df = TestCases().compared_tar_pre_combat_stats(combat_instances_lst=inst_lst, tar_name='player')
        print(df)

    # dps: 333.7, 2463 movement, 2.2sec / 100 rotations (masteries used)
    # dps: 336.3, dmg: 3132, 2464 movement, 2.2sec / 100 rotations (rounding changed)
    # dps: 336.3, dmg: 3132, 2464 movement, 2.4sec / 100 rotations (death application doesnt remove other buffs)

