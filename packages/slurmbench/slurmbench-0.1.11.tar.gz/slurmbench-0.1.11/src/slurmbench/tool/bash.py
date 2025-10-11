"""Tools script logics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, final

import slurmbench.bash.items as bash_items
import slurmbench.experiment.file_system as exp_fs
import slurmbench.samples.bash as smp_sh

from . import results

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path


class Argument[R: results.Result]:
    """Argument bash lines builder."""

    def __init__(
        self,
        input_result: R,
        work_exp_fs_manager: exp_fs.WorkManager,
    ) -> None:
        """Initialize."""
        self._input_result = input_result
        self._input_data_smp_sh_fs_manager = smp_sh.sample_shell_fs_manager(
            input_result.exp_fs_manager(),
        )
        self._work_exp_fs_manager = work_exp_fs_manager
        self._work_smp_sh_fs_manager = smp_sh.sample_shell_fs_manager(
            self._work_exp_fs_manager,
        )

    def input_result(self) -> R:
        """Get input result."""
        return self._input_result

    def input_data_smp_sh_fs_manager(self) -> smp_sh.smp_fs.Manager:
        """Get input data sample shell file system manager."""
        return self._input_data_smp_sh_fs_manager

    def work_exp_fs_manager(self) -> exp_fs.WorkManager:
        """Get working experiment file system manager."""
        return self._work_exp_fs_manager

    def work_smp_sh_fs_manager(self) -> smp_sh.smp_fs.Manager:
        """Get working sample shell file system manager."""
        return self._work_smp_sh_fs_manager

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield from ()

    def close_lines(self) -> Iterator[str]:
        """Get shell input close lines."""
        yield from ()


class Options:
    """Bash lines builder for user tool options."""

    USER_TOOL_OPTIONS_VAR = bash_items.Variable("USER_TOOL_OPTIONS")

    def __init__(self, tool_options: Iterable[str]) -> None:
        """Initialize."""
        self.__tool_options = tool_options

    def tool_options(self) -> Iterable[str]:
        """Get tool options."""
        return self.__tool_options

    def set_options(self) -> Iterator[str]:
        """Set user tool options sh array variable."""
        yield self.USER_TOOL_OPTIONS_VAR.set(
            "(" + " ".join(self.__tool_options) + ")",
        )


class WithOptions(ABC):
    """Commands with options."""

    WORK_EXP_SAMPLE_DIR_VAR = bash_items.Variable("WORK_EXP_SAMPLE_DIR")

    CORE_COMMAND_SH_FILENAME = "core_command.sh"

    @classmethod
    def core_command_sh_path(cls, tool_bash_script_dir: Path) -> Path:
        """Get core command shell path."""
        return tool_bash_script_dir / cls.CORE_COMMAND_SH_FILENAME

    def __init__(
        self,
        opts_sh_lines_builder: Options,
        exp_fs_managers: exp_fs.Managers,
        tool_bash_script_dir: Path,
    ) -> None:
        """Initialize."""
        self._opts_sh_lines_builder = opts_sh_lines_builder
        self._exp_fs_managers = exp_fs_managers
        self._tool_bash_script_dir = tool_bash_script_dir

    @abstractmethod
    def init_lines(self) -> Iterator[str]:
        """Iterate over core command shell input init lines."""
        raise NotImplementedError

    @abstractmethod
    def close_lines(self) -> Iterator[str]:
        """Iterate over core command shell input close lines."""
        raise NotImplementedError

    def commands(self) -> Iterator[str]:
        """Iterate over the tool commands."""
        # DOCU say WORK_EXP_SAMPLE_DIR variable is set
        # DOCU say SAMPLES_TSV variable is set
        yield from smp_sh.SampleUIDLinesBuilder(
            self._exp_fs_managers.data().samples_tsv(),
        ).lines()
        yield ""
        yield from self.set_work_sample_exp_dir()
        yield from self.mkdir_work_sample_exp_dir()
        yield ""
        yield from self._opts_sh_lines_builder.set_options()
        yield ""
        yield from self.init_lines()
        yield ""
        yield from self.core_commands()
        yield ""
        yield from self.close_lines()

    def opts_sh_lines_builder(self) -> Options:
        """Get options bash lines builder."""
        return self._opts_sh_lines_builder

    def exp_fs_managers(self) -> exp_fs.Managers:
        """Get experiment file system managers."""
        return self._exp_fs_managers

    def set_work_sample_exp_dir(self) -> Iterator[str]:
        """Set working experiment sample directory."""
        work_exp_sample_dir = smp_sh.sample_shell_fs_manager(
            self._exp_fs_managers.work(),
        ).sample_dir()
        yield self.WORK_EXP_SAMPLE_DIR_VAR.set(
            bash_items.path_to_str(work_exp_sample_dir),
        )

    def mkdir_work_sample_exp_dir(self) -> Iterator[str]:
        """Mkdir working experiment sample directory."""
        yield f"mkdir -p {self.WORK_EXP_SAMPLE_DIR_VAR.eval()} 2>/dev/null"

    def core_commands(self) -> Iterator[str]:
        """Iterate over the tool command lines."""
        core_command_shell_path = self.core_command_sh_path(self._tool_bash_script_dir)

        with core_command_shell_path.open("r") as in_core_cmd:
            for line in in_core_cmd:
                yield line.rstrip()


class OnlyOptions(WithOptions):
    """Tool commands when the tool has no arguments."""

    def init_lines(self) -> Iterator[str]:
        """Iterate over core command shell input init lines."""
        yield from ()

    def close_lines(self) -> Iterator[str]:
        """Iterate over core command shell input close lines."""
        yield from ()


@final
class WithArguments(WithOptions):
    """Tool commands with options and arguments."""

    def __init__(
        self,
        arg_sh_lines_builders: Iterable[Argument],
        opts_sh_lines_builder: Options,
        exp_fs_managers: exp_fs.Managers,
        _tool_bash_script_dir: Path,
    ) -> None:
        """Initialize."""
        self._arg_sh_lines_builders = list(arg_sh_lines_builders)
        super().__init__(opts_sh_lines_builder, exp_fs_managers, _tool_bash_script_dir)

    def arg_sh_lines_builders(self) -> Iterator[Argument]:
        """Get argument bash lines builders."""
        yield from self._arg_sh_lines_builders

    def init_lines(self) -> Iterator[str]:
        """Iterate over core command shell input init lines."""
        for result_lines_builder in self._arg_sh_lines_builders:
            yield from result_lines_builder.init_lines()

    def close_lines(self) -> Iterator[str]:
        """Iterate over core command shell input close lines."""
        for result_lines_builder in self._arg_sh_lines_builders:
            yield from result_lines_builder.close_lines()
