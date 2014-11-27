import abilities


class UserSession(object):

    def __init__(self, input_dct):
        self.input_dct = input_dct
        self.instances_results = {}

    def combat_instance(self):

        player_champ_name = self.input_dct['selected_champions_dct']['player']
        player_champ_module = __import__(player_champ_name)
        player_champ_class = getattr(player_champ_module, 'TotalChampionAttributes')

        class CombinerClass(player_champ_class, abilities.VisualRepresentation):

            def __init__(self,
                         rotation_lst,
                         max_targets_dct,
                         selected_champions_dct,
                         champion_lvls_dct,
                         ability_lvls_dct,
                         max_combat_time,
                         initial_active_buffs=None,
                         initial_current_stats=None,
                         items_lst=None,
                         selected_runes=None):

                abilities.VisualRepresentation.__init__(self,
                                                        rotation_lst=rotation_lst,
                                                        max_targets_dct=max_targets_dct,
                                                        selected_champions_dct=selected_champions_dct,
                                                        champion_lvls_dct=champion_lvls_dct,
                                                        ability_lvls_dct=ability_lvls_dct,
                                                        max_combat_time=max_combat_time,
                                                        initial_active_buffs=initial_active_buffs,
                                                        initial_current_stats=initial_current_stats,
                                                        items_lst=items_lst,
                                                        selected_runes=selected_runes)

                player_champ_module.TotalChampionAttributes.__init__(self,
                                                                     ability_lvls_dct=ability_lvls_dct,
                                                                     req_stats_func=self.request_stat,
                                                                     act_buffs=self.active_buffs,
                                                                     current_stats=self.current_stats,
                                                                     current_target=self.current_target,
                                                                     champion_lvls_dct=champion_lvls_dct,
                                                                     current_target_num=self.current_target_num)

        return CombinerClass(**self.input_dct)

