# Copyright (c) 2025 Ping Guo
# Licensed under the MIT License


from abc import ABC, abstractmethod
from typing import List
from evotool.core import Solution, BaseTask
from .base_method_interface import BaseMethodInterface



class FunSearchInterface(BaseMethodInterface):
    """Base adapter for FunSearch algorithm"""

    def __init__(self, task: BaseTask):
        super().__init__(task)

    def make_init_sol(self) -> Solution:
        return self.task.make_init_sol_wo_other_info()
    
    @abstractmethod
    def get_prompt(self, solutions: List[Solution]) -> List[dict]:
        """Generate prompt based on multiple solutions"""
        pass
