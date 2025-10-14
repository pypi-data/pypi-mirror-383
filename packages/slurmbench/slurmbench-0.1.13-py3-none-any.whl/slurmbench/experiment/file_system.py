"""Experiment input/output logics."""

from __future__ import annotations

from pathlib import Path
from typing import Self, final

import slurmbench.samples.file_system as smp_fs
import slurmbench.samples.items as smp
import slurmbench.tool.description as tool_desc

from .bash import file_system as exp_bash_fs
from .slurm import file_system as exp_slurm_fs


class ManagerBase:
    """Experiment file system manager base."""

    CONFIG_YAML_NAME = Path("config.yaml")
    IN_PROGRESS_YAML_NAME = Path("in_progress.yaml")

    SCRIPT_DIR_NAME = Path("scripts")

    def __init__(
        self,
        root_directory_path: Path,
        tool_description: tool_desc.Description,
        experiment_name: str,
    ) -> None:
        """Initialize."""
        self._root_directory_path = root_directory_path
        self._tool_description = tool_description
        self._experiment_name = experiment_name

    def tool_description(self) -> tool_desc.Description:
        """Get tool description."""
        return self._tool_description

    def experiment_name(self) -> str:
        """Get experiment name."""
        return self._experiment_name

    def root_dir(self) -> Path:
        """Get root directory path."""
        return self._root_directory_path

    def topic_dir(self) -> Path:
        """Get topic directory path."""
        return self._root_directory_path / self._tool_description.topic().name()

    def tool_dir(self) -> Path:
        """Get tool directory path."""
        return self.topic_dir() / self._tool_description.name()

    def exp_dir(self) -> Path:
        """Get experiment directory path."""
        return self.tool_dir() / self._experiment_name

    #
    # Experiment files
    #
    def config_yaml(self) -> Path:
        """Get config file."""
        return self.exp_dir() / self.CONFIG_YAML_NAME

    def in_progress_yaml(self) -> Path:
        """Get in progress file."""
        return self.exp_dir() / self.IN_PROGRESS_YAML_NAME

    #
    # Sbatch scripts
    #
    def scripts_fs_manager(self, date_str: str) -> exp_bash_fs.Manager:
        """Get experiment scripts file system manager."""
        return exp_bash_fs.Manager(self.exp_dir() / self.SCRIPT_DIR_NAME, date_str)

    #
    # Sample experiment directories
    #
    def sample_dir(self, sample_dirname: str | Path) -> Path:
        """Get sample experiment directory path."""
        return self.exp_dir() / sample_dirname

    def sample_fs_manager(self, sample: smp.RowNumbered) -> smp_fs.Manager:
        """Get sample experiment directory path."""
        return smp_fs.Manager.from_exp_dir_and_sample(self.exp_dir(), sample)


@final
class DataManager(ManagerBase):
    """Data experiment manager."""

    SAMPLES_TSV_NAME = Path("samples.tsv")

    TOOL_ENV_WRAPPER_SCRIPT_NAME = Path("env_wrapper.sh")

    ERRORS_TSV_NAME = Path("errors.tsv")
    HISTORY_YAML_NAME = Path("history.yaml")

    def samples_tsv(self) -> Path:
        """Get samples TSV file."""
        return self.root_dir() / self.SAMPLES_TSV_NAME

    def tool_env_script_sh(self) -> Path:
        """Get tool environment script file."""
        return self.tool_dir() / self.TOOL_ENV_WRAPPER_SCRIPT_NAME

    def errors_tsv(self) -> Path:
        """Get errors file."""
        return self.exp_dir() / self.ERRORS_TSV_NAME

    def history_yaml(self) -> Path:
        """Get history file."""
        return self.exp_dir() / self.HISTORY_YAML_NAME


@final
class WorkManager(ManagerBase):
    """Work experiment manager."""

    UNRESOLVED_SAMPLES_TSV_NAME = Path("unresolved_samples.tsv")
    RESOLVED_SAMPLES_TSV_NAME = Path("resolved_samples.tsv")

    TMP_SLURM_LOG_DIR_NAME = Path("logs")

    def __init__(
        self,
        root_directory_path: Path,
        tool_description: tool_desc.Description,
        experiment_name: str,
    ) -> None:
        super().__init__(root_directory_path, tool_description, experiment_name)
        self.__slurm_log_fs_manager = exp_slurm_fs.LogsManager(
            self.exp_dir() / self.TMP_SLURM_LOG_DIR_NAME,
        )

    def unresolved_samples_tsv(self) -> Path:
        """Get unresolved samples TSV file."""
        return self.exp_dir() / self.UNRESOLVED_SAMPLES_TSV_NAME

    def resolved_samples_tsv(self) -> Path:
        """Get resolved samples TSV file."""
        return self.exp_dir() / self.RESOLVED_SAMPLES_TSV_NAME

    #
    # Tmp sbatch logs
    #
    def slurm_log_fs_manager(self) -> exp_slurm_fs.LogsManager:
        """Get slurm logs manager."""
        return self.__slurm_log_fs_manager


class Managers:
    """Experiment file system managers."""

    @classmethod
    def new(
        cls,
        data_dir: Path,
        work_dir: Path,
        tool_description: tool_desc.Description,
        experiment_name: str,
    ) -> Self:
        """Create new experiment file system managers."""
        return cls(
            DataManager(data_dir, tool_description, experiment_name),
            WorkManager(work_dir, tool_description, experiment_name),
        )

    def __init__(
        self,
        data_fs_manager: DataManager,
        work_fs_manager: WorkManager,
    ) -> None:
        self._data_fs_manager = data_fs_manager
        self._work_fs_manager = work_fs_manager

    def data(self) -> DataManager:
        """Get experiment data file system manager."""
        return self._data_fs_manager

    def work(self) -> WorkManager:
        """Get experiment working file system manager."""
        return self._work_fs_manager
