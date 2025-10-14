from typing import Dict, Any, Callable, List, Optional, Union
import logging
from pointr_cloud_common.api.v8.base_service import BaseApiService


class FeatureApiService(BaseApiService):
    """Service for handling feature operations in V8 API."""

    def __init__(self, api_service):
        """Initialize the feature service."""
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_building_features(self, building_id: str) -> Dict[str, Any]:
        """
        Fetch all features for a building (V8: /api/v8/buildings/{building_id}/features/draft).
        Always returns a FeatureCollection (extracts from response['result']['features']).
        """
        endpoint = f"api/v8/buildings/{building_id}/features/draft"
        response = self._make_request("GET", endpoint)
       
        # Extract features from the result field when present
        if response and "result" in response:
            return response["result"]

        # If the API already returns a FeatureCollection, pass it through
        if response:
            return response
        return {"type": "FeatureCollection", "features": []}

    def get_building_features_by_type(self, building_id: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a building.
        
        Args:
            building_id: The building identifier
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type
        """
        endpoint = f"api/v8/buildings/{building_id}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_level_features(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """
        Get all features for a specific level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            
        Returns:
            Dictionary containing all features for the level
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/draft"
        return self._make_request("GET", endpoint)

    def get_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type for the level
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_site_features(self, site_id: str) -> Dict[str, Any]:
        """
        Get all features for a site.
        
        Args:
            site_id: The site identifier
            
        Returns:
            Dictionary containing all features for the site
        """
        endpoint = f"api/v8/sites/{site_id}/features/draft"
        return self._make_request("GET", endpoint)

    def get_site_features_by_type(self, site_id: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a site.
        
        Args:
            site_id: The site identifier
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type for the site
        """
        endpoint = f"api/v8/sites/{site_id}/features/type-codes/{type_code}/draft"
        return self._make_request("GET", endpoint)

    def get_level_mapobjects(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """Get map objects for a specific level using the draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/mapobjects/draft"
        return self._make_request("GET", endpoint)

    def upsert_level_mapobjects(
        self,
        building_id: str,
        level_index: str,
        mapobjects: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Create or update map objects for a level using the non-draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/mapobjects"
        payload = self._ensure_feature_collection(mapobjects)
        return self._make_request("POST", endpoint, payload)

    def get_level_beacons(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """Get beacons for a specific level using the draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/beacons/draft"
        return self._make_request("GET", endpoint)

    def upsert_level_beacons(
        self,
        building_id: str,
        level_index: str,
        beacons: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Create or update beacons for a level using the non-draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/beacons"
        payload = self._ensure_feature_collection(beacons)
        return self._make_request("POST", endpoint, payload)

    def get_level_geofences(self, building_id: str, level_index: str) -> Dict[str, Any]:
        """Get beacon geofences for a level using the draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/geofences/draft"
        return self._make_request("GET", endpoint)

    def upsert_level_geofences(
        self,
        building_id: str,
        level_index: str,
        geofences: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Create or update beacon geofences for a level using the non-draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/geofences"
        payload = self._ensure_feature_collection(geofences)
        return self._make_request("POST", endpoint, payload)

    def get_building_graphs(self, building_id: str) -> Dict[str, Any]:
        """Get all graphs for a building using the draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/graphs/draft"
        response = self._make_request("GET", endpoint)
        if response and "result" in response and response["result"]:
            return response["result"]
        if response:
            return response
        return {"type": "FeatureCollection", "features": []}

    def upsert_building_graphs(
        self, building_id: str, graphs: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Create or update graphs for a building using the non-draft endpoint."""
        endpoint = f"api/v8/buildings/{building_id}/graphs"
        payload = self._ensure_feature_collection(graphs)
        return self._make_request("POST", endpoint, payload)

    def get_site_paths(self, site_id: str) -> Dict[str, Any]:
        """Get all outdoor paths for a site using the graphs endpoint."""
        return self.get_site_graphs(site_id)
    
    def get_site_graphs(self, site_id: str) -> Dict[str, Any]:
        """
        Get all graphs (paths) for a site using the V8 graphs endpoint.
        
        Args:
            site_id: The site identifier
            
        Returns:
            Dictionary containing all graphs for the site
        """
        endpoint = f"api/v8/sites/{site_id}/graphs/draft"
        response = self._make_request("GET", endpoint)
        
        # V8 API returns data in the 'result' field
        if response and "result" in response and response["result"]:
            return response["result"]
        
        return {"type": "FeatureCollection", "features": []}
    
    def put_site_paths(
        self, site_id: str, paths: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> bool:
        """Create or update outdoor paths for a site using the graphs endpoint."""
        endpoint = f"api/v8/sites/{site_id}/graphs"
        try:
            payload = self._ensure_feature_collection(paths)
            self._make_request("POST", endpoint, payload)
            return True
        except Exception as e:
            self.logger.error(f"Failed to upsert site paths for {site_id}: {str(e)}")
            return False

    def create_site_graphs(self, site_id: str, graphs: Dict[str, Any]) -> bool:
        """Backward compatible alias for :meth:`put_site_paths`."""
        return self.put_site_paths(site_id, graphs)

    def upsert_building_features(self, site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upsert (create or update) all features for a building (V8: /api/v8/sites/{site_id}/buildings/{building_id}/features).
        """
        endpoint = f"api/v8/sites/{site_id}/buildings/{building_id}/features"
        return self._make_request("PUT", endpoint, features)

    # Backwards compatibility
    def create_or_update_building_features(self, site_id: str, building_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for ``upsert_building_features`` for legacy callers."""
        return self.upsert_building_features(site_id, building_id, features)

    def create_or_update_level_features(self, building_id: str, level_index: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update features for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            features: The features to create or update
            
        Returns:
            Response from the API
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features"
        return self._make_request("PUT", endpoint, features)

    def create_or_update_site_features(self, site_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update features for a site.
        
        Args:
            site_id: The site identifier
            features: The features to create or update
            
        Returns:
            Response from the API
        """
        endpoint = f"api/v8/sites/{site_id}/features"
        return self._make_request("PUT", endpoint, features)

    def delete_building_features(self, site_id: str, building_id: str) -> bool:
        """
        Delete all features for a building.
        
        Args:
            site_id: The site identifier
            building_id: The building identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_building_features_by_type(self, building_id: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a building.
        
        Args:
            building_id: The building identifier
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def delete_level_features(self, building_id: str, level_index: str) -> bool:
        """
        Delete all features for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_level_features_by_type(self, building_id: str, level_index: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a level.
        
        Args:
            building_id: The building identifier
            level_index: The level index
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/buildings/{building_id}/levels/{level_index}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def delete_site_features(self, site_id: str) -> bool:
        """
        Delete all features for a site.
        
        Args:
            site_id: The site identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/sites/{site_id}/features"
        self._make_request("DELETE", endpoint)
        return True

    def delete_site_features_by_type(self, site_id: str, type_code: str) -> bool:
        """
        Delete features of a specific type for a site.
        
        Args:
            site_id: The site identifier
            type_code: The type code of features to delete
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/sites/{site_id}/features/type-codes/{type_code}"
        self._make_request("DELETE", endpoint)
        return True

    def get_feature_by_id(self, feature_id: str) -> Dict[str, Any]:
        """
        Get a specific feature by its ID.
        
        Args:
            feature_id: The feature identifier
            
        Returns:
            Dictionary containing the feature data
        """
        endpoint = f"api/v8/features/{feature_id}"
        return self._make_request("GET", endpoint)

    def create_or_update_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a single feature.
        
        Args:
            feature: The feature data
            
        Returns:
            Response from the API
        """
        endpoint = "api/v8/features"
        return self._make_request("PUT", endpoint, {"features": [feature]})

    def delete_feature(self, feature_id: str) -> bool:
        """
        Delete a specific feature.
        
        Args:
            feature_id: The feature identifier
            
        Returns:
            True if successful
        """
        endpoint = f"api/v8/features/{feature_id}"
        self._make_request("DELETE", endpoint)
        return True

    def collect_level_mapobjects(self, site_id: str, building_id: str) -> Dict[str, Any]:
        """Aggregate all map objects for a building by traversing its levels."""
        return self._collect_level_features(
            site_id,
            building_id,
            self.get_level_mapobjects,
            "map objects",
        )

    def collect_level_beacons(self, site_id: str, building_id: str) -> Dict[str, Any]:
        """Aggregate all beacon features for a building by traversing its levels."""
        return self._collect_level_features(
            site_id,
            building_id,
            self.get_level_beacons,
            "beacons",
        )

    def collect_level_geofences(self, site_id: str, building_id: str) -> Dict[str, Any]:
        """Aggregate all beacon geofences for a building by traversing its levels."""
        return self._collect_level_features(
            site_id,
            building_id,
            self.get_level_geofences,
            "beacon geofences",
        )

    @staticmethod
    def _ensure_feature_collection(
        data: Union[Dict[str, Any], List[Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """Normalize input into a GeoJSON FeatureCollection payload."""
        if not data:
            return {"type": "FeatureCollection", "features": []}

        if isinstance(data, dict) and "features" in data:
            return data

        if isinstance(data, list):
            features = list(data)
        elif isinstance(data, dict):
            features = [data]
        else:
            raise TypeError("Unsupported payload type for feature collection")

        return {"type": "FeatureCollection", "features": features}

    def _collect_level_features(
        self,
        site_id: str,
        building_id: str,
        fetcher: Callable[[str, str], Dict[str, Any]],
        feature_label: str,
    ) -> Dict[str, Any]:
        """Helper to gather level-based feature collections for a building."""
        collection = {"type": "FeatureCollection", "features": []}

        try:
            levels = self.api_service.get_levels(site_id, building_id)
        except Exception as exc:
            self.logger.error(
                "Failed to load levels for building %s when collecting %s: %s",
                building_id,
                feature_label,
                exc,
            )
            return collection

        for level in levels or []:
            level_id = getattr(level, "fid", level)
            try:
                level_data = fetcher(building_id, level_id)
            except Exception as exc:
                self.logger.warning(
                    "Failed to retrieve %s for level %s in building %s: %s",
                    feature_label,
                    level_id,
                    building_id,
                    exc,
                )
                continue

            if level_data and level_data.get("features"):
                collection["features"].extend(level_data["features"])

        return collection
