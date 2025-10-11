from zsynctech_studio_sdk.core.context import get_client, INSTANCE_ID, SDK_DIR, ENCRYPTION_KEY
from zsynctech_studio_sdk.models.config import ExecutionSettings, CredentialModel
from zsynctech_studio_sdk.core.errors import ExecutionFinishedError
from zsynctech_studio_sdk.models.execution import ExecutionModel
from zsynctech_studio_sdk.enums.execution import ExecutionStatus
from zsynctech_studio_sdk.core.loggers import get_logger
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.core.task import Task
from zsynctech_studio_sdk.utils import decrypt
from typing import Optional, Dict, List
from cachelib import FileSystemCache
from uuid_extensions import uuid7
from functools import wraps
import json
import os


EXECUTION_FINISHED_STATUS = [
    ExecutionStatus.OUT_OF_OPERATING_HOURS,
    ExecutionStatus.INTERRUPTED,
    ExecutionStatus.FINISHED,
    ExecutionStatus.ERROR,
]


logger = get_logger()


def is_a_finished_execution(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.model.status in EXECUTION_FINISHED_STATUS:
            raise ExecutionFinishedError(
                f"Cannot perform '{method.__name__}' "
                f"on a finished execution with status '{self.model.status.value}'."
            )
        return method(self, *args, **kwargs)
    return wrapper

def send_execution(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if self.model.status in EXECUTION_FINISHED_STATUS:
            self.model.endDate = get_utc_now()
        self._client.post(
            url="executions",
            json=self.model.model_dump()
        ).raise_for_status()
        return result
    return wrapper


class Execution:
    def __init__(self) -> None:
        self.model = ExecutionModel()
        self._client = get_client()
        self._cache = FileSystemCache(
            cache_dir=os.path.join(SDK_DIR, INSTANCE_ID.get()),
            default_timeout=0
        )
        self._settings: Optional[ExecutionSettings] = None
    
    @property
    def settings(self):
        return self._settings

    def task(
            self,
            code: Optional[str] = str(uuid7()),
            description: Optional[str] = "Não informado"
        ) -> Task:
        """Create a new task within the execution.

        Args:
            code (Optional[str], optional): Taks code. Defaults to str(uuid7()).
            description (Optional[str], optional): Text description. Defaults to "Não informado".

        Returns:
            Task: The created task instance.
        """
        task = Task(
            description,
            execution_id=self.model.id,
            code=code
        )
        return task

    @staticmethod
    def decrypt_credentials(credentials: Optional[List[CredentialModel]]) -> Optional[Dict[str, str]]:
        """Decrypts credentials and returns them as a dictionary {key: value}.

        Args:
            credentials (Optional[List[Credential]]): A list of Credential objects, or None.

        Returns:
            Optional[Dict[str, str]]: A dictionary with decrypted values, or None if no credentials are provided.
        """
        if credentials is None:
            return None

        decrypted_dict: Dict[str, str] = {}
        for cred in credentials:
            if cred.encrypted:
                decrypted_dict[cred.key] = decrypt(cred.value, ENCRYPTION_KEY.get())
            else:
                decrypted_dict[cred.key] = cred.value

        return decrypted_dict

    @send_execution
    @is_a_finished_execution
    def start(self, observation: Optional[str] = "Execução iniciada") -> 'Execution':
        """Mark the execution as started.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to None.

        Returns:
            Execution: The current execution instance.
        """
        self.model.observation = observation
        self.model.status = ExecutionStatus.RUNNING
        logger.info(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def finish(self, observation: Optional[str] = "Execução finalizada com sucesso") -> 'Execution':
        """Mark the execution as finish.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to None.

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.FINISHED
        self.model.observation = observation
        logger.success(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def out_of_operating_hours(self, observation: Optional[str] = "Fora do horário de execução") -> 'Execution':
        """Mark the execution as out of operating hours.

        Args:
            observation (Optional[str], optional): Observation text. Defaults to "Fora do horário de execução".

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.OUT_OF_OPERATING_HOURS
        self.model.observation = observation
        logger.error(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def error(self, observation: Optional[str] = "Ocorreu um erro na execução") -> 'Execution':
        """Mark the execution as finish.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.ERROR
        self.model.observation = observation
        logger.error(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def interrupted(self, observation: Optional[str] = "Operação interrompida pelo sistema") -> 'Execution':
        """Mark the execution as interrupted.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.OUT_OF_OPERATING_HOURS
        self.model.observation = observation
        logger.error(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def waiting(self, observation: Optional[str] = "Execução em espera") -> 'Execution':
        """Mark the execution as waiting.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.WAITING
        self.model.observation = observation
        logger.info(self.model.observation)
        return self

    @send_execution
    @is_a_finished_execution
    def scheduled(self, observation: Optional[str] = "Execução agendada para o próximo horário disponível") -> 'Execution':
        """Mark the execution as scheduled.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.status = ExecutionStatus.SCHEDULED
        self.model.observation = observation
        logger.info(self.model.observation)
        return self

    @send_execution
    def increment_task_count(self) -> 'Execution':
        """Increment the current task count by one.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        if self.model.totalTaskCount == 0 or self.model.currentTaskCount >= self.model.totalTaskCount:
            self.model.totalTaskCount += 1
        self.model.currentTaskCount = self.model.currentTaskCount + 1
        logger.info(f"Processado {self.model.currentTaskCount} de {self.model.totalTaskCount}")
        return self

    @send_execution
    def update_current_task_count(self, current_task_count: int) -> 'Execution':
        """Update the current task count to a specific value.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.currentTaskCount = current_task_count
        logger.info(f"Processado {self.model.currentTaskCount} de {self.model.totalTaskCount}")
        return self

    @send_execution
    def set_total_task_count(self, total_task_count: int) -> 'Execution':
        """Set the total task count to a specific value.

        Args:
            observation: str Observation text.

        Returns:
            Execution: The current execution instance.
        """
        self.model.totalTaskCount = total_task_count
        logger.info(f"Total de tasks a processar: {self.model.totalTaskCount}")
        return self

    def __get_latest_instance_file(self) -> Optional[str]:
        """Gets the latest instance file path based on modification time.
        Args:

        Returns:
            Optional[str]: The path to the latest instance file, or None if not found.
        """
        candidates = [
            os.path.join(SDK_DIR, f)
            for f in os.listdir(SDK_DIR)
            if f.endswith(".json") and f.startswith(INSTANCE_ID.get())
        ]
        if not candidates:
            return None
        return max(candidates, key=os.path.getmtime)

    def get_next_execution(self) -> Optional[ExecutionSettings]:
        """Gets the next execution settings from the latest instance file.

        Returns:
            Optional[ExecutionSettings]: Execution settings
        """
        cached = self._cache.get("settings")

        latest_file = self.__get_latest_instance_file()
        if not latest_file:
            logger.info("Sem atualizações")
            return None

        current_mtime = os.path.getmtime(latest_file)

        if cached and cached["path"] == latest_file and cached["mtime"] == current_mtime:
            logger.info("Sem atualizações")
            return None

        try:
            with open(latest_file, mode="r", encoding="utf8") as file:
                data = json.load(file)
        except Exception as e:
            logger.exception(e)
            return None

        self.model.id = data["executionId"]

        new_cache = {
            "path": latest_file,
            "mtime": current_mtime,
            "data": data
        }
        self._cache.set("settings", new_cache)

        self._settings = ExecutionSettings(**data)

        logger.info(f"Execução iniciada - {self._settings.executionId}")

        return self._settings

    def get_last_execution(self) -> Optional[ExecutionSettings]:
        """Gets the last execution settings from the cache.

        Returns:
            Optional[ExecutionSettings]: Execution settings
        """
        cached = self._cache.get("settings")
        if not cached:
            return None

        if "data" in cached:
            data = cached["data"]
            self.model.id = data["executionId"]
            self._settings = ExecutionSettings(**data)
            logger.info(f"Última execução (cache): {self._settings.executionId}")
            return self._settings

        try:
            with open(cached["path"], mode="r", encoding="utf8") as file:
                data = json.load(file)
        except Exception:
            return None

        self.model.id = data["executionId"]
        cached["data"] = data
        self._cache.set("settings", cached)

        self._settings = ExecutionSettings(**data)

        logger.info(f"Última execução: {self._settings.executionId}")

        return self._settings