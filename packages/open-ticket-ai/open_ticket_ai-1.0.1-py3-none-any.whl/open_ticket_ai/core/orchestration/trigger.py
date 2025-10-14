import asyncio
from abc import ABC, abstractmethod
from typing import Any, Protocol

from pydantic import BaseModel

from open_ticket_ai.core.config.renderable import Renderable
from open_ticket_ai.core.logging_iface import LoggerFactory
from open_ticket_ai.core.orchestration.orchestrator_config import TriggerDefinition


class PipeRunnerObserver(Protocol):
    async def on_trigger_fired(self) -> None: ...


class Trigger[ParamsT: BaseModel](Renderable, ABC):
    params_class: type[ParamsT]

    def __init__(
        self,
        config: TriggerDefinition[ParamsT],
        logger_factory: LoggerFactory,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.trigger_def = config
        self._observers: list[PipeRunnerObserver] = []
        self._running = False
        self._logger = logger_factory.get_logger(self.__class__.__name__)

        if isinstance(config.params, dict):
            self.params: ParamsT = self.params_class.model_validate(config.params)
        else:
            self.params: ParamsT = config.params

    def attach(self, observer: PipeRunnerObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: PipeRunnerObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> None:
        for obs in self._observers:
            asyncio.create_task(obs.on_trigger_fired())

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
