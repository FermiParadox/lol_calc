"""
Contains history of modifications done to modules through automated tools.
Contains tools for automated modification of modules (insertion or replacement of class, dicts etc.).
"""

import copy


MODIFICATION_HISTORY = {}


class ObjectCreation(object):

    """
    Contains methods that create objects in string form.

    Objects end with at least one \n character.
    """

    @staticmethod
    def class_as_string(class_name, inheritance=None):
        """
        Creates a class (name and parent classes) in string form.

        Args:
            class_name: (str)
            inheritance:
                None
                (tpl) List of classes names as strings.
        Returns:
            (str)
        """

        string = 'class %s' % class_name

        if inheritance is not None:
            string += '('

            for inh_name in inheritance:
                string += inh_name + ', '

            string += '):\n\n'

        else:
            string += '(object):\n\n'

        return string

    @staticmethod
    def imports_as_strings(modules_to_import):
        """
        Creates module imports in string form.

        Args:
            modules_to_import: (lst) List of module names as strings.
        Returns:
            (str)
        """

        string = ''

        for module_name in modules_to_import:

            string += 'import %s\n' % module_name

        return string


class ObjectDetection(object):

    """

    """

    @staticmethod
    def imports_end_location(module_as_str):
        """
        Detects end of module imports in chosen module string.

        Non conditional imports must be on consecutive lines.
        Imports that are part of testing classes are ignored.

        Args:
            module_as_str: (str)
        Returns:
            (int)
        Raises:
            BaseException: If 0-indentation imports are not grouped together.
        """

    @staticmethod
    def dct_end_location(module_as_str, dct_name_end, name_to_body_connector=' = '):
        """
        Detects location of the last character of a dict (literal or constructor form).

        Args:
            module_as_str: (str)
            dct_name_end: (int) The start of the dict body.
            name_to_body_connector: (str) The intermediate characters between dict name and its body.
        Returns:
            (int)
        Raises:
            BaseException:
                If dict is not detected on same line as name.
                If dict is not closing because of mistyping.
        """

        char_str = module_as_str[dct_name_end:]

        # Checks if constructor or literal form
        # and notes bracket type.
        if char_str.find(name_to_body_connector+'dict(') == 0:
            opening_bracket_char = '('
            closing_bracket_char = ')'

        elif char_str.find(name_to_body_connector+'{') == 0:
            opening_bracket_char = '{'
            closing_bracket_char = '}'
        else:
            raise BaseException('No constructor or literal form dictionary detected at given start point.')

        opening_brackets = 0
        dct_end = None

        # Checks each character to see how many brackets opened and closed,
        # until they become equal (therefor dict has closed).
        for char, char_num in zip(char_str, range(len(char_str))):
            if char == opening_bracket_char:
                opening_brackets += 1
            elif char == closing_bracket_char:
                opening_brackets -= 1

                # Checks if dict has closed.
                if opening_brackets == 0:
                    dct_end = dct_name_end+char_num
                    break

        if dct_end is not None:
            return dct_end
        else:
            raise BaseException('Dictionary is not closed.')

    @staticmethod
    def class_end_location(module_as_str, class_name):
        """
        Detects where the class ends by checking 4-spaces after newlines or consecutive newlines.
        """

        class_start = module_as_str.index('class ' + class_name + '(')

        # Removes the initial part of the module (which does not contain the class).
        module_piece = module_as_str[class_start:]

        marker = 0
        class_end = None

        while True:

            # Finds the newline in the module_piece.
            # (marker is added to value to compensate for the slicing)
            next_newline_loc = module_piece[marker:].find('\n') + marker

            class_end = next_newline_loc

            # Breaks loop if there are no other newlines.
            if module_piece[marker:].find('\n') == -1:
                # (Then class end is at the end of the file.)
                class_end = len(module_piece)
                break

            # Detects comments that should be avoided even though they are syntactically allowed.
            if (module_piece[next_newline_loc:].find('\n#') == 0) or (module_piece[next_newline_loc:].find('\n"') == 0):
                raise BaseException('')

            # Detects newlines followed by 4 spaces ..
            if module_piece[next_newline_loc:].find('\n    ') == 0:
                pass

            # .. or newlines followed by a newline.
            elif module_piece[next_newline_loc:].find('\n\n') == 0:
                pass

            # If they are not detected, class has ended.
            else:
                break

            # Sets start on next character.
            marker += 1

        return class_start + class_end


