import dmg_categories
import palette
import copy


class ItemsBase(dmg_categories.Categories):

    def __init__(self,
                 tot_stats,
                 act_buffs,
                 current_stats,
                 current_target,
                 champion_lvls_dct,
                 current_target_num):

        self.active_buffs = act_buffs

        dmg_categories.Categories.__init__(self,
                                           tot_stats=tot_stats,
                                           current_stats=current_stats,
                                           current_target=current_target,
                                           champion_lvls_dct=champion_lvls_dct,
                                           current_target_num=current_target_num)


class Gunblade(ItemsBase):

    GUNBLADE_ATTRIBUTES = dict(
        passive=dict(
            ad=45,
            ap=65,
            lifesteal=12/100,
            spellvamp=20/100,
        ),

        unique_passive=dict(
            spellvamp=20/100,),
        active=dict(
            dmg_type='magic',
            base_dmg=150,
            scaling_stats=dict(
                ap=40/100
            ),

            duration=2,
            cooldown=60,
            cooldown_timer_reduction=3,

            speed_reduction=40/100,


        ))

    def gunblade_stats_buff(self):

        return dict(
            stats=dict(
                ad=dict(
                    additive=self.GUNBLADE_ATTRIBUTES['passive']['ad']),
                ap=dict(
                    additive=self.GUNBLADE_ATTRIBUTES['passive']['ap']),
                lifesteal=dict(
                    additive=self.GUNBLADE_ATTRIBUTES['passive']['lifesteal']),
            ),

            # (up to 6 gunblades can provide this bonus)
            max_stacks=6,
            target='player',
            duration='permanent',)

    def gunblade_unique_passive_buff(self):
        return dict(
            stats=dict(
                spellvamp=dict(
                    additive=self.GUNBLADE_ATTRIBUTES['passive']['spellvamp']),),

            target='player',
            duration='permanent',)

    def gunblade_dmg(self):

        return dict(
            dmg_category='standard_dmg',
            dmg_type=self.GUNBLADE_ATTRIBUTES['active']['dmg_type'],
            target='enemy',
            special={'spellvamp': None, 'dmg_source': 'gunblade'}
        )

    def gunblade_dmg_value(self):

        return self.standard_dmg(ability_dct=self.GUNBLADE_ATTRIBUTES['active'])

    def gunblade_slow_buff(self):

        return dict(
            stats=dict(
                speed_reduction=dict(
                    percent=self.GUNBLADE_ATTRIBUTES['active']['speed_reduction']),
            ),

            duration=self.GUNBLADE_ATTRIBUTES['active']['duration'],
            target='enemy')

    @staticmethod
    def gunblade_effects():

        return dict(
            enemy=dict(

                # Buffs and effects activated on cast.
                actives=dict(buffs=['gunblade_slow_buff'],
                             dmg=['gunblade_dmg'])),

            player=dict(

                # Buffs and effects activated at purchase.
                passives=dict(buffs=['gunblade_stats_buff', 'gunblade_unique_passive_buff'],
                              dmg=[]))
        )


class AllItems(Gunblade,):

    def __init__(self, items_lst, kwargs):

        """
        Sets item effects when called.
        """

        self.items_lst = items_lst
        self.items_effects = {}

        ItemsBase.__init__(self, **kwargs)

        self.set_items_effects()

    def set_items_effects(self):
        """
        Modifies items_effects by inserting effects of all items.

        After modification items_effects contains effects of each item.
        Multiple buffs of an item are handled in other methods.
        """

        # Appends each item's effects to the 'items_effects'.
        for item_name in self.items_lst:
            item_effect_dct = getattr(self, item_name + '_effects')()
            dct = copy.deepcopy(palette.ChampionsStats.item_effects())

            # (player or enemy)
            for tar_type in item_effect_dct:
                # (passive or active)
                for application_type in item_effect_dct[tar_type]:
                    # (multiplicative or additive)
                    for effect_type in item_effect_dct[tar_type][application_type]:
                        # (dmg or buff)
                        for effect_name in item_effect_dct[tar_type][application_type][effect_type]:

                            dct[tar_type][application_type][effect_type].append(effect_name)

            # If item hasn't been applied before, it applies it.
            # (Otherwise, item was bought multiple times, and has already been added.)
            if item_name not in self.items_effects:
                self.items_effects.update({item_name: dct})
