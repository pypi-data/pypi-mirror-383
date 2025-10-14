"""Tool connector module."""

from __future__ import annotations

import inspect
import logging
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Self, TypeVar, final

import slurmbench.experiment.file_system as exp_fs
import slurmbench.topic.results as topic_res
import slurmbench.topic.visitor as topic_visitor

from . import bash, results
from . import config as cfg
from . import description as desc

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_LOGGER = logging.getLogger(__name__)


class Names(StrEnum):
    """Tool names."""

    @abstractmethod
    def topic_tools(self) -> type[topic_visitor.Tools]:
        """Get topic tools."""
        raise NotImplementedError


class InvalidToolNameError[N: Names, T: topic_visitor.Tools]:
    """Invalid tool name error."""

    def __init__(
        self,
        arg_name: N,
        invalid_tool_name: str,
        valid_tools: Iterable[T],
    ) -> None:
        self._arg_name = arg_name
        self._invalid_tool_name = invalid_tool_name
        self._valid_tools = tuple(valid_tools)

    def arg_name(self) -> N:
        """Get argument name."""
        return self._arg_name

    def invalid_tool_name(self) -> str:
        """Get invalid tool name."""
        return self._invalid_tool_name

    def valid_tools(self) -> tuple[T, ...]:
        """Get list of valid tools."""
        return self._valid_tools


class Arg[N: Names, T: topic_visitor.Tools, R: results.Result](ABC):
    """Tool argument configuration."""

    @classmethod
    def config_type(cls) -> type[cfg.Arg]:
        """Get config type."""
        return cfg.Arg

    @classmethod
    @abstractmethod
    def name(cls) -> N:
        """Get name."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def tools_type(cls) -> type[T]:
        """Get tools type."""
        raise NotImplementedError

    @classmethod
    def valid_tools(cls) -> Iterable[T]:
        """Get valid tools."""
        return (
            tool
            for tool in cls.tools_type()
            if cls.result_visitor().tool_gives_the_result(tool)
        )

    @classmethod
    @abstractmethod
    def result_visitor(cls) -> type[topic_res.Visitor[T, R]]:
        """Get result visitor function."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def sh_lines_builder_type(cls) -> type[bash.Argument[R]]:
        """Get shell lines builder."""
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: cfg.Arg) -> Self | InvalidToolNameError[N, T]:
        """Convert dict to object."""
        try:
            tool = cls.tools_type()(config.tool_name())
        except ValueError:
            return InvalidToolNameError(
                cls.name(),
                config.tool_name(),
                cls.valid_tools(),
            )
        match cls.result_visitor().result_builder_from_tool(tool):
            case topic_res.Error():
                return InvalidToolNameError(
                    cls.name(),
                    config.tool_name(),
                    cls.valid_tools(),
                )
        return cls(tool, config.exp_name())

    def __init__(self, tool: T, exp_name: str) -> None:
        """Initialize."""
        self._tool = tool
        self._exp_name = exp_name

    def tool(self) -> T:
        """Get tool."""
        return self._tool

    def exp_name(self) -> str:
        """Get experiment name."""
        return self._exp_name

    def result(self, data_exp_fs_manager: exp_fs.DataManager) -> R:
        """Convert argument to input."""
        return self.result_visitor().result_builder()(
            exp_fs.WorkManager(
                data_exp_fs_manager.root_dir(),
                self._tool.to_description(),
                self._exp_name,
            ),
        )

    def sh_lines_builder(self, exp_fs_managers: exp_fs.Managers) -> bash.Argument[R]:
        """Convert input to shell lines builder."""
        return self.sh_lines_builder_type()(
            self.result(exp_fs_managers.data()),
            exp_fs_managers.work(),
        )

    def to_config(self) -> cfg.Arg:
        """Convert to config."""
        return cfg.Arg(str(self._tool), self._exp_name)


class MissingArgumentNameError[N: Names]:
    """Missing argument name error."""

    def __init__(self, missing_arg_name: N, names_type: type[N]) -> None:
        self._missing_arg_name = missing_arg_name
        self._names_type = names_type

    def missing_arg_name(self) -> N:
        """Get missing argument name."""
        return self._missing_arg_name

    def names_type(self) -> type[N]:
        """Get names type."""
        return self._names_type


