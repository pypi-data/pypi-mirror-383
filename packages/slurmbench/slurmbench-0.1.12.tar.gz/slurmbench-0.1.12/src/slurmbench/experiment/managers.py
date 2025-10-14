"""Experiment managers."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import slurmbench.tool.connector as tool_connector

if TYPE_CHECKING:
    from . import file_system as exp_fs


class WithOptions[C: tool_connector.WithOptions]:
    """Experiment manager."""

    def __init__(
        self,
        exp_fs_managers: exp_fs.Managers,
        tool_connector: C,
    ) -> None:
        self._fs_managers = exp_fs_managers
        self._tool_connector = tool_connector

    def exp_name(self) -> str:
        """Get experiment name."""
        return self._fs_managers.data().experiment_name()

    def fs_managers(self) -> exp_fs.Managers:
        """Get experiment file system managers."""
        return self._fs_managers

    def tool_connector(self) -> C:
        """Get tool connector."""
        return self._tool_connector


@final
class OnlyOptions(WithOptions[tool_connector.OnlyOptions]):
    """Experiment manager with only options."""


@final
class WithArguments[N: tool_connector.Names](
    WithOptions[tool_connector.WithArguments[N]],
):
    """Experiment manager with arguments."""
