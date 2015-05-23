import collections


class InvalidMasteriesSetupError(Exception):
    pass


class Masteries(object):

    MASTERIES_TREE_CATEGORIES = ()
    MASTERIES_ATTRIBUTES = {}
    PREVIOUS_TIER_REQUIRED_POINTS = 4
    MAX_MASTERIES_COUNT = 30

    def __init__(self, selected_masteries_dct):
        self.selected_masteries_dct = selected_masteries_dct

    def _mastery_dct(self, mastery_name):
        return self.MASTERIES_ATTRIBUTES[mastery_name]

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