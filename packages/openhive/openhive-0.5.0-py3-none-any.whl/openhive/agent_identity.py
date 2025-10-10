import json
import uuid
from .agent_config import AgentConfig
from .agent_signature import AgentSignature
from .types import AgentMessageType


class AgentIdentity:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.private_key = config.keys['privateKey'].encode('utf-8')
        self.public_key = config.keys['publicKey'].encode('utf-8')

    @classmethod
    def create(cls, config: AgentConfig):
        return cls(config)

    def id(self) -> str:
        return self.config.id

    def name(self) -> str:
        return self.config.name
        
    def get_public_key_b64(self) -> str:
        return self.public_key.decode('utf-8')

    def _create_message(
        self,
        to_agent_id: str,
        msg_type: AgentMessageType,
        data: dict,
    ) -> dict:
        message_without_sig = {
            "from": self.id(),
            "to": to_agent_id,
            "type": msg_type.value,
            "data": data,
        }
        
        # Pydantic models need to be converted to dicts for JSON serialization
        # but here `data` is already a dict.
        # We need a stable JSON representation for signing.
        message_json = json.dumps(
            message_without_sig,
            sort_keys=True, 
            separators=(',', ':')
        ).encode('utf-8')
        
        signature = AgentSignature.sign(message_json, self.private_key)
        
        return {**message_without_sig, "sig": signature}

    def createTaskRequest(
        self,
        to_agent_id: str,
        capability: str,
        params: dict,
        task_id: str = None,
    ) -> dict:
        data = {
            "task_id": task_id or str(uuid.uuid4()),
            "capability": capability,
            "params": params,
        }
        return self._create_message(
            to_agent_id,
            AgentMessageType.TASK_REQUEST,
            data,
        )

    def createTaskResult(
        self,
        to_agent_id: str,
        task_id: str,
        result: dict,
    ) -> dict:
        data = {
            "task_id": task_id,
            "status": "completed",
            "result": result,
        }
        return self._create_message(
            to_agent_id,
            AgentMessageType.TASK_RESULT,
            data,
        )

    def createTaskError(
        self,
        to_agent_id: str,
        task_id: str,
        error: str,
        message: str,
        retry: bool,
    ) -> dict:
        data = {
            "task_id": task_id,
            "error": error,
            "message": message,
            "retry": retry,
        }
        return self._create_message(
            to_agent_id,
            AgentMessageType.TASK_ERROR,
            data,
        )

    def verify_message(
        self, message: dict, public_key: bytes,
    ) -> bool:
        message_copy = message.copy()
        signature = message_copy.pop("sig")

        message_json = (
            json.dumps(
                message_copy,
                sort_keys=True,
                separators=(',', ':'),
            ).encode('utf-8')
        )
        return AgentSignature.verify(
            message_json,
            signature,
            public_key,
        )
