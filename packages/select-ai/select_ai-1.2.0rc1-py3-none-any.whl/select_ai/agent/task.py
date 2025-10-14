# -----------------------------------------------------------------------------
# Copyright (c) 2025, Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# http://oss.oracle.com/licenses/upl.
# -----------------------------------------------------------------------------

import json
from abc import ABC
from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Iterator,
    List,
    Mapping,
    Optional,
    Union,
)

import oracledb

from select_ai import BaseProfile
from select_ai._abc import SelectAIDataClass
from select_ai._enums import StrEnum
from select_ai.agent.sql import (
    GET_USER_AI_AGENT_TASK,
    GET_USER_AI_AGENT_TASK_ATTRIBUTES,
    LIST_USER_AI_AGENT_TASKS,
)
from select_ai.async_profile import AsyncProfile
from select_ai.db import async_cursor, cursor
from select_ai.errors import AgentTaskNotFoundError
from select_ai.profile import Profile


@dataclass
class TaskAttributes(SelectAIDataClass):
    """AI Task attributes

    :param str instruction: Statement describing what the task is
     meant to accomplish

    :param List[str] tools: List of tools the agent can use to
     execute the task

    :param str input: Task name whose output will be automatically
     provided by select ai to LLM

    :param bool enable_human_tool: Enable agent to ask question
     to user when it requires information or clarification
     during a task. Default value is True.

    """

    instruction: str
    tools: Optional[List[str]] = None
    input: Optional[str] = None
    enable_human_tool: Optional[bool] = True


class BaseTask(ABC):

    def __init__(
        self,
        task_name: Optional[str] = None,
        description: Optional[str] = None,
        attributes: Optional[TaskAttributes] = None,
    ):
        if attributes and not isinstance(attributes, TaskAttributes):
            raise TypeError(
                "'attributes' must be an object of type "
                "select_ai.agent.TaskAttributes"
            )
        self.task_name = task_name
        self.description = description
        self.attributes = attributes

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"task_name={self.task_name}, "
            f"attributes={self.attributes}, description={self.description})"
        )


class Task(BaseTask):
    """
    select_ai.agent.Task class lets you create, delete, enable, disable and
    list AI Tasks

    :param str task_name: The name of the AI task
    :param str description: Optional description of the AI task
    :param select_ai.agent.TaskAttributes attributes: AI task attributes

    """

    @staticmethod
    def _get_attributes(task_name: str) -> TaskAttributes:
        with cursor() as cr:
            cr.execute(
                GET_USER_AI_AGENT_TASK_ATTRIBUTES, task_name=task_name.upper()
            )
            attributes = cr.fetchall()
            if attributes:
                post_processed_attributes = {}
                for k, v in attributes:
                    if isinstance(v, oracledb.LOB):
                        post_processed_attributes[k] = v.read()
                    else:
                        post_processed_attributes[k] = v
                return TaskAttributes(**post_processed_attributes)
            else:
                raise AgentTaskNotFoundError(task_name=task_name)

    def create(
        self, enabled: Optional[bool] = True, replace: Optional[bool] = False
    ):
        """
        Create a task that a Select AI agent can include in its
        reasoning process

        :param bool enabled: Whether the AI Task should be enabled.
         Default value is True.

        :param bool replace: Whether the AI Task should be replaced.
         Default value is False.

        """
        if self.task_name is None:
            raise AttributeError("Task must have a name")
        if self.attributes is None:
            raise AttributeError("Task must have attributes")

        parameters = {
            "task_name": self.task_name,
            "attributes": self.attributes.json(),
        }

        if self.description:
            parameters["description"] = self.description

        if not enabled:
            parameters["status"] = "disabled"

        with cursor() as cr:
            try:
                cr.callproc(
                    "DBMS_CLOUD_AI_AGENT.CREATE_TASK",
                    keyword_parameters=parameters,
                )
            except oracledb.Error as err:
                (err_obj,) = err.args
                if err_obj.code in (20051, 20052) and replace:
                    self.delete(force=True)
                    cr.callproc(
                        "DBMS_CLOUD_AI_AGENT.CREATE_TASK",
                        keyword_parameters=parameters,
                    )
                else:
                    raise

    def delete(self, force: bool = False):
        """
        Delete AI Task from the database

        :param bool force: Force the deletion. Default value is False.
        """
        with cursor() as cr:
            cr.callproc(
                "DBMS_CLOUD_AI_AGENT.DROP_TASK",
                keyword_parameters={
                    "task_name": self.task_name,
                    "force": force,
                },
            )

    def disable(self):
        """
        Disable AI Task
        """
        pass

    def enable(self):
        """
        Enable AI Task
        """
        pass

    @classmethod
    def list(cls, task_name_pattern: Optional[str] = ".*") -> Iterator["Task"]:
        """List AI Tasks

        :param str task_name_pattern: Regular expressions can be used
         to specify a pattern. Function REGEXP_LIKE is used to perform the
         match. Default value is ".*" i.e. match all tasks.

        :return: Iterator[Task]
        """
        with cursor() as cr:
            cr.execute(
                LIST_USER_AI_AGENT_TASKS,
                task_name_pattern=task_name_pattern,
            )
            for row in cr.fetchall():
                task_name = row[0]
                if row[1]:
                    description = row[1].read()  # Oracle.LOB
                else:
                    description = None
                attributes = cls._get_attributes(task_name=task_name)
                yield cls(
                    task_name=task_name,
                    description=description,
                    attributes=attributes,
                )

    @classmethod
    def fetch(cls, task_name: str) -> "Task":
        """
        Fetch AI Task attributes from the Database and build a proxy object in
        the Python layer

        :param str task_name: The name of the AI Task

        :return: select_ai.agent.Task

        :raises select_ai.errors.AgentTaskNotFoundError:
         If the AI Task is not found
        """
        pass

    def set_attributes(self, attributes: TaskAttributes):
        """
        Set AI Task attributes
        """
        pass

    def set_attribute(self, attribute_name: str, attribute_value: Any):
        """
        Set a single AI Task attribute specified using name and value
        """
        pass


class AsyncTask(BaseTask):
    pass
