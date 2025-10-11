# -*- coding: utf-8 -*-

"""
This module provides a base implementation for ETL tasks
under the project ecosystem.
"""

from abc import ABC, abstractmethod
from enum import Enum
from logging import Logger
from typing import Any, Optional

from core_mixins.interfaces.factory import IFactory


class TaskStatus(str, Enum):
    """Possible status a task can have during its life"""

    CREATED = "CREATED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ITask(IFactory, ABC):
    """Base implementations for different tasks/processes"""

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._name = name
        self.description = description
        self._status = TaskStatus.CREATED
        self.logger = logger

    @classmethod
    def registration_key(cls) -> str:
        """It returns the key used to register the class"""
        return cls.__name__

    @property
    def name(self):
        """It returns the task identification"""
        return self._name or self.registration_key()

    @property
    def status(self) -> TaskStatus:
        """It returns the current status of the task"""
        return self._status

    @status.setter
    def status(self, status: TaskStatus) -> None:
        self._status = status

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """You must implement the task's process"""

    def info(self, message) -> None:
        """Log entry with severity 'INFO'"""

        if self.logger:
            self.logger.info(f"{self.name} | {message}")

    def warning(self, message) -> None:
        """Log entry with severity 'WARNING'"""

        if self.logger:
            self.logger.warning(f"{self.name} | {message}")

    def error(self, error) -> None:
        """Log entry with severity 'ERROR'"""

        if self.logger:
            self.logger.error(f"{self.name} | {error}")


class TaskResult:
    """
    Represents the result of a task execution that
    exposes `status`, `result`, or the error.
    """

    def __init__(
        self,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[Exception] = None,
        execution_time: float = 0.0,
    ) -> None:
        self.status = status
        self.execution_time = execution_time
        self.result = result
        self.error = error

    def __repr__(self) -> str:
        if self.status == TaskStatus.SUCCESS:
            return f"TaskResult(status={self.status}, result={self.result})"

        if self.status == TaskStatus.ERROR:
            return f"TaskResult(status={self.status}, error={self.error})"

        return f"TaskResult(status={self.status})"

    @property
    def is_success(self) -> bool:
        """Check if the task execution was successful"""
        return self.status == TaskStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        """Check if the task execution failed"""
        return self.status == TaskStatus.ERROR


class TaskException(Exception):
    """Custom exception for Tasks"""
