
from typing import Any, Dict, List, Optional

from knowrithm_py.knowrithm.client import KnowrithmClient


class AgentService:
    """
    Thin wrapper around ``app/blueprints/agent/routes.py`` endpoints. Provides a
    typed, well documented interface for creating and managing Knowrithm agents.
    """

    def __init__(self, client: KnowrithmClient):
        self.client = client

    def create_agent(
        self,
        payload: Dict[str, Any],
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new agent bound to the authenticated company and optional LLM settings.

        Endpoint:
            ``POST /v1/agent`` - requires API key scope ``write`` or JWT with equivalent rights.

        Payload:
            Must include ``name``; may include ``description``, ``avatar_url``,
            ``llm_settings_id``, ``personality_traits``, ``capabilities``,
            ``operating_hours``, ``languages``, ``status`` (see README).
        """
        return self.client._make_request("POST", "/agent", data=payload, headers=headers)

    def get_agent(self, agent_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retrieve agent details by identifier (public endpoint).

        Endpoint:
            ``GET /v1/agent/<agent_id>`` - no authentication required.
        """
        return self.client._make_request("GET", f"/agent/{agent_id}", headers=headers)

    def list_agents(
        self,
        *,
        company_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        List agents that belong to the current company or to a specific company
        for super admins.

        Endpoint:
            ``GET /v1/agent`` - requires ``read`` scope or a JWT.

        Query parameters:
            ``company_id`` (super admins), ``status``, ``search``, ``page``, ``per_page``.
        """
        params: Dict[str, Any] = {}
        if company_id is not None:
            params["company_id"] = company_id
        if status is not None:
            params["status"] = status
        if search is not None:
            params["search"] = search
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self.client._make_request("GET", "/agent", params=params or None, headers=headers)

    def update_agent(
        self,
        agent_id: str,
        payload: Dict[str, Any],
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Replace an agent's metadata and associated LLM settings.

        Endpoint:
            ``PUT /v1/agent/<agent_id>`` - requires ``write`` scope or JWT.
        """
        return self.client._make_request("PUT", f"/agent/{agent_id}", data=payload, headers=headers)

    def delete_agent(self, agent_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Soft-delete an agent (must have no active conversations).

        Endpoint:
            ``DELETE /v1/agent/<agent_id>`` - requires agent write permissions.
        """
        return self.client._make_request("DELETE", f"/agent/{agent_id}", headers=headers)

    def restore_agent(self, agent_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Restore a soft-deleted agent.

        Endpoint:
            ``PATCH /v1/agent/<agent_id>/restore`` - requires write scope.
        """
        return self.client._make_request("PATCH", f"/agent/{agent_id}/restore", headers=headers)

    def get_embed_code(self, agent_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retrieve the embed code that powers the public chat widget for this agent.

        Endpoint:
            ``GET /v1/agent/<agent_id>/embed-code`` - requires read scope or JWT.
        """
        return self.client._make_request("GET", f"/agent/{agent_id}/embed-code", headers=headers)

    def test_agent(
        self,
        agent_id: str,
        *,
        query: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Run a test prompt against the agent.

        Endpoint:
            ``POST /v1/agent/<agent_id>/test`` - requires read scope or JWT.

        Args:
            query: Optional free-form prompt; omitted defaults to a sample prompt on the server.
        """
        payload: Optional[Dict[str, Any]] = None
        if query is not None:
            payload = {"query": query}
        return self.client._make_request(
            "POST",
            f"/agent/{agent_id}/test",
            data=payload,
            headers=headers,
        )

    def get_agent_stats(self, agent_id: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retrieve aggregate statistics for an agent.

        Endpoint:
            ``GET /v1/agent/<agent_id>/stats`` - requires read scope or JWT.
        """
        return self.client._make_request("GET", f"/agent/{agent_id}/stats", headers=headers)

    def clone_agent(
        self,
        agent_id: str,
        *,
        name: Optional[str] = None,
        llm_settings_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Duplicate an agent configuration.

        Endpoint:
            ``POST /v1/agent/<agent_id>/clone`` - requires write scope.

        Payload options:
            ``name`` for the new agent; ``llm_settings_id`` to override the copied settings.
        """
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if llm_settings_id is not None:
            payload["llm_settings_id"] = llm_settings_id
        return self.client._make_request("POST", f"/agent/{agent_id}/clone", data=payload or None, headers=headers)

    def fetch_widget_script(self, headers: Optional[Dict[str, str]] = None) -> str:
        """
        Download the public widget JavaScript bundle.

        Endpoint:
            ``GET /widget.js`` - no authentication required.

        Returns:
            Raw JavaScript text as delivered by the API.
        """
        response = self.client._make_request("GET", "/widget.js", headers=headers)
        if isinstance(response, bytes):
            return response.decode("utf-8")
        if isinstance(response, str):
            return response
        raise TypeError("Expected widget.js to return a JavaScript string, received JSON payload instead.")

    def render_test_page(
        self,
        body_html: str,
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Request the internal widget test page.

        Endpoint:
            ``POST /test`` - intended for internal QA flows; no authentication.

        Payload:
            ``body`` containing an HTML snippet.
        """
        payload = {"body": body_html}
        return self.client._make_request("POST", "/test", data=payload, headers=headers)
