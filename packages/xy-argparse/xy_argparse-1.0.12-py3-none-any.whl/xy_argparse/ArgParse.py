# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "ArgParse"
"""
  * @File    :   ArgParse.py
  * @Time    :   2023/06/06 19:40:37
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
"""

from argparse import ArgumentParser, Namespace
import pkg_resources
from uuid import uuid4


class ArgParse:
    identifier: str = uuid4().hex
    __prog = None
    description = "命令行解析"
    __version = None

    def fetch_package_version(self, package_name="") -> str | None:
        version = None
        try:
            version = pkg_resources.get_distribution(package_name).version
        except:
            pass
        return version

    def quick_default_info(self, module_name=""):
        version = self.fetch_package_version(module_name)
        self.prog = f"{module_name}-{version}"
        self.description = f""">>>>>>>>>>>> {module_name} - v{version} <<<<<<<<<<<<<"""

    @property
    def prog(self):
        if isinstance(self.__prog, str) and len(self.__prog) > 0:
            return self.__prog
        module_name = self.__module__
        if isinstance(self.__module__, str) and len(self.__module__) > 0:
            if "." in self.__module__:
                module_name = self.__module__.split(".")[0]
        return module_name

    @prog.setter
    def prog(self, prog):
        self.__prog = prog

    @property
    def version(self):
        if isinstance(self.__version, str) and len(self.__version) > 0:
            return self.__version
        module_name = self.__module__
        try:
            return pkg_resources.get_distribution(module_name.split(".")[0]).version
        except:
            return self.__version

    @version.setter
    def version(self, version):
        self.__version = version

    parser = ArgumentParser(
        prog=__prog,
        description=description,
    )
    __arguments = None

    def __init__(
        self,
        prog=__prog,
        description=description,
        version=__version,
    ) -> None:
        self.__prog = prog
        self.description = description
        self.__version = version
        self.default_parser()
        self.add_arguments()
        self.parse_arguments()

    def default_parser(self):
        self.parser = ArgumentParser(
            prog=self.prog,
            description=self.description,
        )

    def add_arguments(self):
        pass

    def add_argument(
        self,
        flag: str,
        name: str,
        action=None,  # type: ignore
        type_name: type = str,
        help_text: str = "",
        choices=None,
        required=False,
        nargs="?",
        default=None,
    ) -> None:
        if isinstance(self.parser, ArgumentParser):
            self.parser.add_argument(
                flag,
                name,
                type=type_name,
                help=help_text,
                action=action,  # type: ignore
                choices=choices,
                required=required,
                nargs=nargs,
                default=default,
            )

    def arguments(self):
        return self.__arguments

    def parse_arguments(self):
        try:
            self.__arguments, _ = self.parser.parse_known_args()
        except:
            self.__arguments = None

    def get_argument(self, name: str):
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            arguments_map = arguments.__dict__
            if isinstance(arguments_map, dict):
                return arguments_map.get(name)
        return None

    def run_arguments(self):
        self.parse_arguments()
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            arguments_map = arguments.__dict__
            for argument_name, argument_value in arguments_map.items():
                go_on = self.on_arguments(
                    argument_name,
                    argument_value,
                    arguments=arguments,
                )
                if go_on is True:
                    continue
                else:
                    break

    def on_arguments(
        self,
        name,
        value,
        arguments=None,
    ):
        return True
