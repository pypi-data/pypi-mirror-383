from abc import abstractmethod
from typing import Any

from .stage_interface import StageInterface as ImplementsInterface
from .types import T_in, T_out


class Stage(
    ImplementsInterface[T_in, T_out],
):
    @abstractmethod
    async def __call__(
        self,
        payload: T_in,
        /,  # Make 'payload' a positional-only parameter
        *args: Any,
        **kwds: Any,
    ) -> T_out:
        """
        Runs the stage.
        """
        pass
