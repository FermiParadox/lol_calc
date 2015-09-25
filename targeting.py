# TODO: refactor everything, since it's very old code.


class Targeting(object):

    def __init__(self,
                 enemy_target_names):

        self.current_target = None
        self.targets_already_hit = None
        self.enemy_target_names = enemy_target_names

    def switch_to_first_alive_enemy(self):
        """Modifies current_target to first alive enemy.
        """
        for tar in self.enemy_target_names:
            if 'dead_buff' not in self.active_buffs[tar]:
                self.current_target = tar
                return
        else:
            self.current_target = None

    def switch_target(self, effect_name):
        """
        Modifies current_target based on the effect's target and available targets (non dead).
        """

        tar_type = getattr(self, effect_name)()['target']

        # If the effect targets the player..
        if tar_type == 'player':
            # .. it sets current_target to 'player'.
            self.current_target = 'player'
        # Otherwise it sets it to the first alive enemy.
        else:
            self.switch_to_first_alive_enemy()

    def is_alive(self, tar_name):
        if 'dead_buff' in self.active_buffs[tar_name]:
            return False
        else:
            return True

    def next_alive_enemy(self):
        """
        Modifies current_target,
        if there are available (and alive) enemy targets.

        If there are no valid targets, sets current_target to None.
        """

        if self.current_target in ('player', None):
            enemies_seq = self.enemy_target_names

        else:
            # Slices off current and previous enemies.
            curr_tar_index = 1 + self.enemy_target_names.index(self.current_target)
            enemies_seq = self.enemy_target_names[curr_tar_index:]

        for tar in enemies_seq:
            if self.is_alive(tar_name=tar):
                return tar

        else:
            # All enemies are dead.
            return None

    def target_type(self, tar_name=None):
        """
        Returns 'enemy' or 'player' based on the self.current_target.

        :param tar_name: If given, it checks its type instead of self.current_target.
        :return: (str)
        """

        if tar_name:
            tar = tar_name
        else:
            tar = self.current_target

        if tar != 'player':
            return 'enemy'
        else:
            return 'player'

    def reverse_target_type(self, tar_name=None):
        """
        Returns the opposite of given target type.

        :param tar_name:
        :return: (str)
        """

        if self.target_type(tar_name=tar_name) == 'player':
            return 'enemy'
        else:
            return 'player'

    def current_target_or_player(self, tar_type):
        if tar_type == 'player':
            return tar_type
        else:
            return self.current_target
