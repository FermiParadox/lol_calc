import unittest
import user_instance_settings


class Setups(unittest.TestCase):

    def setUp(self):

        self.selected_champions_dct = dict(
            player='jax',
            enemy_1='jax',
            enemy_2='jax',
            enemy_3='jax')

        self.rotation_lst = ['AA', 'w', 'AA', 'e', 'r']

        self.champion_lvls_dct = dict(
            player=1,
            enemy_1=1,
            enemy_2=1,
            enemy_3=1,
            enemy_4=1,
            enemy_5=1,)

        self.ability_lvls_dct = dict(
            q=1,
            w=1,
            e=1,
            r=1)

        self.max_targets_dct = dict(
        )

        self.items_lst = []

        self.kwargs = dict(
            rotation_lst=self.rotation_lst,
            max_targets_dct=self.max_targets_dct,
            selected_champions_dct=self.selected_champions_dct,
            champion_lvls_dct=self.champion_lvls_dct,
            ability_lvls_dct=self.ability_lvls_dct,
            max_combat_time=None,
            items_lst=self.items_lst,
            initial_active_buffs=None,
            initial_current_stats=None,
            selected_runes=None)

    def set_champ_instance(self):
        self.inst = user_instance_settings.UserInstance(self.kwargs).champion_instance()

    def set_ability_lvls(self, lvls_tpl=None, same_lvl=None):
        """
        Sets ability lvls to given tuple.

        Args:
            lvls_tpl: tpl containing lvls accordingly for q, w, e, r
            same_lvl: int lvl given to all abilities
        Returns:
            None
        Raises:
            BaseException: if both arguments are given at the same time.
        """

        # If accidental assignment of both arguments occurs, raises exception.
        if (lvls_tpl is None) or (same_lvl is None):
            pass
        else:
            raise BaseException('Only one arg can be given at a time.')

        # Assigns various lvls to each ability.
        if lvls_tpl:
            for ability_name, ability_lvl in self.kwargs['ability_lvls_dct'], lvls_tpl:
                self.kwargs['ability_lvls_dct'][ability_name] = lvls_tpl

        # Assigns same lvl to all abilities..
        else:
            for ability_name in self.kwargs['ability_lvls_dct']:
                self.kwargs['ability_lvls_dct'][ability_name] = same_lvl

    def set_champion_lvls(self, lvls_tpl=None, same_lvl=None):
        """
        Sets all champion lvls to given tuple.

        Args:
            lvls_tpl: Tpl containing lvls accordingly for q, w, e, r.
            same_lvl: Int lvl given to all champions.
        Returns:
            None
        Raises:
            BaseException: if both arguments are given at the same time.
        """

        # If accidental assignment of both arguments occurs, raises exception.
        if (lvls_tpl is None) or (same_lvl is None):
            pass
        else:
            raise BaseException('Only one arg can be given at a time.')

        # Assigns various lvls to each target.
        if lvls_tpl:
            for target_name, champion_lvl in self.kwargs['champion_lvls_dct'], lvls_tpl:
                self.kwargs['champion_lvls_dct'][target_name] = champion_lvl

        # Same lvl all targets.
        else:
            for target_name in self.kwargs['champion_lvls_dct']:
                self.kwargs['champion_lvls_dct'][target_name] = same_lvl


class GeneralTest(Setups):

    def _test_att_speed_increase_on_aa(self, last_aa=7):
        """
        Tests if attack speed is increased between consecutive AAs
        up to a limit defined by the last AA that increases att_speed.

        Args:
            last_aa: Int. Last AA which causes increase in AA.
        Returns:
            None
        """

        self.set_champ_instance()
        initial_att_speed = self.inst.request_stat(target_name='player', stat_name='att_speed')

        # Each time increases number of AA in rotation by one.
        aa_number = 1
        while aa_number < last_aa:
            self.setUp()

            # Sets rotation list equal to aa_number of AAs.
            self.kwargs['rotation_lst'] = ['AA' for num in range(aa_number)]

            self.set_champ_instance()
            self.inst.combat_loop()

            final_att_speed = self.inst.request_stat(target_name='player', stat_name='att_speed')

            self.assertGreater(final_att_speed, initial_att_speed)

            # Prepares next check.
            initial_att_speed = final_att_speed

            aa_number += 1

    def _test_player_stat_by_item(self):
        """
        Tests if player's stat increases as expected when equipping an item.

        An additive stat is chosen.
        """

        # WITH ITEM
        self.kwargs['items_lst'] = ['gunblade']
        self.set_champ_instance()
        self.inst.combat_loop()

        player_total_stat = self.inst.request_stat(target_name='player', stat_name='ad')

        # NO ITEM
        self.setUp()
        self.set_champ_instance()
        self.inst.combat_loop()

        stat_sum = self.inst.request_stat(target_name='player', stat_name='ad')
        stat_sum += self.inst.gunblade_stats_buff()['stats']['ad']['additive']

        self.assertEqual(player_total_stat, stat_sum,
                         "Item's stat plus player's base, not equal to player's total stat.")

    def _test_dps_increase_by_item(self, gunblade_count=1):
        """
        Tests if dps increases as expected when equipping an item.
        """
        # WITH ITEM
        for count_var in range(gunblade_count):
            self.kwargs['items_lst'].append('gunblade')
        self.set_champ_instance()
        self.inst.combat_loop()
        dps_with_item = self.inst.dps()

        # NO ITEM
        self.setUp()
        self.set_champ_instance()
        self.inst.combat_loop()

        dps_without_item = self.inst.dps()

        self.assertGreater(dps_with_item, dps_without_item,
                           "Item didn't increase dps.")

    def _test_aa_reset_by_ability(self):
        """
        Tests if an ability resets a champion's AA cooldown.
        """


if __name__ == '__main__':
    unittest.main()