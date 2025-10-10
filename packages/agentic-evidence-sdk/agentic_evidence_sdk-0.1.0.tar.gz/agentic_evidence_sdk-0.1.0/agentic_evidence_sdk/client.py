# SPDX-License-Identifier: Apache-2.0
# Copyright © 2025 Rajeshwar Dhayalan and Contributors

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json
import time
import urllib.request
import urllib.error
from pydantic import BaseModel

# Models (SDK-local, aligned with backend schemas)
class ArtifactCreate(BaseModel):
    filename: str
    content_type: Optional[str] = None
    content_base64: Optional[str] = None
    uri: Optional[str] = None
    size: Optional[int] = None
    sha256: Optional[str] = None

class EvidenceCreate(BaseModel):
    source: str
    agent_id: Optional[str] = None
    event: Dict[str, Any]
    time: Optional[str] = None
    level: Optional[str] = None
    environment: Optional[str] = None
    service: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    controls_hints: Optional[List[str]] = None
    artifacts: Optional[List[ArtifactCreate]] = None

class ArtifactResponse(BaseModel):
    uri: str
    content_hash: str
    size: Optional[int]

class EvidenceResponse(BaseModel):
    evidence_id: str
    created_at: str
    status: str
    combined_hash: str
    signature: Optional[str] = None
    artifacts: Optional[List[ArtifactResponse]] = None

class EvidenceDetail(BaseModel):
    evidence_id: str
    source: str
    agent_id: Optional[str]
    event: Dict[str, Any]
    timestamp: str
    status: str
    status_updated_at: Optional[str]
    status_reason: Optional[str]
    combined_hash: Optional[str]
    signature: Optional[str]
    artifacts: Optional[List[ArtifactResponse]]

class ControlMappingResponse(BaseModel):
    control_id: str
    confidence: Optional[float]
    rationale: Optional[str]
    matched_rule_id: Optional[str]
    mapping_version: int
    rule_pack_digest: Optional[str]
    mapped_at: str
    status: str

class PaginatedEvidence(BaseModel):
    items: List[EvidenceDetail]
    total_count: int
    limit: int
    offset: int
    has_next: bool
    next_offset: Optional[int] = None
    sort: Optional[str] = None
    applied_filters: Optional[Dict[str, Any]] = None

@dataclass
class EvidenceClient:
    base_url: str = "http://127.0.0.1:8000"
    api_key: str = ""
    timeout: Optional[float] = 10.0
    retries: int = 3

    def _headers(self) -> Dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, params: Dict[str, Any] | None = None, body: Dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            from urllib.parse import urlencode
            qs = urlencode({k: v for k, v in params.items() if v is not None})
            if qs:
                url = f"{url}?{qs}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, headers=self._headers(), method=method)
        attempt = 0
        backoff = 0.5
        while True:
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    text = resp.read().decode("utf-8")
                    return json.loads(text) if text else None
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                attempt += 1
                if attempt > self.retries:
                    raise
                time.sleep(backoff)
                backoff = min(backoff * 2, 2.0)

    # Methods
    def record_evidence(self, evidence: EvidenceCreate | Dict[str, Any]) -> EvidenceResponse:
        if isinstance(evidence, EvidenceCreate):
            payload = evidence.model_dump()
        else:
            payload = evidence
        data = self._request("POST", "/api/v1/evidence", body=payload)
        return EvidenceResponse.model_validate(data)

    def get_evidence(self, evidence_id: str) -> EvidenceDetail:
        data = self._request("GET", f"/api/v1/evidence/{evidence_id}")
        return EvidenceDetail.model_validate(data)

    def list_evidence(self,
                      limit: int = 50,
                      offset: int = 0,
                      source: Optional[str] = None,
                      agent_id: Optional[str] = None,
                      status: Optional[str] = None,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      sort: Optional[str] = None,
                      return_items_only: bool = True) -> List[EvidenceDetail] | PaginatedEvidence:
        params = {
            "limit": limit,
            "offset": offset,
            "source": source,
            "agent_id": agent_id,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "sort": sort,
        }
        data = self._request("GET", "/api/v1/evidence", params=params)
        if return_items_only:
            # Support both wrapper and raw list responses for compatibility
            if isinstance(data, dict) and "items" in data:
                return [EvidenceDetail.model_validate(item) for item in data["items"]]
            return [EvidenceDetail.model_validate(item) for item in data]
        else:
            return PaginatedEvidence.model_validate(data)

    def list_mappings(self, evidence_id: str) -> List[ControlMappingResponse]:
        data = self._request("GET", f"/api/v1/evidence/{evidence_id}/mappings")
        return [ControlMappingResponse.model_validate(item) for item in data]