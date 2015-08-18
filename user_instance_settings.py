import importlib


class UserSession(object):

    def __init__(self):

        self.instances_results = {}

    @staticmethod
    def combiner_class(input_dct):

        player_champ_name = input_dct['selected_champions_dct']['player']
        # TODO: Import all champions at top of module?
        player_champ_module = importlib.import_module('champions.'+player_champ_name)
        player_champ_tot_attr_class = getattr(player_champ_module, 'ChampionAttributes')

        return player_champ_tot_attr_class(input_dct)

    def single_reverted_enemy_stats_and_buffs(self, input_dct, enemy_name):
        """
        Calculates enemy's stats and enemy generated buffs to be applied to player,
        by creating an instance with given enemy being converted to 'player'.

        :return: (dict) Contains buffs that should be applied to the player and enemy's total stats.
        """

        new_input_dct = {}

        enemy_champion = input_dct['selected_champions_dct'][enemy_name]
        new_input_dct.update({'selected_champions_dct': {'player': enemy_champion, 'enemy_1': 'jax'}})

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

        return instance.reversed_precombat_player_stats_and_enemy_buffs

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


