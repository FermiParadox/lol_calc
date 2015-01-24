import unittest
import random
import buffs


class TestMethodAddBuffs(unittest.TestCase):

    def ability_dct_ranges(self):
        return dict(
            q=random.randint(1, 5),
            w=random.randint(1, 5),
            e=random.randint(1, 5),
            r=random.randint(1, 3))

    def available_targets(self):
        """Returns list with 'player' and 5 enemies."""
        tar_lst = ['player']
        for num in xrange(1, 6):
            tar_lst.append('enemy_'+str(num))
        return tar_lst

    def champion_lvl_dct_ranges(self):
        return [1, 18]

    def setUp(self):
        self.ability_lvls_dct = self.ability_dct_ranges()
        self.current_target = random.choice(self.available_targets)
        self.champion_lvls_dct = self.champion_lvl_dct_ranges()

    def test_add_buffs(self):

        buffs.BuffsGeneral(ability_lvls_dct=self.ability_lvls_dct,
                           champion_lvls_dct={},
                           selected_champions_dct={},
                           current_target=self.current_target,
                           current_time=self.current_time).add_buff(self.buff_name)


if __name__ == '__main__':


    print TestMethodAddBuffs().available_targets()