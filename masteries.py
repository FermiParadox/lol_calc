import collections
import palette

BUFF_DCT_BASE = dict(
    target_type='placeholder',
    duration='placeholder',
    max_stacks='placeholder',
    stats=dict(
        placeholder_stat_1='placeholder'
    ),
    on_hit=dict(
        apply_buff=['placeholder', ],
        cause_dmg=['placeholder', ],
        reduce_cd={},
        remove_buff=['placeholder', ]
    ),
    prohibit_cd_start='placeholder',
    buff_source='placeholder',
    dot=False
)
_MASTERIES_BUFF_DCT = palette.buff_dct_base_deepcopy()
_MASTERIES_BUFF_DCT['target'] = 'player'
_MASTERIES_BUFF_DCT['duration'] = 'permanent'
_MASTERIES_BUFF_DCT['max_stacks'] = 1
_MASTERIES_BUFF_DCT['on_hit'] = None
_MASTERIES_BUFF_DCT['prohibit_cd_start'] = None
_MASTERIES_BUFF_DCT['buff_source'] = 'masteries'
_MASTERIES_BUFF_DCT['dot'] = False


class InvalidMasteriesSetupError(Exception):
    pass


class Masteries(object):

    MASTERIES_TREE_CATEGORIES = ()
    MASTERIES_ATTRIBUTES = {}
    PREVIOUS_TIER_REQUIRED_POINTS = 4
    MAX_MASTERIES_COUNT = 30

    def __init__(self, selected_masteries_dct):
        self.selected_masteries_dct = selected_masteries_dct
        self.__masteries_stats_buff = {}

    def _mastery_dct(self, mastery_name):
        return self.MASTERIES_ATTRIBUTES[mastery_name]

    def _mastery_stats_dct(self, mastery_name):
        return self._mastery_dct(mastery_name=mastery_name)['stats']

    def _max_mastery_points(self, mastery_name):
        return self._mastery_dct(mastery_name=mastery_name)['max_points']

    def _mastery_tier_points(self, mastery_name):
        return self._mastery_dct(mastery_name=mastery_name)['tier']

    def _mastery_tree_category(self, mastery_name):
        return self._mastery_dct(mastery_name=mastery_name)['tree_category']

    def _validate_single_mastery_dependencies(self, mastery_dct, mastery_name):
        """
        Checks if given mastery has enough points in masteries it depends from.

        :raise: InvalidMasteriesSetup
        :return: None
        """

        if 'from' in mastery_dct:
            roots_lst = mastery_dct['from']

            for root_mastery in roots_lst:
                root_points = self.selected_masteries_dct[root_mastery]

                # Dependency must have exactly max points.
                if root_points != self._max_mastery_points(mastery_name=mastery_name):
                    raise InvalidMasteriesSetupError

    def _validate_single_mastery_points_count(self, mastery_name):
        """
        Checks if given mastery exceeds its own max.

        :raise: InvalidMasteriesSetup
        :return: None
        """

        mastery_points = self.selected_masteries_dct[mastery_name]
        max_points = self._max_mastery_points(mastery_name=mastery_name)

        if (mastery_points < 0) or (mastery_points > max_points):
            raise InvalidMasteriesSetupError

    def _validate_tier_counts(self, tiers_points_dct):
        """
        Checks if all base tiers have enough points.

        :param tiers_points_dct:
        :return: None
        """
        for tree_name in tiers_points_dct:
            # Creates a list with all tiers' numbers excluding the highest.
            # Highest tier is ignored since its count is irrelevant.
            tree_tiers_dct = sorted(tiers_points_dct[tree_name])[:-1]

            # Therefor, all previous tiers must have enough points.
            for tier_num in tree_tiers_dct:
                # Tier count check.
                if tree_tiers_dct[tier_num] < self.PREVIOUS_TIER_REQUIRED_POINTS:
                    raise InvalidMasteriesSetupError

    def _validate_total_masteries_count(self, total_masteries_points):
        if total_masteries_points > self.MAX_MASTERIES_COUNT:
            raise InvalidMasteriesSetupError

    def _validate_masteries(self):

        total_points = 0
        tiers_points_dct = {k: collections.Counter() for k in self.MASTERIES_TREE_CATEGORIES}

        for mastery_name in self.selected_masteries_dct:
            mastery_dct = self.selected_masteries_dct[mastery_name]

            self._validate_single_mastery_dependencies(mastery_dct=mastery_dct, mastery_name=mastery_name)
            self._validate_single_mastery_points_count(mastery_name=mastery_name)

            mastery_points = self.selected_masteries_dct[mastery_name]
            mastery_tier = self._mastery_tier_points(mastery_name=mastery_name)
            mastery_category = self._mastery_tree_category(mastery_name=mastery_name)

            tiers_points_dct[mastery_category] += {mastery_tier: mastery_points}
            total_points += mastery_points

        self._validate_tier_counts(tiers_points_dct=tiers_points_dct)
        self._validate_total_masteries_count(total_masteries_points=total_points)

    def _create_masteries_buff(self):
        """
        Creates a single buff for stat-only masteries to avoid calculating everything multiple times.

        :return: None
        """

        self.__masteries_stats_buff

        total_stats = {}

        for mastery_name in self.selected_masteries_dct:
            stats_dct = self._mastery_stats_dct(mastery_name=mastery_name)

            # If it has no stats, goes to next mastery.
            if not stats_dct:
                continue

            # Index of mastery stat value tuple.
            index = self.selected_masteries_dct[mastery_name] - 1

            for stat_name in stats_dct:

                # (creates stat name if it doesnt exist)
                if stat_name not in total_stats:
                    total_stats.update({stat_name: {}})

                for stat_type in stats_dct[stat_name]:

                    # (creates type of given stat name if it doesnt exist)
                    if stat_type not in total_stats[stat_name]:
                        total_stats[stat_name].update({stat_type: 0})

                    # Values are determined by points in mastery.
                    stat_val = stats_dct[stat_name][stat_type][index]
                    # Adds value to existing counter.
                    total_stats[stat_name][stat_type] += stat_val

        self.__masteries_stats_buff['stats'] = total_stats

    def masteries_buff(self):
        return self.__masteries_stats_buff