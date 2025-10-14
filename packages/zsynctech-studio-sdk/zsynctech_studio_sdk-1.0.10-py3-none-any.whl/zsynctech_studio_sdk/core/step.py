from zsynctech_studio_sdk.core.context import get_client, INSTANCE_ID
from zsynctech_studio_sdk.core.loggers import get_logger
from zsynctech_studio_sdk.models.step import StepModel
from zsynctech_studio_sdk.enums.step import StepStatus
from zsynctech_studio_sdk.utils import get_utc_now
from typing import Optional
from functools import wraps


STEP_FINALIZED_STATUS = [
    StepStatus.SUCCESS,
    StepStatus.FAIL
]

logger = get_logger()

def send_step(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if self.model.status in STEP_FINALIZED_STATUS:
            self.model.endDate = get_utc_now(1)
        self._client.post(
            url="taskSteps",
            json=self.model.model_dump()
        ).raise_for_status()
        return result
    return wrapper


class Step:
    def __init__(self, step_code: str, task_id: str):
        self.model = StepModel(
            stepCode=step_code,
            automationOnClientId=INSTANCE_ID.get(),
            taskId=task_id,
            status=StepStatus.UNPROCESSED
        )
        self._client = get_client()

    @send_step
    def start(self, observation: Optional[str] = "Step iniciado") -> 'Step':
        """Mark the step as started.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to "Step iniciado".

        Returns:
            Step: The current step instance.
        """
        self.model.status = StepStatus.RUNNING
        self.model.startDate = get_utc_now()
        self.model.observation = observation
        logger.info(f"Step code: {self.model.stepCode} - Observation: {self.model.observation}")
        return self

    @send_step
    def success(self, observation: Optional[str] = "Step finalizado com sucesso") -> 'Step':
        """Mark the step as success.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to "Step iniciado".

        Returns:
            Step: The current step instance.
        """
        self.model.status = StepStatus.SUCCESS
        self.model.observation = observation
        logger.success(f"Step code: {self.model.stepCode} - Observation: {self.model.observation}")
        return self

    @send_step
    def error(self, observation: Optional[str] = "Ocorreu um erro no step") -> 'Step':
        """Mark the step as fail.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to "Ocorreu um erro no step".

        Returns:
            Step: The current step instance.
        """
        self.model.status = StepStatus.FAIL
        self.model.observation = observation
        logger.error(f"Step code: {self.model.stepCode} - Observation: {self.model.observation}")
        return self