import importlib
import os

import palette


# All available champion modules are stored.
ALL_CHAMPIONS_TOTAL_ATTRIBUTES_CLASSES = {}
for champ_name in palette.ALL_CHAMPIONS_NAMES:
    champ_name = champ_name.lower()

    # Filters out non implemented champions
    if champ_name + '.py' in os.listdir('/home/black/Dev/PycharmProjects/WhiteProject/champions'):
        player_champ_module = importlib.import_module('champions.' + champ_name)
        player_champ_tot_attr_class = getattr(player_champ_module, 'ChampionAttributes')

        ALL_CHAMPIONS_TOTAL_ATTRIBUTES_CLASSES.update({champ_name: player_champ_tot_attr_class})


class UserSession(object):

    @staticmethod
    def combiner_class(input_dct):

        player_champ_name = input_dct['selected_champions_dct']['player']

        return ALL_CHAMPIONS_TOTAL_ATTRIBUTES_CLASSES[player_champ_name](input_dct)

    def reversed_combat_instance(self, input_dct, enemy_name):
        new_input_dct = {}

        enemy_champion = input_dct['selected_champions_dct'][enemy_name]
        player_champion = input_dct['selected_champions_dct']['player']
        new_input_dct.update({'selected_champions_dct': {'player': enemy_champion, 'enemy_1': player_champion}})

        player_lvl = input_dct['champion_lvls_dct']['player']
        enemy_lvl = input_dct['champion_lvls_dct'][enemy_name]
        new_input_dct.update({'champion_lvls_dct': {'player': enemy_lvl, 'enemy_1': player_lvl}})

        chosen_items_dct = input_dct['chosen_items_dct']
        if enemy_name in chosen_items_dct:
            enemy_items = chosen_items_dct[enemy_name]
        else:
            enemy_items = []
        new_input_dct.update({'chosen_items_dct': {'player': enemy_items, }})

        new_input_dct.update({'_reversed_combat_mode': True})

        for key in input_dct:
            if key not in new_input_dct:
                value = input_dct[key]
                new_input_dct.update({key: value})

        instance = self.combiner_class(new_input_dct)
        instance.run_combat()

        return instance

    def all_enemy_stats(self, input_dct):
        """
        Combines all enemy induced dmg, and enemies' stats on player into a single dict.

        :return: (dict)
        """
        enemies_base_stats = {}
        dmg_data = {}

        enemy_target_names = tuple(tar for tar in sorted(input_dct['selected_champions_dct']) if tar != 'player')

        for enemy_name in enemy_target_names:
            instance = self.reversed_combat_instance(input_dct=input_dct, enemy_name=enemy_name)

            # Stats
            stats_dct = instance.reversed_precombat_player_stats
            enemies_base_stats.update({enemy_name: stats_dct})

            # Dmg
            enemy_dmg_results = instance.combat_results
            dmg_data.update({enemy_name: enemy_dmg_results})

        return {'all_stats': enemies_base_stats, 'all_dmg_results': dmg_data}

    def finalized_input_dct(self, input_dct):
        """
        Creates final input dict for the player's combat instance, by inserting buffs and stats originating from enemy.

        :return: (dict)
        """

        dct = {}

        stats_and_buffs_dct = self.all_enemy_stats(input_dct=input_dct)
        enemies_stats_dct = stats_and_buffs_dct['all_stats']
        dmg_data_dct = stats_and_buffs_dct['all_dmg_results']

        dct.update({'initial_enemies_total_stats': enemies_stats_dct})
        dct.update({'enemies_originating_dmg_data': dmg_data_dct})

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

        instance = self.instance_after_combat(input_dct=input_dct)
        instance.represent_results_visually()

        return instance

    def create_instance_and_return_image_name(self, input_dct):
        instance = self.instance_after_combat(input_dct=input_dct)
        instance.store_results_as_image()

        return instance.temp_combat_results_image_name
