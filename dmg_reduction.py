class ArmorMRReduction(object):

    @staticmethod
    def reduced_armor(request_stat, bonuses_dct, target, stat='armor'):
        """Returns the armor a dmg "sees".

        Order of application is: 'flat armor reduction', 'percent armor reduction', 'percent armor penetration',
        'flat armor penetration'.

        Reductions are target based bonuses. Penetrations are player based.
        """
        # Checks if stat is inside target's bonuses dict,
        # .. since some stats don't exist in base_stats they can only be created by bonuses.
        if ('percent_'+stat+'_reduction') in bonuses_dct[target]:
            percent_reduction = request_stat(target, 'percent_'+stat+'_reduction')
        else:
            percent_reduction = 0

        if ('percent_'+stat+'_penetration') in bonuses_dct['player']:
            percent_penetration = request_stat('player', 'percent_'+stat+'_penetration')
        else:
            percent_penetration = 0

        armor_after_reductions = request_stat(target, stat)
        # Applies flat reduction
        if ('flat_'+stat+'_reduction') in bonuses_dct[target]:
            armor_after_reductions -= request_stat(target, 'flat_'+stat+'_reduction')

        # Applies percent reduction and percent penetration
        if armor_after_reductions <= 0:
            return armor_after_reductions                               # Armor can't be reduced further if negative
        else:
            armor_after_reductions *= (1-percent_reduction) * (1-percent_penetration)

        # Applies flat penetration
        if ('flat_'+stat+'_penetration') in bonuses_dct['player']:
            if armor_after_reductions > request_stat('player', 'flat_'+stat+'_penetration'):
                return armor_after_reductions - request_stat('player', 'flat_'+stat+'_penetration')
            else:
                return 0.
        else:
            return armor_after_reductions

    def reduced_mr(self, request_stat, bonuses_dct, target):
        """Returns the magic resist a dmg "sees".

        Same as reduced_armor().
        """
        return self.reduced_armor(request_stat, bonuses_dct, target, stat='mr')

    def percent_physical_reduction_by_armor(self, request_stat, bonuses_dct, target, stat='armor'):
        """Returns percentage dmg reduction caused by armor.
        """
        return (self.reduced_armor(request_stat, bonuses_dct, target, stat) /
                (100.+abs(self.reduced_armor(request_stat, bonuses_dct, target, stat)))
                )

    def percent_magic_reduction_by_mr(self, request_stat, bonuses_dct, target):
        """Returns percentage reduction caused by mr.
        """
        return self.percent_physical_reduction_by_armor(request_stat, bonuses_dct, target, stat='mr')

    def physical_dmg_taken(self, request_stat, bonuses_dct, target):
        """
        (float) -> float

        Returns dmg_taken after armor.
        >>>ArmorMRReduction().physical_dmg_taken(-25.)
        1.2
        """
        return 1. - self.percent_physical_reduction_by_armor(request_stat, bonuses_dct, target)

    def magic_dmg_taken(self, request_stat, bonuses_dct, target):
        """
        (float) -> float

        Returns dmg_taken after mr.

        >>>ArmorMRReduction().magic_dmg_taken(-25.)
        1.2
        """
        return 1. - self.percent_magic_reduction_by_mr(request_stat, bonuses_dct, target)


class DmgMitigation(ArmorMRReduction):

    @staticmethod
    def mitigated_dmg(dmg_value, dmg_type, request_stat, bonuses_dct, target):
        """
        (float, str, dict) -> float

        Returns mitigated dmg based on its type (magic, physical, AA).
        True dmg doesn't reach this method.
        """

        if dmg_type == 'health_regen':
            return dmg_value

        # Checks if there is any percent dmg reduction and applies it.
        if 'percent_dmg_reduction' in bonuses_dct[target]:
            dmg_value *= 1-request_stat(target, 'percent_dmg_reduction')

        # Magic dmg.
        if dmg_type == 'magic':
            # Checks if there is any percent magic reduction and applies it.
            dmg_value *= 1-request_stat(target, 'percent_magic_reduction')

            # Checks if there is flat magic reduction
            if 'flat_magic_reduction' in bonuses_dct[target]:
                dmg_value -= request_stat(target, 'flat_magic_reduction')

            # Checks if there is flat reduction
            if 'flat_reduction' in bonuses_dct[target]:
                dmg_value -= request_stat(target, 'flat_reduction')

            return max(dmg_value, 0)

        # Physical (AA or non-AA)..
        else:
            # Checks if there is any percent physical reduction and applies it.
            dmg_value *= 1-request_stat(target, 'percent_physical_reduction')

            # Checks if there is flat physical reduction
            if 'flat_physical_reduction' in bonuses_dct[target]:
                dmg_value -= request_stat(target, 'flat_physical_reduction')

            # Checks if there is flat reduction
            if 'flat_reduction' in bonuses_dct[target]:
                dmg_value -= request_stat(target, 'flat_reduction')

            # AA reduction.
            if dmg_type == 'AA':
                if 'flat_AA_reduction' in bonuses_dct[target]:
                    dmg_value -= request_stat(target, 'flat_AA_reduction')
                return dmg_value
            else:
                return dmg_value


if __name__ == '__main__':

    class TestArmorMRReduction(object):

        MSG_START = '\n\n---------------------------'

        def tot_stats(self, tar, stat):
                return self.tot_stats_dct[tar][stat]

        def set_up(self):

            self.tot_stats_dct = dict(
                player=dict(),
                enemy_1=dict(
                    armor=100,
                    mr=100),
                enemy_2=dict(
                    armor=100,
                    mr=100),
                enemy_3=dict(
                    armor=100,
                    mr=100))

            self.bonuses_dct = dict(
                player=dict(),
                enemy_1=dict(),
                enemy_2=dict())

        def test_reduced_armor(self):

            self.set_up()



            msg = self.MSG_START

            return msg