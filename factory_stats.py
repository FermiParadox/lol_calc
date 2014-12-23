import palette
import copy
import app_runes_database


class ChampionStatsRiot(object):

    STAT_NAME_CONVERSION_DCT = dict(
        firstly={
            '_per_lvl': 'perlevel',
            'ad': 'attackdamage',
            'mr': 'spellblock',
            '5': 'regen',
            'att_speed': 'attackspeed'
        },
        secondary={
            '_': ''
        })

    @staticmethod
    def palette_deepcopy_base_stats():

        return dict(
            mp=copy.deepcopy(palette.BaseStatsWithMana().CHAMPION_BASE_STATS))

    def api_champion_stats_dct(self, champ_name):
        """
        Returns a dict containing stats of a champion and their values.
        """

        api_stats_dct = app_runes_database.API_CHAMPIONS_BASE_STATS['data'][champ_name.capitalize()]['stats']

        app_stats_dct = self.palette_deepcopy_base_stats()['mp']

        # Determines the resource used by the champion for spells.
        if 'mp' in api_stats_dct:

            # Creates intermediate dict matching names between app and API.
            matched_names_dct = copy.deepcopy(app_stats_dct)

            # For each name in the app..
            for stat_name in app_stats_dct:

                matched_names_dct.update({stat_name: stat_name})

                # ..matches app name to a temporary API name.
                # The temporary name is modified until it reaches API format.

                # Applies initial modifications.
                for modification in self.STAT_NAME_CONVERSION_DCT['firstly']:

                    if modification in stat_name:

                        matched_names_dct[stat_name] = (
                            matched_names_dct[stat_name].replace(modification,
                                                                 self.STAT_NAME_CONVERSION_DCT['firstly'][modification]))

                # Then applies secondary.
                for modification in self.STAT_NAME_CONVERSION_DCT['secondary']:

                    if modification in stat_name:

                        matched_names_dct[stat_name] = (
                            matched_names_dct[stat_name].replace(modification,
                                                                 self.STAT_NAME_CONVERSION_DCT['secondary'][modification]))

                # Matches app and api keywords where applicable.
                if matched_names_dct[stat_name] in api_stats_dct:
                    app_stats_dct[stat_name] = api_stats_dct[matched_names_dct[stat_name]]

        return app_stats_dct

    def champion_stats_string(self, champ_name):
        """
        Creates a champion's base stats dict.

        Dictionary-string includes full name, '=' and it's in constructor form.

        Returns:
            (str)
        """

        # DICT TO STRING
        champ_stats_str = 'CHAMPION_BASE_STATS = '+str(self.api_champion_stats_dct(champ_name=champ_name))

        # Changes dict literal to dict constructor
        champ_stats_str = champ_stats_str.replace("{'", 'dict(\n    ')
        champ_stats_str = champ_stats_str.replace('}', ')')
        champ_stats_str = champ_stats_str.replace("': ", "=")

        champ_stats_str = champ_stats_str.replace(", '", ", ")

        # Adds newlines and indentation.
        champ_stats_str = champ_stats_str.replace(', ', ',\n    ')

        return champ_stats_str

    @staticmethod
    def insert_base_stats_dictionary(module_name, dictionary_name, dictionary_str):
        """
        Opens a file (or creates it if it doesn't exist) and edits it,
        by replacing the given dict or creating it if it doesnt exist.

        Dictionary_string includes full name, '=' and it's in constructor form.

        Returns:
            None
        """

        with open(module_name+'.py', 'w+') as unmodified_file:
            opened_file_as_str = unmodified_file.read()

            # SEARCH DICT.
            if opened_file_as_str.find(dictionary_name) != -1:
                # If so, stores its name start.
                dictionary_name_start_location = opened_file_as_str.find(dictionary_name)

                parenthesis_openings = 0
                dict_ending_index = dictionary_name_start_location

                # DETERMINE START AND FINISH OF DICT.
                # (starts searching after the dictionary name start)
                for char in opened_file_as_str[dictionary_name_start_location:]:

                    # Adds 1 until the loop ends, therefor marking the ending index.
                    dict_ending_index += 1

                    # Checks what the char was so that it defines the start and end of the dictionary.
                    if char == '(':
                        parenthesis_openings += 1
                    elif char == ')':
                        parenthesis_openings -= 1

                        # If all parenthesis have been closed,
                        # then it has reached the end of the dictionary.
                        if parenthesis_openings == 0:
                            break

                # CREATE NEW FILE
                opened_file_as_str = (opened_file_as_str[:dictionary_name_start_location] +
                                      dictionary_str +
                                      opened_file_as_str[dict_ending_index:])

            else:
                # CREATE NEW FILE
                opened_file_as_str = (dictionary_str +
                                      opened_file_as_str)

            # SAVE MODIFIED
            unmodified_file.write(opened_file_as_str)


class TotalChampionAttributesInsertion(object):
    TOTAL_CHAMPION_ATTRIBUTES_STRING = """
    class TotalChampionAttributes(RAbility):

    def abilities_effects(self):
        return dict(
            inn=self.inn_effects(),
            q=self.q_effects(),
            w=self.w_effects(),
            e=self.e_effects(),
            r=self.r_effects()
        )

    def abilities_stats(self):
        return dict(
            q=self.Q_STATS,
            w=self.W_STATS,
            e=self.E_STATS,
            r=self.R_STATS
        )
        """

    @staticmethod
    def insert_class_detector(class_name, class_string):
        """
        Opens a file and edits it,
        by inserting the TotalChampionAttributes class if not inserted.
        """




if __name__ == '__main__':

    champName = 'vi'

    ChampionStatsRiot().insert_base_stats_dictionary(module_name=champName,
                                                     dictionary_name='CHAMPION_BASE_STATS',
                                                     dictionary_str=ChampionStatsRiot().champion_stats_string(champName))