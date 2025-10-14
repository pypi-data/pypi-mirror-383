from typing import Dict, Any, List, Optional, Union
import logging
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError


class FeatureApiService(BaseApiService):
    """Service for handling feature operations in V9 API."""

    def __init__(self, api_service):
        """Initialize the feature service."""
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_site_features(self, site_fid: str) -> Dict[str, Any]:
        """
        Get all features for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            Dictionary containing all features for the site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site features for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def get_site_features_by_type(self, site_fid: str, type_code: str) -> Dict[str, Any]:
        """
        Get features of a specific type for a site.
        
        Args:
            site_fid: The site FID
            type_code: The type code of features to retrieve
            
        Returns:
            Dictionary containing features of the specified type
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features/type-code/{type_code}"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site features by type {type_code} for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def get_site_paths(self, site_fid: str) -> Dict[str, Any]:
        """
        Get all paths for a site.

        Args:
            site_fid: The site FID

        Returns:
            Dictionary containing all paths for the site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/paths"
        try:
            response = self._make_request("GET", endpoint)
            return response
        except Exception as e:
            self.logger.error(f"Failed to get site paths for {site_fid}: {str(e)}")
            return {"type": "FeatureCollection", "features": []}

    def put_site_paths(
        self, site_fid: str, paths: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> bool:
        """Replace outdoor paths for a site using a POST request."""
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/paths"
        try:
            payload = self._ensure_feature_collection(paths)
            self._make_request("POST", endpoint, payload)
            return True
        except Exception as e:
            self.logger.error(f"Failed to put site paths for {site_fid}: {str(e)}")
            return False

    def create_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        """
        Create features for a site.
        
        Args:
            site_fid: The site FID
            features: The features to create
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            response = self._make_request("PUT", endpoint, features)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create site features for {site_fid}: {str(e)}")
            return False

    def update_site_features(self, site_fid: str, features: Dict[str, Any]) -> bool:
        """
        Update features for a site.
        
        Args:
            site_fid: The site FID
            features: The features to update
            
        Returns:
            True if successful, False otherwise
        """
        return self.create_site_features(site_fid, features)

    def delete_site_features(self, site_fid: str) -> bool:
        """
        Delete all features for a site.

        Args:
            site_fid: The site FID

        Returns:
            True if successful, False otherwise
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/features"
        try:
            self._make_request("DELETE", endpoint)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete site features for {site_fid}: {str(e)}")
            return False

    def get_building_map_objects(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        """Retrieve map objects for a building."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/map-objects"
        )
        return self._make_request("GET", endpoint)

    def put_building_map_objects(
        self,
        site_fid: str,
        building_fid: str,
        map_objects: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Replace map objects for a building using POST semantics."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/map-objects"
        )
        payload = self._ensure_feature_collection(map_objects)
        return self._make_request("POST", endpoint, payload)

    def get_building_beacons(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        """Retrieve beacons for a building."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/beacons"
        )
        return self._make_request("GET", endpoint)

    def put_building_beacons(
        self,
        site_fid: str,
        building_fid: str,
        beacons: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Replace beacons for a building using POST semantics."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/beacons"
        )
        payload = self._ensure_feature_collection(beacons)
        return self._make_request("POST", endpoint, payload)

    def get_building_beacon_geofences(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        """Retrieve beacon geofences for a building."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/beacon-geofences"
        )
        return self._make_request("GET", endpoint)

    def put_building_beacon_geofences(
        self,
        site_fid: str,
        building_fid: str,
        beacon_geofences: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Replace beacon geofences for a building using POST semantics."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/beacon-geofences"
        )
        payload = self._ensure_feature_collection(beacon_geofences)
        return self._make_request("POST", endpoint, payload)

    def put_building_paths(
        self,
        site_fid: str,
        building_fid: str,
        paths: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Replace indoor paths for a building using POST semantics."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/paths"
        )
        payload = self._ensure_feature_collection(paths)
        return self._make_request("POST", endpoint, payload)

    def get_building_paths(self, site_fid: str, building_fid: str) -> Dict[str, Any]:
        """Retrieve indoor paths for a building."""
        endpoint = (
            f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}/paths"
        )
        return self._make_request("GET", endpoint)

    @staticmethod
    def _ensure_feature_collection(
        data: Union[Dict[str, Any], List[Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """Normalize payloads into a GeoJSON FeatureCollection."""
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
