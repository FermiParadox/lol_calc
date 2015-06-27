import abilities

import importlib


class UserSession(object):

    def __init__(self,
                 test_and_display_mode=False):

        self.test_and_display_mode = test_and_display_mode
        self.instances_results = {}

    def combiner_class(self, input_dct):

        player_champ_name = input_dct['selected_champions_dct']['player']
        player_champ_module = importlib.import_module('champions.'+player_champ_name)
        player_champ_tot_attr_class = getattr(player_champ_module, 'ChampionAttributes')

        # Checks if class is used for testing purposes.
        if self.test_and_display_mode:
            main_loop_class = abilities.VisualRepresentation
        else:
            main_loop_class = abilities.Actions

        class CombinerClass(player_champ_tot_attr_class, main_loop_class):

            def __init__(self,
                         rotation_lst,
                         max_targets_dct,
                         selected_champions_dct,
                         champion_lvls_dct,
                         ability_lvls_dct,
                         max_combat_time,
                         selected_masteries_dct,
                         initial_active_buffs=None,
                         initial_current_stats=None,
                         items_lst=None,
                         selected_runes=None):

                main_loop_class.__init__(self,
                                         rotation_lst=rotation_lst,
                                         max_targets_dct=max_targets_dct,
                                         selected_champions_dct=selected_champions_dct,
                                         champion_lvls_dct=champion_lvls_dct,
                                         ability_lvls_dct=ability_lvls_dct,
                                         max_combat_time=max_combat_time,
                                         initial_active_buffs=initial_active_buffs,
                                         initial_current_stats=initial_current_stats,
                                         chosen_items_lst=items_lst,
                                         selected_runes=selected_runes,
                                         selected_masteries_dct=selected_masteries_dct)

                player_champ_tot_attr_class.__init__(self,)

        return CombinerClass(**input_dct)

    def instance_after_combat(self, input_dct):
        """
        Returns instance after running combat.

        :param input_dct:
        :return:
        """
        instance = self.combiner_class(input_dct)
        instance.run_combat()

        return instance

    def create_instance_and_represent_results(self, input_dct):
        instance = self.instance_after_combat(input_dct=input_dct)
        instance.represent_results_visually()

        return instance