class ObjectInsertion(ObjectCreation, ObjectDetection):

    def __init__(self):
        self.history = {}   # Contains log of modification events on current session.
                            # eg. {241014: {'jax': ['inserted CHAMP_BASE_STATS',], }, }

    def log_session_actions(self):
        """
        Modifies MODIFICATION_HISTORY by inserting all changes made during current session.

        return:
            None
        """

        final_mod_history = copy.deepcopy(MODIFICATION_HISTORY.update(self.history))

    def insert_or_replace_obj(self, module_name, obj_name, object_as_str, order=None):
        """
        Edits a module by inserting or replacing an object (given in string form).
        Also modifies history by inserting actions taken.

        Args:
            module_name: (string) Name of module to modify.
            obj_name: (string) Name of object to insert.
            object_as_str: (string) Object name, equal sign, and object body.
            order:
        Returns:
            None
        """

        # Searches in module and detects the location of an object.
        if self.locate_str(module_name=module_name, obj_name=obj_name):
            self.replace_obj(module_name=module_name,
                             obj_name=obj_name,
                             object_as_str=object_as_str)
        else:
            self.insert_obj(module_name=module_name,
                            obj_name=obj_name,
                            object_as_str=object_as_str,
                            order=order)


class ChampionModuleBuilder(ObjectInsertion):
    """
    Contains methods for the creation of a champion module and insertion of its basic objects.

    """
    def insert_imports(self, champ_name, modules_to_import):
        """
        Inserts or replaces existing reports.

        Returns:
            (str) Operation details, whether they were inserted, replaced, or ignored.
        """

        module_name = champ_name

        imports_as_str = self.imports_as_strings(modules_to_import=modules_to_import)

        self.insert_or_replace_obj(module_name=module_name, obj_name='imports', object_as_str=imports_as_str)

        pass

    def create_champion_module(self, champion_name):
        """
        Creates champion module and its contents. If module exists, it inserts the contents.

        Args:
            champion_name: (str)
        Returns:
            (str): Operation details, whether module was created, modified, or ignored.
        """

        pass


if __name__ == '__main__':

    class TestFactoryModule(object):
        DELIMITER = '\n----------------------------------------------------------'

        def test_dct_end_location(self, module_name, dct_name):
            """
            Returns:
                (str)
            """

            msg = self.DELIMITER

            with open(module_name, 'r') as file:
                mod_as_str = file.read()
                # Removed for test display clarity.
                mod_as_str = mod_as_str.replace('\n', '')

                dct_name_end = mod_as_str.find(dct_name)+len(dct_name)
                dct_body_end = ObjectDetection.dct_end_location(module_as_str=mod_as_str,
                                                                dct_name_end=dct_name_end)

                msg += '\nDict name: %s' % dct_name
                msg += '\nDict end location: %s' % str(dct_body_end)

                # Prints the piece at the end of the dict.
                # (ensures small names at start of module don't cause display problems)
                display_start = max(0, dct_body_end-30)
                display_end = dct_body_end + 1
                msg += '\nDict piece: ... %s ... \n' % mod_as_str[display_start:display_end]

            return msg

        def test_class_end_location(self, module_name, class_name):
            """
            Returns:
                (str)
            """

            msg = self.DELIMITER

            with open(module_name, 'r') as file:
                mod_as_str = file.read()

                class_end = ObjectDetection.class_end_location(module_as_str=mod_as_str, class_name=class_name)

                msg += '\nClass name: %s' % class_name
                msg += '\nClass end location: %s' % str(class_end)

                # Prints the piece at the end of the dict.
                # (ensures small names at start of module don't cause display problems)
                display_start = max(0, class_end-100)
                msg += '\nClass piece: ... %s ...\n' % mod_as_str[display_start:class_end]

            return msg

        def __repr__(self):

            module_and_dict_couples = (
                ('factory_module.py', 'MODIFICATION_HISTORY'),
                ('jax.py', 'CHAMPION_BASE_STATS'),
            )

            module_and_class_couples = (
                ('palette.py', '_Ability'),
                ('palette.py', 'ChampionsStats'),
            )
            #-------------------------------------------------
            # dct_end_location
            msg = self.DELIMITER
            for couple in module_and_dict_couples:

                msg += self.test_dct_end_location(module_name=couple[0], dct_name=couple[1])

            # class_end_location
            msg += self.DELIMITER
            for couple in module_and_class_couples:
                msg += self.test_class_end_location(module_name=couple[0], class_name=couple[1])

            msg += self.DELIMITER

            return msg

    print(TestFactoryModule().__repr__())