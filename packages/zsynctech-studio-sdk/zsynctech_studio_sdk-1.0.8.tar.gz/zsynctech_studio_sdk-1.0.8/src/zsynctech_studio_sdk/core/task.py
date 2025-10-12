from zsynctech_studio_sdk.core.context import get_client
from zsynctech_studio_sdk.core.loggers import get_logger
from zsynctech_studio_sdk.models.task import TaskModel
from zsynctech_studio_sdk.enums.task import TaskStatus
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.core.step import Step
from typing import Dict

logger = get_logger()


class Task:
    def __init__(self, description: str, execution_id: str, code: str):
        self.model = TaskModel(
            description=description,
            executionId=execution_id,
            code=code
        )
        self.steps: Dict[str, Step] = {}
        self._client = get_client()

    def step(self, step_code: str) -> Step:
        """Create or retrieve a step within the task.

        Args:
            step_code (str): Step code.

        Returns:
            Step: The created or retrieved step instance.
        """
        step = self.steps.get(step_code)
        if step is None:
            step = Step(
                step_code,
                task_id=self.model.id
            )
        self.steps[step_code] = step
        return step
    

    def __enter__(self) -> 'Task':
        """Mark the task as started.

        Returns:
            Task: The current task instance.
        """
        self.model.status = TaskStatus.RUNNING
        self.model.startDate = get_utc_now()
        self._client.post(
            url="tasks",
            json=self.model.model_dump()
        ).raise_for_status()
        logger.info(f"Task code: {self.model.code} iniciada")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Mark the task as completed or failed based on the presence of an exception.

        Args:
            exc_type (_type_): _type_ of the exception, if any.
            exc_val (_type_): _value_ of the exception, if any.
            exc_tb (_type_): _traceback_ of the exception, if any.

        Returns:
            bool: False to propagate the exception, True to suppress it.
        """
        if exc_type:
            self.model.status = TaskStatus.FAIL
            self.model.observation = str(exc_val)
            logger.error(f"Ocorreu um erro ao executar a task - {self.model.code}")
        else:
            self.model.status = TaskStatus.SUCCESS

        self.model.endDate = get_utc_now()

        self._client.post(
            url="tasks",
            json=self.model.model_dump()
        ).raise_for_status()

        logger.success(f"Task code: {self.model.code} finalizada com sucesso")
        
        return False