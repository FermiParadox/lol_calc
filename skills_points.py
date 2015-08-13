import palette


class SkillsLvlUp(object):

    DEFAULT_MAX_SPELL_POINTS = dict(
        r=3,
        q=5,
        w=5,
        e=5)

    TOTAL_SKILLS_POINTS = 18
    MAX_CHAMPION_LVL = TOTAL_SKILLS_POINTS

    def __init__(self, skill_lvl_up_data_dct):
        self.priorities_seq = skill_lvl_up_data_dct['spells_lvl_up_queue']
        self.all_at_least_one_point_on_each = skill_lvl_up_data_dct['at_least_one_lvl_in_each']
        self.max_spells_lvls = skill_lvl_up_data_dct['max_spells_lvl_ups']
        self.automatically_lvled_up = skill_lvl_up_data_dct['automatically_lvled_up']

    def _allowed_points_of_spell(self, spell_name, max_spells_lvls, champ_lvl):
        """
        Returns the maximum points that can be spent on given spell, based on current champion lvl.

        :return: (int)


        >>> l_1 = [1, 5, 6, 10, 11, 12, 15, 16, 17, 18]
        >>> [SkillsLvlUp()._allowed_points_of_spell('r', 'standard', i) for i in l_1]
        [0, 0, 1, 1, 2, 2, 2, 3, 3, 3]

        >>> l_2 = [1, 2, 3, 8, 9, 10, 11, 18]
        >>> [SkillsLvlUp()._allowed_points_of_spell('w', 'standard', i) for i in l_2]
        [1, 1, 2, 4, 5, 5, 5, 5]
        """

        if max_spells_lvls != 'standard':
            max_points_allowed_by_spell = max_spells_lvls[spell_name]
        else:
            max_points_allowed_by_spell = self.DEFAULT_MAX_SPELL_POINTS[spell_name]

        if spell_name == 'r':
            max_allowed_by_champ_lvl = ((champ_lvl-1) // 5)

        else:
            max_allowed_by_champ_lvl = (champ_lvl + 1) // 2

        return min(max_points_allowed_by_spell, max_allowed_by_champ_lvl)

    def _skill_lvling_order_queue(self):
        """
        Returns a tuple of spell names in lvling up order.

        NOTE: Automatically lvled up spells aren't included.

        :return: (tuple)
        """

        lvl_up_queue = []
        total_spent_points = 0

        if self.all_at_least_one_point_on_each:
            # Adds 1 point in all non ultimate spells.
            for spell in self.priorities_seq:
                if spell != 'r':
                    lvl_up_queue.append(spell)
                    total_spent_points += 1

        while total_spent_points < self.TOTAL_SKILLS_POINTS:
            # Tries adding points to spells from highest to lowest priority.
            for spell_name in self.priorities_seq:

                allowed_points = self._allowed_points_of_spell(spell_name=spell_name,
                                                               max_spells_lvls=self.max_spells_lvls,
                                                               champ_lvl=total_spent_points+1)

                _spent_points = lvl_up_queue.count(spell_name)

                if _spent_points < allowed_points:
                    lvl_up_queue.append(spell_name)
                    total_spent_points += 1
                    break

        return tuple(lvl_up_queue)

    def skills_points_on_all_lvls(self):
        """
        Returns points on each ability for every champion lvl.

        :return: (dict)
        """

        dct = {}

        skill_lvling_queue = self._skill_lvling_order_queue()

        for champ_lvl in range(1, self.MAX_CHAMPION_LVL+1):
            dct.update({champ_lvl: {}})
            queue_slice = skill_lvling_queue[:champ_lvl]

            for spell_name in palette.SPELL_SHORTCUTS:
                # Normal spell points.
                spell_points = queue_slice.count(spell_name)

                # Automatically assigned points.
                if self.automatically_lvled_up:
                    if spell_name in self.automatically_lvled_up:
                        # Adds 1 point for each champ lvl (up to current champ lvl) at which the ability is lvled up.
                        for champ_lvl_spell_lvled_up in self.automatically_lvled_up[spell_name]:
                            if champ_lvl_spell_lvled_up <= champ_lvl:
                                spell_points += 1

                dct[champ_lvl].update({spell_name: spell_points})

        return dct
