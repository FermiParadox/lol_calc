import unittest

from tests import test_base


class TestJaxAbilities(test_base.GeneralTest):

    def test_jax_inn_att_speed(self):
        """
        Tests if jax innate increases his att_speed on each hit and then stabilizes after the 6th.
        """
        pass

    def test_jax_r_dmg(self):
        """
        Tests if jax r passive dmg is applied after 3 hits.
        """


if __name__ == '__main__':
    unittest.main()