# Copyright (C) - 2023 - 2025 - Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import json
import pathlib

from cosmotech.orchestrator.core.command_template import CommandTemplate


class Plugin:
    def __init__(self, __file: str):
        self.name: str = pathlib.Path(__file).parent.name

        self.templates: dict[str, CommandTemplate] = dict()
        self.exit_commands: list[str] = list()

    def __register_template(self, template_name: str, template: CommandTemplate):
        template.sourcePlugin = self.name
        self.templates[template_name] = template

    def __register_exit_command(self, template_name):
        self.exit_commands.append(template_name)

    def register_template(self, template_as_dict: dict):
        try:
            _template = CommandTemplate(**template_as_dict)
            _template_name = _template.id
            self.__register_template(_template_name, _template)
        except ValueError:
            return False
        except TypeError:
            return False
        return _template

    def load_folder(self, plugin_folder: pathlib.Path):
        count = 0
        for _path in plugin_folder.glob("templates/**/*.json"):
            if _path.is_file():
                with _path.open("r") as _file:
                    try:
                        _file_content = json.load(_file)
                    except json.JSONDecodeError:
                        pass
                    else:
                        if not isinstance(_file_content, dict):
                            continue
                        is_exit_command = "templates/on_exit/" in str(_path)

                        def _read(_template_as_dict, is_exit_command: bool = False):
                            try:
                                _template = CommandTemplate(**_template_as_dict)
                            except ValueError:
                                return 0
                            _template_name = _template.id
                            self.__register_template(_template_name, _template)
                            if is_exit_command:
                                self.__register_exit_command(_template_name)
                            return 1

                        if _templates := _file_content.get("commandTemplates", []):
                            for _template_dict in _templates:
                                count += _read(_template_dict, is_exit_command)
                        else:
                            count += _read(_file_content, is_exit_command)
        return count
