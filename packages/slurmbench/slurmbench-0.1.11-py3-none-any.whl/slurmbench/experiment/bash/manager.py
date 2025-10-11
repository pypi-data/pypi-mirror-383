"""Experiment bash manager."""

from __future__ import annotations

from typing import TYPE_CHECKING

import slurmbench.experiment.in_progress as exp_in_progress
import slurmbench.experiment.managers as exp_managers

if TYPE_CHECKING:
    from . import file_system as fs


class Manager:
    """Experiment bash manager."""

    @classmethod
    def from_exp_fs_manager(
        cls,
        exp_fs_manager: exp_managers.OnlyOptions | exp_managers.WithArguments,
    ) -> Manager:
        """Initialize from experiment file system manager."""
        date_str = exp_in_progress.get_today_format_string()
        return cls(
            date_str,
            exp_fs_manager.fs_managers().data().scripts_fs_manager(date_str),
            exp_fs_manager.fs_managers().work().scripts_fs_manager(date_str),
        )

    def __init__(
        self,
        date_str: str,
        data_sh_fs_manager: fs.Manager,
        work_sh_fs_manager: fs.Manager,
    ) -> None:
        self.__date_str = date_str
        self.__data_sh_fs_manager = data_sh_fs_manager
        self.__work_sh_fs_manager = work_sh_fs_manager

    def date_str(self) -> str:
        """Get date string."""
        return self.__date_str

    def data_sh_fs_manager(self) -> fs.Manager:
        """Get data shell file system manager."""
        return self.__data_sh_fs_manager

    def work_sh_fs_manager(self) -> fs.Manager:
        """Get working shell file system manager."""
        return self.__work_sh_fs_manager
