"""Tools script logics."""

from __future__ import annotations

import logging
import shutil
import stat
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, assert_never

import typer

import slurmbench.bash.items as bash_items
import slurmbench.experiment.file_system as exp_fs
import slurmbench.experiment.managers as exp_managers
import slurmbench.experiment.slurm.status as exp_slurm_status
import slurmbench.samples.items as smp
import slurmbench.slurm.bash as slurm_bash
import slurmbench.tool.bash as tool_bash
import slurmbench.tool.environments as tools_envs

from . import items as exp_bash_items
from . import manager

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_LOGGER = logging.getLogger(__name__)


def run_scripts(
    exp_manager: exp_managers.OnlyOptions | exp_managers.WithArguments,
    samples_to_run: Iterable[smp.RowNumbered],
    slurm_opts: str,
) -> manager.Manager:
    """Create the run script."""
    sh_manager = manager.Manager.from_exp_fs_manager(exp_manager)
    sh_manager.data_sh_fs_manager().scripts_dir().mkdir(parents=True, exist_ok=True)
    sh_manager.work_sh_fs_manager().scripts_dir().mkdir(parents=True, exist_ok=True)

    exp_manager.fs_managers().work().slurm_log_fs_manager().log_dir().mkdir(
        parents=True,
        exist_ok=True,
    )

    tool_commands = exp_manager.tool_connector().sh_commands(exp_manager.fs_managers())
    tool_bash_env_wrapper = tools_envs.ScriptWrapper.new(
        exp_manager.fs_managers().data().tool_env_script_sh(),
    )
    if isinstance(tool_bash_env_wrapper, tools_envs.MissingMagicCommentError):
        _LOGGER.error(tool_bash_env_wrapper)
        _LOGGER.critical("Cannot parse the tool environment wrapper script")
        raise typer.Exit(1)  # REFACTOR should use contexts instead of existing locally

    for script_path in (
        _init_env_script(sh_manager, tool_bash_env_wrapper),
        _command_script(sh_manager, tool_commands),
        _close_env_script(sh_manager, tool_bash_env_wrapper),
        _sbatch_script(exp_manager, sh_manager, samples_to_run, slurm_opts),
    ):
        _add_x_permissions(script_path)
        shutil.copy(script_path, sh_manager.data_sh_fs_manager().scripts_dir())

    return sh_manager


def _init_env_script(
    sh_manager: manager.Manager,
    tool_bash_env_wrapper: tools_envs.ScriptWrapper,
) -> Path:
    """Write the init environment script."""
    script_path = sh_manager.work_sh_fs_manager().step_script(
        exp_bash_items.Steps.INIT_ENV,
    )
    with script_path.open("w") as f_out:
        for line in tool_bash_env_wrapper.init_env_lines():
            f_out.write(line + "\n")
    return script_path


def _command_script(
    sh_manager: manager.Manager,
    tool_cmd: tool_bash.WithOptions,
) -> Path:
    """Write the command script (which `srun` will call)."""
    script_path = sh_manager.work_sh_fs_manager().step_script(
        exp_bash_items.Steps.COMMAND,
    )
    with script_path.open("w") as command_out:
        for line in _tool_command_script_lines(tool_cmd):
            command_out.write(line + "\n")
    return script_path


def _tool_command_script_lines(
    tool_cmd: tool_bash.WithOptions,
) -> Iterator[str]:
    """Return command lines."""
    yield bash_items.BASH_SHEBANG
    yield ""
    yield "set -e"  # exit error at the first command failing
    yield ""
    yield from tool_cmd.commands()


def _close_env_script(
    sh_manager: manager.Manager,
    tool_bash_env_wrapper: tools_envs.ScriptWrapper,
) -> Path:
    """Write the close environment script."""
    script_path = sh_manager.work_sh_fs_manager().step_script(
        exp_bash_items.Steps.CLOSE_ENV,
    )
    with script_path.open("w") as f_out:
        for line in tool_bash_env_wrapper.close_env_lines():
            f_out.write(line + "\n")
    return script_path


def _add_x_permissions(cmd_sh_path: Path) -> None:
    """Chmod +x the subscript (called by `srun`) for everyone."""
    st = cmd_sh_path.stat()
    cmd_sh_path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _sbatch_script(
    exp_manager: exp_managers.OnlyOptions | exp_managers.WithArguments,
    sh_manager: manager.Manager,
    samples_to_run: Iterable[smp.RowNumbered],
    slurm_opts: str,
) -> Path:
    """Write the sbatch script."""
    sbatch_script = sh_manager.work_sh_fs_manager().sbatch_script()
    with sbatch_script.open("w") as sbatch_out:
        for line in SbatchLinesBuilder.lines(
            slurm_opts,
            sh_manager,
            exp_manager.fs_managers().work(),
            samples_to_run,
        ):
            sbatch_out.write(line + "\n")
    return sbatch_script


