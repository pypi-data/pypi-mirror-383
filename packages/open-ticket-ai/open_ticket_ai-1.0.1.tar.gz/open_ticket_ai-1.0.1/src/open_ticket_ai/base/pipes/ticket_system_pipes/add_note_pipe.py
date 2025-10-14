from typing import Any

from pydantic import BaseModel

from open_ticket_ai.core.logging_iface import LoggerFactory
from open_ticket_ai.core.pipeline.pipe import ParamsModel, Pipe
from open_ticket_ai.core.pipeline.pipe_config import PipeConfig, PipeResult
from open_ticket_ai.core.ticket_system_integration.ticket_system_service import TicketSystemService
from open_ticket_ai.core.ticket_system_integration.unified_models import UnifiedNote


class AddNoteParams(ParamsModel):
    ticket_id: str | int
    note: UnifiedNote


class AddNotePipeResultData(BaseModel):
    note_added: bool


class AddNotePipeConfig(PipeConfig[AddNoteParams]):
    pass


class AddNotePipe(Pipe[AddNoteParams]):
    params_class = AddNoteParams

    def __init__(
        self,
        ticket_system: TicketSystemService,
        pipe_config: AddNotePipeConfig,
        logger_factory: LoggerFactory,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pipe_config, logger_factory=logger_factory)
        self.pipe_config = AddNotePipeConfig.model_validate(pipe_config.model_dump())
        self.ticket_system = ticket_system

    async def _process(self) -> PipeResult[AddNotePipeResultData]:
        try:
            ticket_id_str = str(self.params.ticket_id)
            success = await self.ticket_system.add_note(ticket_id_str, self.params.note)
            if not success:
                return PipeResult[AddNotePipeResultData](
                    success=False,
                    failed=True,
                    message="Failed to add note to ticket",
                    data=AddNotePipeResultData(note_added=False),
                )
            return PipeResult[AddNotePipeResultData](
                success=True, failed=False, data=AddNotePipeResultData(note_added=True)
            )
        except Exception as e:
            return PipeResult[AddNotePipeResultData](
                success=False, failed=True, message=str(e), data=AddNotePipeResultData(note_added=False)
            )
