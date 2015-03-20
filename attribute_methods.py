import dmgs_buffs_categories
import copy


class ChampionAttributeBase(dmgs_buffs_categories.DmgCategories):

    def __init__(self,
                 current_target,
                 act_buffs,
                 ability_lvls_dct,
                 req_stats_func,
                 current_stats,
                 champion_lvls_dct,
                 current_target_num,):

        self.current_target = current_target
        self.act_buffs = act_buffs
        self.ability_lvls_dct = ability_lvls_dct
        self.request_stat = req_stats_func
        self.current_stats = current_stats
        self.champion_lvls_dct = champion_lvls_dct
        self.current_target_num = current_target_num

        dmgs_buffs_categories.DmgCategories.__init__(self,
                                                     req_stats_func=req_stats_func,
                                                     current_stats=current_stats,
                                                     current_target=current_target,
                                                     champion_lvls_dct=champion_lvls_dct,
                                                     current_target_num=current_target_num,
                                                     active_buffs=act_buffs)

    def _x_value(self, x_name, x_type, x_owner):
        """
        Determines value of x in a condition trigger.

        Returns:
            (num)
        """

        if x_owner == 'player':
            owner = x_owner
        else:
            owner = self.current_target

        # BUFF STACKS VALUE
        if x_type == 'buff':
            # If buff is active, returns stacks.
            if x_name in self.act_buffs[owner]:
                return self.act_buffs[owner][x_name]['current_stacks']
            # Otherwise returns 0.
            else:
                return 0

        # STAT VALUE
        elif x_type == 'stat':
            return self.request_stat(target_name=x_owner, stat_name=x_name)

        # ABILITY LVL
        elif x_type == 'ability_lvl':
            return self.ability_lvls_dct[x_name]

    def _formula_to_value(self, formula, x_name, x_type, x_owner, formula_type):
        """
        Converts condition trigger formula to value.

        Returns:
            (str)
            (bool)
            (num)
            (sequence)
            (None)
        """

        if formula_type == 'constant_value':
            return eval(formula)

        else:
            x = self._x_value(x_name, x_type, x_owner)
            return eval(formula)

    ABILITIES_EFFECTS = {
    'e': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': [],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}},
    'q': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': [],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}},
    'r': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': ['r_dmg_red'],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': ['r_n_hit_initiator'],
                                  'dmg': [],
                                  'remove_buff': []}}},
    'w': {'enemy': {'actives': {'buffs': [], 'dmg': [], 'remove_buff': []},
                    'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}},
          'player': {'actives': {'buffs': [],
                                 'cds_modified': {},
                                 'dmg': [],
                                 'remove_buff': []},
                     'passives': {'buffs': [], 'dmg': [], 'remove_buff': []}}}
}

    ABILITIES_CONDITIONS = {
    'q_apply_w_conditional': {'effects': {'apply_w_dmg': {'ability_name': 'q',
                                                          'category': 'dmg',
                                                          'effect_type': 'ability_effect',
                                                          'modification_type': 'append',
                                                          'names_lst': ['w_dmg_0'],
                                                          'tar_type': 'enemy'},
                                          'remove_w_buff': {'ability_name': 'q',
                                                            'category': 'remove_buff',
                                                            'effect_type': 'ability_effect',
                                                            'modification_type': 'append',
                                                            'names_lst': ['w_buff_0'],
                                                            'tar_type': 'player'}},
                              'triggers': {}},
    'r_nth_hit': {'effects': {'apply_r_dmg': {'buff_name': 'r_n_hit_initiator',
                                              'category': 'apply_dmg',
                                              'effect_type': 'buff_on_hit',
                                              'modification_type': 'append',
                                              'names_lst': ['r_dmg_0']},
                              'remove_r_counter_stacks': {'buff_name': 'r_n_hit_initiator',
                                                          'category': 'remove_buff',
                                                          'effect_type': 'buff_on_hit',
                                                          'modification_type': 'append',
                                                          'names_lst': ['r_hit_counter']}},
                  'triggers': {'nth_hit_trig': {'buff_name': 'r_hit_counter',
                                                'operator': '>=',
                                                'owner_type': 'player',
                                                'stacks': 2,
                                                'trigger_type': 'buff'}}}}

    def abilities_effects(self, ability_name):
        """
        Checks if ability effects are affected by any conditionals.
        If not, returns member variable dict. Otherwise returns different version of the dict.

        Returns:
            (dict)
        """

        new_dct = {}
        # Checks if given ability name has conditions affecting its effects.
        for cond in self.ABILITIES_CONDITIONS:
            for eff in self.ABILITIES_CONDITIONS[cond]['effects']:

                eff_dct = self.ABILITIES_CONDITIONS[cond]['effects'][eff]
                if ability_name == eff_dct['ability_name']:

                    if eff_dct['effect_type'] == 'ability_effect':

                        # Then checks if a new dct has been created.
                        if not new_dct:
                            new_dct = copy.deepcopy(self.ABILITIES_EFFECTS[ability_name])

                        # DATA MODIFICATION
                        tar_type = eff_dct['tar_type']
                        mod_type = eff_dct['modification_type']
                        cat_type = eff_dct['category']
                        eff_contents = eff_dct['names_lst']

                        # (it always modifies actives)

                        if mod_type == 'append':
                            new_dct[ability_name][tar_type]['actives'][cat_type] += eff_contents
                        else:
                            new_dct[ability_name][tar_type]['actives'][cat_type] = eff_contents

        if new_dct:
            return new_dct
        else:
            return self.ABILITIES_EFFECTS






child_class_as_str = """class ChampionAttributes(attribute_methods.ChampionAttributeBase):
    def __init__(self, kwargs, external_vars_dct=CHAMPION_EXTERNAL_VARIABLES):
        for i in external_vars_dct:
            setattr(ChampionAttributes, i, external_vars_dct[i])
        super().__init__(**kwargs)"""