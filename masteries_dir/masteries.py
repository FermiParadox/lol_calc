import masteries_dir.masteries_data as masteries_data

import palette
import collections


_CHOSEN_MASTERIES_BUFF_BASE = palette.buff_dct_base_deepcopy()
_CHOSEN_MASTERIES_BUFF_BASE['target_type'] = 'player'
_CHOSEN_MASTERIES_BUFF_BASE['duration'] = 'permanent'
_CHOSEN_MASTERIES_BUFF_BASE['max_stacks'] = 1
_CHOSEN_MASTERIES_BUFF_BASE['on_hit'] = None
_CHOSEN_MASTERIES_BUFF_BASE['prohibit_cd_start'] = None
_CHOSEN_MASTERIES_BUFF_BASE['buff_source'] = 'items'
_CHOSEN_MASTERIES_BUFF_BASE['dot'] = None
# (deleted so that a dict can be created later on that will have this dict updated in it as a reference)
del _CHOSEN_MASTERIES_BUFF_BASE['stats']


class MasteriesProperties(object):

    """
    Creates a single buff containing all static stats from masteries.     
    """

    def __init__(self, selected_masteries_dct, player_lvl):
        self.player_lvl = player_lvl
        self.selected_masteries_dct = selected_masteries_dct
        self.masteries_stats_dct = {}
        self.all_masteries_attrs_dct = masteries_data.MASTERIES_ATTRIBUTES
        
    def _create_stats_dct(self):

        for name in self.selected_masteries_dct:
            mastery_attrs_dct = self.all_masteries_attrs_dct[name]

            # If mastery has any data.
            if mastery_attrs_dct:
                mastery_stats = mastery_attrs_dct['stats']

                # If mastery has any stats.
                if mastery_stats:

                    for stat_name in mastery_stats:
                        stat_dct = mastery_stats[stat_name]

                        # Insert name if it doesn't exist.
                        self.masteries_stats_dct.setdefault(stat_name, {})


                        for stat_type in stat_dct:

                            if stat_type not in self.masteries_stats_dct[stat_name]:




        return {}