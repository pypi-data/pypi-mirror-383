from __future__ import annotations
class _RecordingApi:
    def __init__(self, client_id: str = "client", should_fail: bool = False):
        self.client_id = client_id
        self.calls: List[Tuple[str, str, Optional[Dict[str, Any]]]] = []
        self._should_fail = should_fail
        self.base_url = "https://example.com"
        self.user_email = "tester@example.com"
        self.token = "token"

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.calls.append((method, endpoint, payload))
        if self._should_fail:
            raise RuntimeError("boom")
        return {"status": "ok"}


def test_v8_create_site_graphs_posts_expected_payload():
    api = _RecordingApi()
    service = V8FeatureApiService(api)
    payload = {"type": "FeatureCollection", "features": []}

    assert service.create_site_graphs("site-1", payload) is True
    assert api.calls == [("POST", "api/v8/sites/site-1/graphs", payload)]


def test_v8_create_site_graphs_returns_false_on_error():
    api = _RecordingApi(should_fail=True)
    service = V8FeatureApiService(api)

    assert service.create_site_graphs("site-1", {"type": "FeatureCollection", "features": []}) is False


def test_v8_upsert_building_features_uses_correct_endpoint():
    api = _RecordingApi()
    service = V8FeatureApiService(api)
    payload = {"type": "FeatureCollection", "features": []}

    service.upsert_building_features("site-1", "building-2", payload)

    assert api.calls == [("PUT", "api/v8/sites/site-1/buildings/building-2/features", payload)]


def test_v9_create_site_features_puts_payload_with_client_prefix():
    api = _RecordingApi(client_id="cid-123")
    service = V9FeatureApiService(api)
    service._make_request = api._make_request  # type: ignore[attr-defined]
    payload = {"type": "FeatureCollection", "features": []}

    assert service.create_site_features("site-9", payload) is True
    assert api.calls == [("PUT", "api/v9/content/draft/clients/cid-123/sites/site-9/features", payload)]


def test_v9_get_site_paths_hits_paths_endpoint():
    api = _RecordingApi(client_id="cid-123")
    service = V9FeatureApiService(api)
    service._make_request = api._make_request  # type: ignore[attr-defined]

    service.get_site_paths("site-42")

    assert api.calls == [("GET", "api/v9/content/draft/clients/cid-123/sites/site-42/paths", None)]
from typing import Any, Dict, List, Optional
import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pointr_cloud_common.api.v8.feature_service as v8_feature_module
import pointr_cloud_common.api.v9.feature_service as v9_feature_module

v8_feature_module = importlib.reload(v8_feature_module)
v9_feature_module = importlib.reload(v9_feature_module)

V8FeatureApiService = v8_feature_module.FeatureApiService
V9FeatureApiService = v9_feature_module.FeatureApiService


class _DummyApiService:
    def __init__(self) -> None:
        self.base_url = "https://example.com"
        self.client_id = "test-client"
        self.token = "token"
        self.user_email = None


class _LevelStub:
    def __init__(self, fid: str) -> None:
        self.fid = fid


class _LevelAwareApiService(_DummyApiService):
    def __init__(self, levels: List[_LevelStub]) -> None:
        super().__init__()
        self._levels = levels

    def get_levels(self, site_id: str, building_id: str) -> List[_LevelStub]:
        return self._levels


