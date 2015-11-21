class NoViableEnemyError(Exception):
    pass


class Targeting(object):

    def __init__(self,
                 active_buffs,
                 total_enemies,
                 enemy_target_names):

        self.active_buffs = active_buffs
        self.targets_already_hit = None
        self.targets_already_buffed = None
        self.total_enemies = total_enemies
        self.enemy_target_names = enemy_target_names

        self.current_enemy = 'enemy_1'

    def is_dead(self, tar_name):
        return 'dead_buff' in self.active_buffs[tar_name]

    def is_alive(self, tar_name):
        return not self.is_dead(tar_name=tar_name)

    def first_alive_enemy(self):
        """
        Returns first alive enemy. If all enemies are dead, returns None.

        :return: (str) or (None)
        """
        for tar in self.enemy_target_names:
            if self.is_alive(tar_name=tar):
                return tar

        else:
            return None

    def all_enemies_dead(self):
        if self.first_alive_enemy():
            return False
        # If no alive enemy is found, then everyone is dead.
        else:
            return True

    def switch_to_first_alive_enemy(self):
        """
        Modifies current_target to first alive enemy. If all enemies are dead, raises exception.

        :return: (None)
        """
        tar = self.first_alive_enemy()

        if tar:
            self.current_enemy = tar
            return
        else:
            raise NoViableEnemyError("Everyone is dead. Can't switch to alive enemy")

    def next_alive_enemy(self, current_tar):
        """
        Returns next alive enemy. If all enemies are dead, returns None.

        :return: (str) or (None)
        """

        current_index = self.enemy_target_names.index(current_tar)
        next_index = current_index + 1

        # (max possible index is always smaller than len() by 1)
        if next_index < self.total_enemies:
            return self.enemy_target_names[next_index]
        else:
            return None

    def switch_to_next_alive_enemy(self):
        self.current_enemy = self.next_alive_enemy(current_tar=self.current_enemy)

    @staticmethod
    def target_type(tar_name):

        if tar_name == 'player':
            return 'player'
        else:
            return 'enemy'

    def target_name_by_owner_type(self, owner_type):
        if owner_type == 'player':
            return 'player'
        else:
            return self.first_alive_enemy()

    def opposite_target_type(self, tar_name):
        """
        Returns the opposite of given target type.

        :param tar_name:
        :return: (str)
        """

        if self.target_type(tar_name=tar_name) == 'player':
            return 'enemy'
        else:
            return 'player'

    def player_or_current_enemy(self, tar_type):
        if tar_type == 'player':
            return tar_type
        else:
            return self.current_enemy

    def player_or_first_alive_enemy(self, tar_type):
        if tar_type == 'player':
            return tar_type
        else:
            return self.first_alive_enemy()

    def set_current_enemy(self, examined_tar):
        """
        Sets current_enemy based on examined target.
        If examined target is 'player' it sets it to first alive enemy.
        If no enemy is alive, it sets it to last (dead) enemy.

        :param examined_tar:
        :return:
        """
        if examined_tar == 'player':
            # (if all enemies are dead, focuses on last enemy)
            self.current_enemy = self.first_alive_enemy() or self.enemy_target_names[-1]
        else:
            self.current_enemy = examined_tar
