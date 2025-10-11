# -*- coding: utf-8 -*-

from __future__ import annotations

from multiprocessing.pool import Pool
from typing import List, Optional

from core_mixins.decorators import timer
from core_mixins.interfaces.task import ITask
from core_mixins.interfaces.task import TaskResult
from core_mixins.interfaces.task import TaskStatus


class TasksManager:
    """It manages the execution for the registered tasks"""

    def __init__(self, tasks: List[ITask]):
        self.tasks = tasks

    def execute(
        self,
        task_name: Optional[str] = None,
        parallelize: Optional[bool] = False,
        processes: Optional[int] = None,
    ) -> Optional[List[TaskResult] | TaskResult]:
        """
        Execute all registered tasks. An exception in one task should not
        stop the execution of the others...

        Example of results:

        .. code-block:: python

            [
                TaskResult(status=TaskStatus.SUCCESS, result=...),
                TaskResult(status=TaskStatus.ERROR, error=...)
            ]
        ..

        :param task_name: If defined, only that specific task will be executed.
        :type task_name: str
        :param parallelize: It defines if you want to execute the tasks in parallel.
        :type parallelize: bool
        :param processes: Number of parallel process.
        :type processes: int

        :return: The list of the execution results.
        :rtype: List[TaskResult]
        """

        if not self.tasks:
            return None

        if task_name:
            for task in self.tasks:
                if task_name == task.name:
                    return self._execute(task)

            raise Exception(f"Task [{task_name}] is not registered!")

        res = []
        if not parallelize:
            for task in self.tasks:
                res.append(self._execute(task))

        else:
            with Pool(processes=processes) as pool:
                res = pool.map(self._execute, self.tasks)

        return res

    @staticmethod
    def _execute(task: ITask) -> TaskResult:
        try:

            @timer
            def _execute():
                return task.execute()

            res, seconds = _execute()

            return TaskResult(
                status=TaskStatus.SUCCESS,
                execution_time=seconds,
                result=res,
            )

        except Exception as error:
            return TaskResult(
                status=TaskStatus.ERROR,
                error=error,
            )
