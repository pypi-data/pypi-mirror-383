# Copyright (c) 2025 Ping Guo
# Licensed under the MIT License


import abc
from abc import abstractmethod
from evotoolkit.core import Solution, BaseTask


class BaseMethodInterface(abc.ABC):
    """Base Adapter"""

    def __init__(self, task: BaseTask):
        self.task = task

    @abstractmethod
    def make_init_sol(self) -> Solution:
        """Create initial solution from task info."""
        raise NotImplementedError()

    @abstractmethod
    def parse_response(self, response_str: str) -> Solution:
        raise NotImplementedError()