class ExtraArgumentNameError[N: Names]:
    """Extra argument name error."""

    def __init__(self, extra_arg_names: Iterable[str], names_type: type[N]) -> None:
        self._extra_arg_names = tuple(extra_arg_names)
        self._names_type = names_type

    def extra_arg_names(self) -> tuple[str, ...]:
        """Get extra argument name."""
        return self._extra_arg_names

    def names_type(self) -> type[N]:
        """Get names type."""
        return self._names_type


ArgsLoadError = InvalidToolNameError | MissingArgumentNameError | ExtraArgumentNameError

NamesTypeVar = TypeVar("NamesTypeVar", bound=Names)
ArgWithName = Arg[
    NamesTypeVar,
    topic_visitor.Tools,
    results.Result,
]


class Arguments[N: Names](ABC):
    """Tool arguments configuration."""

    @classmethod
    def config_type(cls) -> type[cfg.Arguments]:
        """Get config type."""
        return cfg.Arguments

    @classmethod
    @abstractmethod
    def arg_types(cls) -> list[type[ArgWithName[N]]]:
        """Get argument type."""
        raise NotImplementedError

    @classmethod
    def names_type(cls) -> type[N]:
        """Get names type."""
        return type(cls.arg_types()[0].name())

    @classmethod
    def from_config(cls, config: cfg.Arguments) -> Self | ArgsLoadError:
        """Convert dict to object."""
        arg_dict: dict[N, ArgWithName[N]] = {}
        for arg_type in cls.arg_types():
            try:
                arg_config = config[str(arg_type.name())]
            except KeyError:
                return MissingArgumentNameError(arg_type.name(), cls.names_type())

            match arg_or_err := arg_type.from_config(arg_config):
                case Arg():
                    arg_dict[arg_type.name()] = arg_or_err
                case InvalidToolNameError():
                    return arg_or_err

        if extra_arg := set(config.arguments().keys()) - {str(n) for n in arg_dict}:
            return ExtraArgumentNameError(extra_arg, cls.names_type())

        return cls(arg_dict)

    def __init__(self, arguments: dict[N, ArgWithName[N]]) -> None:
        self.__arguments = arguments

    def __getitem__(self, name: N) -> ArgWithName[N]:
        """Get argument."""
        return self.__arguments[name]

    def __iter__(self) -> Iterator[tuple[N, ArgWithName[N]]]:
        """Iterate arguments."""
        return iter(self.__arguments.items())

    def results(
        self,
        data_exp_fs_manager: exp_fs.DataManager,
    ) -> Iterator[tuple[N, results.Result]]:
        """Iterate over results associated with the arguments."""
        yield from (
            (name, arg.result(data_exp_fs_manager))
            for name, arg in self.__arguments.items()
        )

    def sh_lines_builders(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> Iterator[bash.Argument]:
        """Convert to commands."""
        return (
            arg.sh_lines_builder(exp_fs_managers) for arg in self.__arguments.values()
        )

    def to_config(self) -> cfg.Arguments:
        """Convert to config."""
        return cfg.Arguments(
            {str(name): arg.to_config() for name, arg in self.__arguments.items()},
        )


@final
class StringOpts:
    """String options.

    When the options are regular short/long options.
    """

    @classmethod
    def from_config(cls, config: cfg.StringOpts) -> Self:
        """Convert dict to object."""
        return cls(config)

    def __init__(self, options: Iterable[str]) -> None:
        self.__options = list(options)

    def __bool__(self) -> bool:
        """Check if options are not empty."""
        return len(self.__options) > 0

    def __len__(self) -> int:
        """Get options length."""
        return len(self.__options)

    def __iter__(self) -> Iterator[str]:
        """Iterate options."""
        return iter(self.__options)

    def sh_lines_builder(self) -> bash.Options:
        """Get shell lines builder type."""
        return bash.Options(self)

    def to_config(self) -> cfg.StringOpts:
        """Convert to config."""
        return cfg.StringOpts(self.__options)


class WithOptions[C: cfg.WithOptions, E](ABC):
    """Tool config with options."""

    @classmethod
    @abstractmethod
    def description(cls) -> desc.Description:
        """Get tool description."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def config_type(cls) -> type[C]:
        """Get config type."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_config(cls, config: C) -> Self | E:
        """Convert dict to object."""
        raise NotImplementedError

    def __init__(self, options: StringOpts) -> None:
        """Initialize."""
        self._options = options

    def options(self) -> StringOpts:
        """Get options."""
        return self._options

    @abstractmethod
    def to_config(self) -> cfg.WithOptions:
        """Convert to config."""
        raise NotImplementedError

    @abstractmethod
    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.WithOptions:
        """Get sh commands."""
        raise NotImplementedError

    def is_same(self, other: Self) -> bool:
        """Check if configs are the same."""
        return self.to_config().is_same(other.to_config())

    @classmethod
    def parent_dir_where_defined(cls) -> Path:
        """Get the parent directory of the module defining the connector.

        Usefull to retrieve the tool template bash script.
        """
        cls_mod = inspect.getmodule(cls)
        match cls_mod:
            case None:
                _LOGGER.critical("No module for %s", cls)
                raise ValueError
        if cls_mod.__file__ is None:
            _LOGGER.critical("No file for %s", cls)
            raise ValueError
        return Path(cls_mod.__file__).parent


class OnlyOptions(WithOptions[cfg.OnlyOptions, "OnlyOptions"]):
    """Tool config without arguments."""

    @classmethod
    def config_type(cls) -> type[cfg.OnlyOptions]:
        """Get config type."""
        return cfg.OnlyOptions

    @classmethod
    def from_config(cls, config: cfg.OnlyOptions) -> Self:
        """Convert dict to object."""
        return cls(StringOpts.from_config(config.options()))

    @classmethod
    def commands_type(cls) -> type[bash.OnlyOptions]:
        """Get commands type."""
        # DOCU user can change CommandsOnlyOptions
        return bash.OnlyOptions

    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.OnlyOptions:
        """Get sh commands."""
        return self.commands_type()(
            bash.Options(self._options),
            exp_fs_managers,
            self.parent_dir_where_defined(),
        )

    def to_config(self) -> cfg.OnlyOptions:
        """Convert to dict."""
        return cfg.OnlyOptions(self._options.to_config())


class WithArguments[N: Names](WithOptions[cfg.WithArguments, ArgsLoadError]):
    """Tool config with arguments."""

    @classmethod
    @abstractmethod
    def arguments_type(cls) -> type[Arguments[N]]:
        """Get argument arguments type."""
        raise NotImplementedError

    @classmethod
    def config_type(cls) -> type[cfg.WithArguments]:
        """Get config type."""
        return cfg.WithArguments

    @classmethod
    def from_config(cls, config: cfg.WithArguments) -> Self | ArgsLoadError:
        """Convert dict to object."""
        match arg_or_err := cls.arguments_type().from_config(config.arguments()):
            case Arguments():
                return cls(arg_or_err, StringOpts.from_config(config.options()))
            case _:
                return arg_or_err

    def __init__(self, arguments: Arguments[N], options: StringOpts) -> None:
        """Initialize."""
        super().__init__(options)
        self._arguments = arguments

    def arguments(self) -> Arguments[N]:
        """Get arguments."""
        return self._arguments

    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.WithArguments:
        """Get sh commands."""
        return bash.WithArguments(
            self._arguments.sh_lines_builders(exp_fs_managers),
            self.options().sh_lines_builder(),
            exp_fs_managers,
            self.parent_dir_where_defined(),
        )

    def to_config(self) -> cfg.WithArguments:
        """Convert to dict."""
        return cfg.WithArguments(
            self._arguments.to_config(),
            self._options.to_config(),
        )


def get_arg[A: Arg](
    exp_fs_manager: exp_fs.ManagerBase,
    arg_type: type[A],
) -> A | InvalidToolNameError:
    """Get argument."""
    arg_config = cfg.Arg.from_yaml(exp_fs_manager.config_yaml())
    return arg_type.from_config(arg_config)
