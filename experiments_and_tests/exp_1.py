import time
import os
import importlib
import sys

PROJECT_PATH = '/home/black/Dev/PycharmProjects/WhiteProject'
RR = time.clock()
print(RR)


def modules_in_project_directory():
    all_files = os.listdir(PROJECT_PATH)

    project_files = set()
    py_files = set()

    # Filter our based on first letter.
    for name in all_files[:]:
        if name[0] in '._':
            pass
        else:
            project_files.add(name)

    # Adds '.py' files.
    for name in project_files:
        if name[-3:] == '.py':
            py_files.add(name)

        # Scans directories for '.py' files and them as well.
        elif name[-3:]:
            inner_dir_path = PROJECT_PATH + '/' + name
            for inner_name in os.listdir(inner_dir_path):
                if inner_name[-3:0] == '.py':
                    py_files.add(inner_name)

    py_files = {i[0:-3] for i in py_files}
    py_files = {i for i in py_files if i[0] not in '._'}

    return py_files


def modules_loaded():
    modules_names = {i for i in sys.modules.keys()}
    return modules_names


def reload_project_modules():
    used_modules = modules_in_project_directory() & set(modules_loaded())

    for module_name in used_modules:
        importlib.reload(importlib.import_module(module_name))


print(modules_in_project_directory())
print(modules_loaded())
reload_project_modules()