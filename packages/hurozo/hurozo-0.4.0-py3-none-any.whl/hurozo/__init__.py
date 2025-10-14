"""Lightweight Hurozo client library.

Provides an :class:`Agent` class to invoke agents via the Hurozo API and a
``RemoteAgent`` helper to register remote agents.

Usage patterns:
  - Name-based: ``agent = Agent("My Agent")``  -> resolves name to UUID at runtime.
  - UUID-based: ``agent = Agent("2325125b-...", True)``  -> uses UUID directly.
  - Remote agent: ``RemoteAgent(my_handler, {"inputs": [...], "outputs": [...]})``

Then:
  - Provide inputs: ``agent.input({"key": "value"})``
  - Run: ``agent.run()``

Configuration:
  - ``HUROZO_API_TOKEN``: Bearer token for API calls (required for name resolution and execution).
  - ``HUROZO_SERVER_URI``: Base URL for the API (default: ``https://hurozo.com``).
  - ``HUROZO_TOKEN`` / ``HUROZO_API_URL``: Optional aliases used by :class:`RemoteAgent`.
"""

from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
from typing import Any, Callable, Dict, Iterable, Optional

import requests

from .firebase import FirebaseAuthError, FirebaseRealtimeBridge, RemoteRequest


def _to_snake(name: str) -> str:
    """Convert a name to snake_case suitable for env vars."""
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return name.strip("_").lower()


class Agent:
    """Represents an agent executable via the Hurozo API.

    Parameters:
    - identifier: display name (default) or UUID (when is_uuid=True)
    - is_uuid: set to True to skip name->UUID resolution and use the identifier directly
    """

    def __init__(self, identifier: str, is_uuid: bool = False):
        self._identifier = identifier
        self._is_uuid = is_uuid
        self.inputs: Dict[str, Any] = {}

    def input(self, mapping: Dict[str, Any]) -> "Agent":
        """Merge ``mapping`` into the agent's input dictionary."""
        self.inputs.update(mapping)
        return self

    def _resolve_uuid(self) -> str:
        """Resolve a display name to an agent UUID via /api/agents.

        Returns the identifier unchanged on failure or if already UUID mode.
        """
        if self._is_uuid:
            return self._identifier

        token = os.environ.get("HUROZO_API_TOKEN")
        if not token:
            # No token -> cannot resolve name. Fall back to given identifier.
            return self._identifier
        base_uri = os.environ.get("HUROZO_SERVER_URI", "https://hurozo.com").rstrip("/")
        try:
            resp = requests.get(
                f"{base_uri}/api/agents",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if not resp.ok:
                return self._identifier
            data = resp.json() or {}
            agents = data.get("agents", []) or []
            # Prefer exact case-sensitive match, then case-insensitive
            target: Optional[dict] = next((a for a in agents if a.get("name") == self._identifier), None)
            if not target:
                lid = self._identifier.lower()
                target = next((a for a in agents if str(a.get("name", "")).lower() == lid), None)
            return target.get("agent_uuid") if target and target.get("agent_uuid") else self._identifier
        except Exception:
            return self._identifier

    def run(self) -> Dict[str, Any]:
        """Invoke the agent via the Hurozo API using the configured token."""
        token = os.environ.get("HUROZO_API_TOKEN")
        if not token:
            raise RuntimeError("HUROZO_API_TOKEN environment variable is required")
        base_uri = os.environ.get("HUROZO_SERVER_URI", "https://hurozo.com").rstrip("/")
        agent_key = self._resolve_uuid()
        url = f"{base_uri}/execute/{agent_key}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json={"inputs": self.inputs})
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"status": response.status_code, "text": response.text}