class _Recorder:
    def __init__(self, response: Optional[Dict[str, Any]] = None) -> None:
        self.calls: List[Dict[str, Any]] = []
        self._response = response or {}

    def __call__(
        self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.calls.append({"method": method, "endpoint": endpoint, "payload": payload})
        return self._response


def test_v8_get_level_mapobjects_uses_draft_endpoint() -> None:
    service = V8FeatureApiService(_DummyApiService())
    recorder = _Recorder({"features": []})
    service._make_request = recorder  # type: ignore[assignment]

    service.get_level_mapobjects("b1", "L2")

    assert recorder.calls == [
        {
            "method": "GET",
            "endpoint": "api/v8/buildings/b1/levels/L2/mapobjects/draft",
            "payload": None,
        }
    ]


def test_v8_upsert_level_beacons_wraps_single_feature() -> None:
    service = V8FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    feature = {"type": "Feature", "properties": {}}
    service.upsert_level_beacons("b1", "L2", feature)

    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == "api/v8/buildings/b1/levels/L2/beacons"
    assert call["payload"] == {"type": "FeatureCollection", "features": [feature]}


def test_v8_get_building_graphs_extracts_result_collection() -> None:
    graphs = {"type": "FeatureCollection", "features": [{"id": 1}]}
    service = V8FeatureApiService(_DummyApiService())
    recorder = _Recorder({"result": graphs})
    service._make_request = recorder  # type: ignore[assignment]

    result = service.get_building_graphs("building-1")

    assert result == graphs
    assert recorder.calls[0]["endpoint"] == "api/v8/buildings/building-1/graphs/draft"


def test_v8_put_site_paths_accepts_feature_list() -> None:
    service = V8FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    feature = {"type": "Feature", "properties": {"fid": "f1"}}
    success = service.put_site_paths("site-1", [feature])

    assert success is True
    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == "api/v8/sites/site-1/graphs"
    assert call["payload"] == {"type": "FeatureCollection", "features": [feature]}


def test_v8_collect_level_mapobjects_traverses_levels() -> None:
    api_service = _LevelAwareApiService([_LevelStub("L1"), _LevelStub("L2")])
    service = V8FeatureApiService(api_service)

    calls: List[Tuple[str, str]] = []

    def fake_level_mapobjects(building_id: str, level_id: str) -> Dict[str, Any]:
        calls.append((building_id, level_id))
        return {"features": [{"level": level_id}]}

    service.get_level_mapobjects = fake_level_mapobjects  # type: ignore[assignment]

    result = service.collect_level_mapobjects("site-1", "building-7")

    assert calls == [("building-7", "L1"), ("building-7", "L2")]
    assert result == {
        "type": "FeatureCollection",
        "features": [{"level": "L1"}, {"level": "L2"}],
    }


def test_v9_put_building_map_objects_uses_post_endpoint() -> None:
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    payload = {"type": "FeatureCollection", "features": []}
    service.put_building_map_objects("site-1", "building-1", payload)

    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/map-objects"
    )
    assert call["payload"] == payload


def test_v9_put_building_beacons_uses_post_endpoint() -> None:
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    payload = {"type": "FeatureCollection", "features": []}
    service.put_building_beacons("site-1", "building-1", payload)

    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/beacons"
    )
    assert call["payload"] == payload


def test_v9_put_building_beacon_geofences_uses_post_endpoint() -> None:
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    payload = {"type": "FeatureCollection", "features": []}
    service.put_building_beacon_geofences("site-1", "building-1", payload)

    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/beacon-geofences"
    )
    assert call["payload"] == payload


def test_v9_get_building_beacon_geofences_hits_endpoint() -> None:
    response = {"features": []}
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder(response)
    service._make_request = recorder  # type: ignore[assignment]

    result = service.get_building_beacon_geofences("site-1", "building-1")

    assert result == response
    call = recorder.calls[0]
    assert call["method"] == "GET"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/beacon-geofences"
    )


def test_v9_put_building_paths_uses_post_endpoint() -> None:
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    payload = {"type": "FeatureCollection", "features": []}
    service.put_building_paths("site-1", "building-1", payload)

    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/paths"
    )
    assert call["payload"] == payload


def test_v9_put_site_paths_returns_boolean() -> None:
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder()
    service._make_request = recorder  # type: ignore[assignment]

    paths = [{"type": "Feature", "properties": {"fid": "p1"}}]
    success = service.put_site_paths("site-1", paths)

    assert success is True
    call = recorder.calls[0]
    assert call["method"] == "POST"
    assert call["endpoint"] == "api/v9/content/draft/clients/test-client/sites/site-1/paths"
    assert call["payload"] == {"type": "FeatureCollection", "features": paths}


def test_v9_get_building_paths_uses_get() -> None:
    response = {"features": []}
    service = V9FeatureApiService(_DummyApiService())
    recorder = _Recorder(response)
    service._make_request = recorder  # type: ignore[assignment]

    result = service.get_building_paths("site-1", "building-1")

    assert result == response
    call = recorder.calls[0]
    assert call["method"] == "GET"
    assert call["endpoint"] == (
        "api/v9/content/draft/clients/test-client/sites/site-1/buildings/building-1/paths"
    )
