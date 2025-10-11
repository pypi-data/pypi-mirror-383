
from typing import Any, Dict, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient


class ConversationService:
    """
    Wrapper for conversation endpoints. Handles creation, listing, restoration,
    and bulk message management in accordance with
    ``app/blueprints/conversation/routes.py``.
    """

    def __init__(self, client: KnowrithmClient):
        self.client = client

    def create_conversation(
        self,
        agent_id: str,
        *,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_context_length: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a conversation scoped to the authenticated entity.

        Endpoint:
            ``POST /v1/conversation`` - requires ``write`` scope or JWT.
        """
        payload: Dict[str, Any] = {"agent_id": agent_id}
        if title is not None:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        if max_context_length is not None:
            payload["max_context_length"] = max_context_length
        return self.client._make_request("POST", "/conversation", data=payload, headers=headers)

    def list_conversations(
        self,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        List active company conversations.

        Endpoint:
            ``GET /v1/conversation`` - requires ``read`` scope or JWT.
        """
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self.client._make_request("GET", "/conversation", params=params or None, headers=headers)

    def list_conversations_for_entity(
        self,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        List conversations for the currently authenticated entity (user or lead).

        Endpoint:
            ``GET /v1/conversation/entity`` - requires ``read`` scope or JWT.
        """
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self.client._make_request("GET", "/conversation/entity", params=params or None, headers=headers)

    def list_deleted_conversations(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        List soft-deleted conversations.

        Endpoint:
            ``GET /v1/conversation/deleted`` - requires read scope.
        """
        return self.client._make_request("GET", "/conversation/deleted", headers=headers)

    def list_conversation_messages(
        self,
        conversation_id: str,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve paginated messages for a conversation.

        Endpoint:
            ``GET /v1/conversation/<conversation_id>/messages`` - requires read scope.
        """
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self.client._make_request(
            "GET",
            f"/conversation/{conversation_id}/messages",
            params=params or None,
            headers=headers,
        )

    def delete_conversation(self, conversation_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Soft-delete a conversation and its messages.

        Endpoint:
            ``DELETE /v1/conversation/<conversation_id>`` - requires write scope.
        """
        return self.client._make_request("DELETE", f"/conversation/{conversation_id}", headers=headers)

    def delete_conversation_messages(
        self,
        conversation_id: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Soft-delete every message in a conversation.

        Endpoint:
            ``DELETE /v1/conversation/<conversation_id>/messages`` - requires write scope.
        """
        return self.client._make_request(
            "DELETE",
            f"/conversation/{conversation_id}/messages",
            headers=headers,
        )

    def restore_conversation(self, conversation_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Restore a soft-deleted conversation.

        Endpoint:
            ``PATCH /v1/conversation/<conversation_id>/restore`` - requires write scope.
        """
        return self.client._make_request(
            "PATCH",
            f"/conversation/{conversation_id}/restore",
            headers=headers,
        )

    def restore_all_messages(
        self,
        conversation_id: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Restore every message within a conversation in a single call.

        Endpoint:
            ``PATCH /v1/conversation/<conversation_id>/message/restore-all`` - requires write scope.
        """
        return self.client._make_request(
            "PATCH",
            f"/conversation/{conversation_id}/message/restore-all",
            headers=headers,
        )


class MessageService:
    """
    Conversation message helper mirroring message-specific endpoints.
    """

    def __init__(self, client: KnowrithmClient):
        self.client = client

    def send_message(
        self,
        conversation_id: str,
        message: str,
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message and receive the AI reply.

        Endpoint:
            ``POST /v1/conversation/<conversation_id>/chat`` - requires write scope or JWT.
        """
        payload = {"message": message}
        return self.client._make_request("POST", f"/conversation/{conversation_id}/chat", data=payload, headers=headers)

    def delete_message(self, message_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Soft-delete a single message.

        Endpoint:
            ``DELETE /v1/message/<message_id>`` - requires write scope.
        """
        return self.client._make_request("DELETE", f"/message/{message_id}", headers=headers)

    def restore_message(self, message_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Restore a soft-deleted message.

        Endpoint:
            ``PATCH /v1/message/<message_id>/restore`` - requires write scope.
        """
        return self.client._make_request("PATCH", f"/message/{message_id}/restore", headers=headers)

    def list_deleted_messages(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        List soft-deleted messages for the company.

        Endpoint:
            ``GET /v1/message/deleted`` - requires read scope.
        """
        return self.client._make_request("GET", "/message/deleted", headers=headers)