class StepLinesBuilder:
    """Sbatch step lines builder."""

    @classmethod
    def set_step_ok_file(
        cls,
        work_exp_fs_manager: exp_fs.WorkManager,
        step: exp_bash_items.Steps,
    ) -> Iterator[str]:
        """Set step OK file variable."""
        yield bash_items.Variable(
            f"{step}_STEP_OK_FILE",
        ).set(
            bash_items.path_to_str(
                work_exp_fs_manager.slurm_log_fs_manager().script_step_status_file(
                    slurm_bash.SLURM_JOB_ID_FROM_VARS,
                    step,
                    exp_slurm_status.ScriptSteps.OK,
                ),
            ),
        )

    @classmethod
    def step_error_file(
        cls,
        work_exp_fs_manager: exp_fs.WorkManager,
        step: exp_bash_items.Steps,
    ) -> Iterator[str]:
        """Set step error file variable."""
        yield bash_items.Variable(
            f"{step}_STEP_ERROR_FILE",
        ).set(
            bash_items.path_to_str(
                work_exp_fs_manager.slurm_log_fs_manager().script_step_status_file(
                    slurm_bash.SLURM_JOB_ID_FROM_VARS,
                    step,
                    exp_slurm_status.ScriptSteps.ERROR,
                ),
            ),
        )

    @classmethod
    def set_script_path(
        cls,
        sh_manager: manager.Manager,
        step: exp_bash_items.Steps,
    ) -> Iterator[str]:
        """Set script path variable."""
        yield bash_items.Variable(f"{step}_SCRIPT").set(
            bash_items.path_to_str(
                sh_manager.work_sh_fs_manager().step_script(step),
            ),
        )


class SbatchLinesBuilder:
    """Sbatch lines builder."""

    TEMPLATE_SCRIPT = Path(__file__).parent / "sbatch_template.sh"

    PBFBENCH_DO_PREFIX = "# PBFBENCH_DO:"

    @classmethod
    def lines(
        cls,
        slurm_opts: str,
        sh_manager: manager.Manager,
        work_exp_fs_manager: exp_fs.WorkManager,
        samples_to_run: Iterable[smp.RowNumbered],
    ) -> Iterator[str]:
        """Return sbatch lines."""
        with cls.TEMPLATE_SCRIPT.open("r") as template_in:
            for line in template_in:
                pbfbench_do = cls._pbfbench_do(line)
                if pbfbench_do is None:
                    yield line.rstrip()
                else:
                    yield from cls._pbfbench_do_lines(
                        line,
                        pbfbench_do,
                        slurm_opts,
                        sh_manager,
                        work_exp_fs_manager,
                        samples_to_run,
                    )

    @classmethod
    def _pbfbench_do(cls, line: str) -> exp_bash_items.PbfbenchDo | None:
        """Return the PBFBENCH_DO comment if it is, otherwise None."""
        if line.startswith(cls.PBFBENCH_DO_PREFIX):
            pbfbench_do_str = line[len(cls.PBFBENCH_DO_PREFIX) :].rstrip().split(":")[0]
            return exp_bash_items.PbfbenchDo(pbfbench_do_str)
        return None

    @classmethod
    def _script_step(cls, line: str) -> exp_bash_items.Steps:
        """Return the script step if it is, otherwise None."""
        step_str = line[len(cls.PBFBENCH_DO_PREFIX) :].rstrip().split(":")[1]
        return exp_bash_items.Steps(step_str)

    @classmethod
    def _pbfbench_do_lines(  # noqa: PLR0913
        cls,
        line: str,
        pbfbench_do: exp_bash_items.PbfbenchDo,
        slurm_opts: str,
        sh_manager: manager.Manager,
        work_exp_fs_manager: exp_fs.WorkManager,
        samples_to_run: Iterable[smp.RowNumbered],
    ) -> Iterator[str]:
        """Return the lines for the PBFBENCH_DO comment."""
        match pbfbench_do:
            case exp_bash_items.PbfbenchDo.SBATCH_COMMENTS:
                return slurm_bash.SbatchCommentLinesBuilder.lines(
                    slurm_opts,
                    (sample.to_base_one() for sample in samples_to_run),
                    work_exp_fs_manager,
                )
            case exp_bash_items.PbfbenchDo.ARRAY_JOB_ID_FILE:
                return iter(
                    (
                        bash_items.Variable(pbfbench_do.value).set(
                            bash_items.path_to_str(
                                work_exp_fs_manager.slurm_log_fs_manager()
                                .job_id_file_manager()
                                .path(),
                            ),
                        ),
                    ),
                )
            case exp_bash_items.PbfbenchDo.STEP:
                step = cls._script_step(line)
                return chain(
                    StepLinesBuilder.set_script_path(sh_manager, step),
                    StepLinesBuilder.set_step_ok_file(work_exp_fs_manager, step),
                    StepLinesBuilder.step_error_file(work_exp_fs_manager, step),
                )
        assert_never(pbfbench_do)