class RemoteAgent:
    """Register a Python callable as a remote agent using REST polling."""

    def __init__(self, handler: Callable[..., Dict[str, Any]], meta: Dict[str, Any]):
        self.handler = handler
        self.name = meta.get("name") or handler.__name__
        self.inputs = meta.get("inputs", [])
        self.outputs = meta.get("outputs", [])

        self.token = (
            os.environ.get("HUROZO_TOKEN")
            or os.environ.get("HUROZO_API_TOKEN")
            or ""
        )
        if not self.token:
            raise RuntimeError("HUROZO_TOKEN or HUROZO_API_TOKEN must be set for RemoteAgent")
        self.base_url = (
            os.environ.get("HUROZO_API_URL")
            or os.environ.get("HUROZO_SERVER_URI", "https://hurozo.com")
        ).rstrip("/")
        self.poll_interval = float(os.environ.get("HUROZO_REMOTE_POLL_INTERVAL", "1.0"))

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "hurozo-remote-agent/1.0"})

        self.debug = str(os.getenv("HUROZO_DEBUG", "")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        self._stop = False
        self._stop_event = threading.Event()
        self._firebase: Optional[FirebaseRealtimeBridge] = None
        self._request_queue: "queue.Queue[RemoteRequest]" = queue.Queue()
        self._pending_request_ids: set[str] = set()

        threading.Thread(target=self._register_loop, daemon=True).start()
        if self._init_realtime():
            self._run_realtime_loop()
        else:
            self._run_polling_loop()

    def _log(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        if not self.debug:
            return
        line = f"[RemoteAgent:{self.name}] {message}"
        if extra:
            try:
                payload = json.dumps(extra, default=str)
            except Exception:
                payload = str(extra)
            line = f"{line} :: {payload}"
        print(line, flush=True)

    def _auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _register_loop(self) -> None:
        url = f"{self.base_url}/api/remote_agents/register"
        payload = {"name": self.name, "inputs": self.inputs, "outputs": self.outputs}
        self._log("registration loop started")
        while not self._stop_event.is_set():
            try:
                res = self._session.post(url, json=payload, headers=self._auth_headers(), timeout=30)
                if res.ok:
                    try:
                        data = res.json() or {}
                        keys = list(data.keys())
                    except Exception:
                        keys = []
                    self._log("registration succeeded", {"status": res.status_code, "response_keys": keys})
                else:
                    self._log("registration failed", {"status": res.status_code, "body": res.text})
            except Exception as exc:
                self._log("registration request errored", {"error": str(exc)})
            time.sleep(240)

    def _init_realtime(self) -> bool:
        try:
            bridge = FirebaseRealtimeBridge(debug=self.debug)
            bridge.bootstrap(self.base_url, self.token)
            self._firebase = bridge
            self._log("realtime bridge ready", {"user_id": bridge.user_id})
            return True
        except FirebaseAuthError as exc:
            self._log("realtime bridge auth failed", {"error": str(exc)})
        except Exception as exc:
            self._log("realtime bridge initialization failed", {"error": str(exc)})
        self._firebase = None
        return False

    def _run_realtime_loop(self) -> None:
        if not self._firebase:
            self._run_polling_loop()
            return
        listener_thread = threading.Thread(target=self._realtime_listener_loop, daemon=True)
        listener_thread.start()
        self._log("realtime loop started")
        try:
            while not self._stop_event.is_set():
                try:
                    request = self._request_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                try:
                    self._process_request({"uuid": request.uuid, "inputs": request.inputs, "_raw": request.raw})
                except KeyboardInterrupt:
                    self._stop = True
                    self._stop_event.set()
                    raise
                except Exception as exc:
                    self._log("realtime request handling failed", {"uuid": request.uuid, "error": str(exc)})
                finally:
                    self._pending_request_ids.discard(request.uuid)
        finally:
            self._stop = True
            self._stop_event.set()

    def _realtime_listener_loop(self) -> None:
        if not self._firebase:
            return

        def stop_check() -> bool:
            return self._stop_event.is_set()

        def enqueue(request: RemoteRequest) -> None:
            if request.uuid in self._pending_request_ids:
                return
            self._pending_request_ids.add(request.uuid)
            self._request_queue.put(request)
            self._log("enqueued realtime request", {"uuid": request.uuid})

        try:
            self._firebase.listen_remote_requests(self.name, enqueue, stop_check)
        except Exception as exc:
            self._log("realtime listener exited", {"error": str(exc)})

    def _run_polling_loop(self) -> None:
        self._log("polling loop started", {"poll_interval": self.poll_interval})
        try:
            while not self._stop_event.is_set():
                try:
                    requests_payload = self._fetch_pending_requests()
                except Exception as exc:
                    self._log("fetch pending failed; backing off", {"error": str(exc)})
                    time.sleep(self.poll_interval)
                    continue
                if not requests_payload:
                    self._log("no pending requests")
                    time.sleep(self.poll_interval)
                    continue
                self._log("fetched pending requests", {"count": len(requests_payload)})
                for request_payload in requests_payload:
                    try:
                        self._process_request(request_payload)
                    except KeyboardInterrupt:
                        self._stop = True
                        self._stop_event.set()
                        raise
                    except Exception as exc:
                        self._log("request handling failed", {"error": str(exc)})
                        time.sleep(0.1)
        finally:
            self._stop = True
            self._stop_event.set()

    def _fetch_pending_requests(self) -> Iterable[Dict[str, Any]]:
        url = f"{self.base_url}/api/remote_agents/requests"
        params = {"agent": self.name, "limit": 20}
        res = self._session.get(url, headers=self._auth_headers(), params=params, timeout=30)
        if not res.ok:
            self._log("pending requests http error", {"status": res.status_code, "body": res.text})
        res.raise_for_status()
        data = res.json() or {}
        requests_payload = data.get("requests") or []
        return [payload for payload in requests_payload if isinstance(payload, dict)]

    def _process_request(self, payload: Dict[str, Any]) -> None:
        uuid = payload.get("uuid") or payload.get("id")
        if not uuid:
            return
        inputs = payload.get("inputs") or {}
        if not isinstance(inputs, dict):
            inputs = {"input": inputs}
        self._log("processing request", {"uuid": uuid})
        if not self._update_request(uuid, "in_progress"):
            return
        self._emit_event("execution_started", {"runId": uuid})
        try:
            try:
                outputs = self.handler(**inputs)
            except TypeError:
                outputs = self.handler(inputs)
        except Exception as exc:
            message = getattr(exc, "message", None) or str(exc)
            self._update_request(uuid, "error", error={"message": message})
            self._log("wrote error response", {"uuid": uuid, "error": message})
            self._emit_event("execution_error", {"runId": uuid, "message": message})
            return
        result_map = self._normalize_outputs(outputs)
        if self._update_request(uuid, "done", outputs=result_map):
            self._log("wrote success response", {"uuid": uuid})
            self._emit_event("execution_finished", {"runId": uuid, "results": result_map})

    def _update_request(self, uuid: str, status: str, **payload: Any) -> bool:
        if self._firebase:
            try:
                outputs = payload.get("outputs") if status == "done" else None
                error = payload.get("error") if status == "error" else None
                if self._firebase.update_remote_request(uuid, status, outputs=outputs, error=error):
                    return True
            except Exception as exc:
                self._log("firestore update failed; falling back to REST", {"uuid": uuid, "status": status, "error": str(exc)})

        url = f"{self.base_url}/api/remote_agents/requests/{uuid}"
        body = {"status": status, "agent": self.name, **payload}
        res = self._session.post(url, headers=self._auth_headers(), json=body, timeout=15)
        if res.status_code == 409:
            self._log("request update conflict", {"uuid": uuid, "status": status})
            return False
        if not res.ok:
            self._log("request update failed", {"uuid": uuid, "status": status, "status_code": res.status_code, "body": res.text})
        res.raise_for_status()
        return True

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        if not self._firebase:
            return
        try:
            self._firebase.create_event(event_type, payload)
        except Exception as exc:
            self._log("failed to publish event", {"event": event_type, "error": str(exc)})

    def _normalize_outputs(self, outputs: Any) -> Dict[str, Any]:
        if outputs is None:
            return {name: None for name in self.outputs} if self.outputs else {}
        if isinstance(outputs, dict):
            if self.outputs:
                normalized = {name: outputs.get(name) for name in self.outputs}
                remaining = {k: v for k, v in outputs.items() if k not in normalized}
                normalized.update(remaining)
                return normalized
            return outputs
        if self.outputs:
            if len(self.outputs) == 1:
                return {self.outputs[0]: outputs}
            if isinstance(outputs, (list, tuple)):
                combined = {}
                for idx, name in enumerate(self.outputs):
                    combined[name] = outputs[idx] if idx < len(outputs) else None
                return combined
            return {self.outputs[0]: outputs}
        if isinstance(outputs, (list, tuple)):
            return {str(idx): value for idx, value in enumerate(outputs)}
        return {"output": outputs}

Node = RemoteAgent
__all__ = ["Agent", "RemoteAgent", "Node"]
