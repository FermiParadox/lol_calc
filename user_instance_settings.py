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
            main_loop_class = abilities.Presets

        class CombinerClass(player_champ_tot_attr_class, main_loop_class):

            def __init__(self,
                         rotation_lst,
                         max_targets_dct,
                         selected_champions_dct,
                         champion_lvls_dct,
                         ability_lvls_dct,
                         max_combat_time,
                         selected_masteries_dct,
                         items_lst,
                         selected_summoner_spells,
                         initial_enemies_total_stats=None,
                         initial_active_buffs=None,
                         initial_current_stats=None,
                         selected_runes=None):

                main_loop_class.__init__(self,
                                         rotation_lst=rotation_lst,
                                         max_targets_dct=max_targets_dct,
                                         selected_champions_dct=selected_champions_dct,
                                         champion_lvls_dct=champion_lvls_dct,
                                         ability_lvls_dct=ability_lvls_dct,
                                         max_combat_time=max_combat_time,
                                         selected_summoner_spells=selected_summoner_spells,
                                         initial_active_buffs=initial_active_buffs,
                                         initial_current_stats=initial_current_stats,
                                         chosen_items_lst=items_lst,
                                         selected_runes=selected_runes,
                                         selected_masteries_dct=selected_masteries_dct,
                                         initial_enemies_total_stats=initial_enemies_total_stats)

                player_champ_tot_attr_class.__init__(self,)

        return CombinerClass(**input_dct)

    def single_reverted_enemy_stats_and_buffs(self, input_dct, enemy_name):
        """
        Calculates enemy's stats and enemy generated buffs to be applied to player,
        by creating an instance with given enemy being converted to 'player'.

        :return: (dict) Contains buffs that should be applied to the player and enemy's total stats.
        """

        new_input_dct = {}

        enemy_champion = input_dct['selected_champions_dct'][enemy_name]
        new_input_dct.update({'selected_champions_dct': {'player': enemy_champion, 'enemy_1': 'jax'}})

        enemy_lvl = input_dct['champion_lvls_dct'][enemy_name]
        new_input_dct.update({'champion_lvls_dct': {'player': enemy_lvl, 'enemy_1': 1}})

        for key in input_dct:
            if key not in new_input_dct:
                value = input_dct[key]
                new_input_dct.update({key: value})

        instance = self.combiner_class(new_input_dct)

        return instance.reversed_precombat_player_stats_and_enemy_buffs()

    def all_enemy_stats_and_final_player_buffs(self, input_dct):
        """
        Combines all enemy induced buffs on player into a single dict,
        and creates enemies' base stats dict.

        :return: (dict)
        """

        player_buffs = {}
        enemies_base_stats = {}

        enemy_target_names = tuple(tar for tar in sorted(input_dct['selected_champions_dct']) if tar != 'player')

        for enemy_name in enemy_target_names:

            stats_and_buffs_dct = self.single_reverted_enemy_stats_and_buffs(input_dct=input_dct, enemy_name=enemy_name)
            stats_dct = stats_and_buffs_dct['stats']
            buffs_dct = stats_and_buffs_dct['buffs']

            enemies_base_stats.update({enemy_name: stats_dct})
            player_buffs.update(buffs_dct)

        return {'all_stats': enemies_base_stats, 'all_player_buffs': player_buffs}

    def finalized_input_dct(self, input_dct):
        """
        Creates final input dict for the player's combat instance, by inserting buffs and stats originating from enemy.

        :return: (dict)
        """

        dct = {}

        stats_and_buffs_dct = self.all_enemy_stats_and_final_player_buffs(input_dct=input_dct)
        enemies_stats_dct = stats_and_buffs_dct['all_stats']
        player_buffs_dct = stats_and_buffs_dct['all_player_buffs']

        dct.update({'initial_active_buffs': {'player': player_buffs_dct}})

        dct.update({'initial_enemies_total_stats': enemies_stats_dct})

        for key in input_dct:
            if key not in dct:
                value = input_dct[key]

                dct.update({key: value})

        return dct

    def instance_after_combat(self, input_dct):
        """
        Returns instance after running combat.

        :param input_dct:
        :return:
        """

        input_dct = self.finalized_input_dct(input_dct=input_dct)

        instance = self.combiner_class(input_dct)
        instance.run_combat()

        return instance

    def create_instance_and_represent_results(self, input_dct):

        input_dct = self.finalized_input_dct(input_dct=input_dct)

        instance = self.instance_after_combat(input_dct=input_dct)
        instance.represent_results_visually()

        return instance


