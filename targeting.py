class Targeting(object):

    def __init__(self,
                 active_buffs,
                 current_target=None,
                 targets_already_hit=None):

        self.current_target = current_target
        self.targets_already_hit = targets_already_hit
        self.active_buffs = active_buffs

    def switch_to_first_alive_enemy(self):
        """Modifies current_target to first alive enemy.
        """
        for tar in sorted(self.active_buffs):
                if (tar != 'player') and ('dead_buff' not in self.active_buffs[tar]):
                    self.current_target = tar
                    break

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

    def next_target(self, enemy_tar_names):
        """
        Modifies current_target,
        if there are available (and alive) enemy targets.

        If there are no valid targets, sets current_target to None.
        """

        while True:
            # Creates next target's name.
            next_tar_name = 'enemy_%s' % (int(self.current_target[6:]) + 1)

            # Checks if target exists.
            if next_tar_name not in enemy_tar_names:

                self.current_target = None
                break

            # Checks if target is alive.
            elif 'dead' not in self.active_buffs[next_tar_name]:
                # Sets next target name.
                self.current_target = next_tar_name
                break

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