from typing import Dict, Any, Optional, List
import json
import logging
from pointr_cloud_common.dto.v9.site_dto import SiteDTO
from pointr_cloud_common.dto.v9.create_response_dto import CreateResponseDTO
from pointr_cloud_common.dto.v9.building_dto import BuildingDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError


def _strip_geometry(obj: Any) -> Any:
    """Recursively drop geometry entries from nested dictionaries/lists."""

    if isinstance(obj, dict):
        return {key: _strip_geometry(value) for key, value in obj.items() if key != "geometry"}
    if isinstance(obj, list):
        return [_strip_geometry(item) for item in obj]
    return obj

class SiteApiService(BaseApiService):
    """Service for site-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def _extract_features(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, dict):
            if data.get("type") == "FeatureCollection":
                features = data.get("features", [])
            else:
                features = data.get("features", [])
        elif isinstance(data, list):
            features = data
        else:
            features = []

        return [feature for feature in features if isinstance(feature, dict)]

    def list_sites_with_buildings(
        self,
        data: Optional[Dict[str, Any]] = None,
    ) -> List[SiteDTO]:
        """Convert a V9 FeatureCollection into SiteDTO objects with nested buildings."""

        if data is None:
            endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites"
            self.logger.info(
                "Fetching V9 sites payload for list_sites_with_buildings: %s", endpoint
            )
            data = self._make_request("GET", endpoint)

        features = self._extract_features(data)
        sites_by_fid: Dict[str, SiteDTO] = {}
        ordered_site_fids: List[str] = []

        for feature in features:
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                continue

            type_code = properties.get("typeCode")
            if type_code != "site-outline":
                continue

            sanitized_feature: Dict[str, Any] = {
                "properties": _strip_geometry(properties),
                "sdkConfigurations": feature.get("sdkConfigurations", []),
                "options": feature.get("options", {}),
                "buildings": [],
            }

            try:
                site_dto = SiteDTO.from_api_json(sanitized_feature)
            except ValidationError as exc:
                raise V9ApiError(f"Failed to parse site feature: {str(exc)}") from exc

            if site_dto.fid not in sites_by_fid:
                ordered_site_fids.append(site_dto.fid)
                sites_by_fid[site_dto.fid] = site_dto

        for feature in features:
            properties = feature.get("properties")
            if not isinstance(properties, dict):
                continue

            if properties.get("typeCode") != "building-outline":
                continue

            sid = properties.get("sid")
            if not sid or sid not in sites_by_fid:
                self.logger.debug(
                    "Skipping building %s without matching site sid=%s",
                    properties.get("fid"),
                    sid,
                )
                continue

            sanitized_building = {
                "properties": _strip_geometry(properties),
                "levels": [],
                "sdkConfigurations": feature.get("sdkConfigurations", []),
                "options": feature.get("options", {}),
            }

            try:
                building_dto = BuildingDTO.from_api_json(sanitized_building)
            except ValidationError as exc:
                raise V9ApiError(
                    f"Failed to parse building feature: {str(exc)}"
                ) from exc

            sites_by_fid[sid].buildings.append(building_dto)

        return [sites_by_fid[fid] for fid in ordered_site_fids]

    def get_sites(self) -> List[SiteDTO]:
        """Get all sites for the client along with their buildings."""
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites"
        data = self._make_request("GET", endpoint)
        try:
            return self.list_sites_with_buildings(data)
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse sites: {str(e)}")

    def create_site(self, site: SiteDTO, source_api_service=None) -> str:
        """
        Create a site in the target environment.
        
        Args:
            site: The site DTO to create
            source_api_service: Optional source API service to fetch geometry data from
            
        Returns:
            The FID of the created site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites"
        
        # Get the site data from the source environment
        site_feature = None
        
        # If a source API service is provided, use it to fetch the source site data
        if source_api_service:
            try:
                self.logger.info(f"Fetching source site data for {site.fid} from source environment")
                source_site_data = source_api_service._make_request(
                    "GET", 
                    f"api/v9/content/draft/clients/{source_api_service.client_id}/sites/{site.fid}"
                )
                
                # Extract the site feature from the source data
                if source_site_data and "features" in source_site_data:
                    for feature in source_site_data["features"]:
                        if feature.get("properties", {}).get("typeCode") == "site-outline":
                            site_feature = feature
                            self.logger.info(f"Successfully retrieved geometry for site {site.fid} from source environment")
                            break
            except Exception as e:
                self.logger.error(f"Failed to retrieve source site data from source environment: {str(e)}")
        
        # If we couldn't find a site feature, create a minimal one
        if not site_feature:
            self.logger.warning(f"No site geometry found for site {site.fid}, creating minimal geometry")
            
            # Create a minimal site feature with the data we have
            site_feature = {
                "type": "Feature",
                "properties": {
                    "typeCode": "site-outline",
                    "name": site.name,
                    "fid": site.fid,
                    "extra": site.extraData
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [0.001, 0.001],  # Small default polygon as last resort
                            [0.001, 0.002],
                            [0.002, 0.002],
                            [0.002, 0.001],
                            [0.001, 0.001]
                        ]
                    ]
                }
            }
            
            # Add optional fields if present
            if hasattr(site, 'eid') and site.eid:
                site_feature["properties"]["eid"] = site.eid
        
        # Create a new feature collection with just the site feature
        payload = {
            "type": "FeatureCollection",
            "features": [site_feature]
        }
        
        self.logger.info(f"Creating site with payload: {json.dumps(payload)[:1000]}...")
        data = self._make_request("POST", endpoint, payload)
        try:
            return CreateResponseDTO.from_api_json(data).fid
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse create response: {str(e)}")

    def update_site(self, site_id: str, site: SiteDTO, source_api_service=None, migration_options=None) -> str:
        """
        Update a site in the target environment.
        
        Args:
            site_id: The ID of the site to update
            site: The site DTO with updated data
            source_api_service: Optional source API service to fetch geometry data from
            
        Returns:
            The FID of the updated site
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_id}"
        site_feature = None
        if source_api_service:
            try:
                source_site_data = source_api_service._make_request(
                    "GET", 
                    f"api/v9/content/draft/clients/{source_api_service.client_id}/sites/{site.fid}"
                )
                if source_site_data and "features" in source_site_data:
                    for feature in source_site_data["features"]:
                        if feature.get("properties", {}).get("typeCode") == "site-outline":
                            site_feature = feature
                            feature["properties"]["fid"] = site_id
                            break
            except Exception as e:
                self.logger.error(f"Exception fetching source site data: {str(e)}")
                import traceback
                print(traceback.format_exc())
                raise
        if not site_feature:
            self.logger.error(f"No site-outline feature found in source data for site {site.fid}")
            raise V9ApiError(f"No site-outline feature found in source data for site {site.fid}")

        # Handle external ID migration options
        if migration_options:
            migrate_external_id = migration_options.get("migrate_site_external_id", True)
            self.logger.info(f"[DEBUG] V9 Site: Got migrate_external_id from options: {migrate_external_id}")

            if not migrate_external_id:
                # When not migrating, try to preserve target's existing external ID
                self.logger.info(f"[DEBUG] V9 Site: Attempting to preserve target's existing external ID for site {site_id}")
                try:
                    # Get the current target site data to preserve its external ID
                    # For V9, use the site-specific draft endpoint
                    site_draft_endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_id}"
                    self.logger.info(f"[DEBUG] V9 Site: Fetching from endpoint: {site_draft_endpoint}")
                    current_site_data = self._make_request("GET", site_draft_endpoint)
                    self.logger.info(f"[DEBUG] V9 Site: Raw current data: {current_site_data}")

                    if current_site_data:
                        # Handle different response formats for V9
                        if "features" in current_site_data:
                            features = current_site_data["features"]
                        elif isinstance(current_site_data, dict) and any("type" in str(v) for v in current_site_data.values()):
                            # Might be a single feature response
                            features = [current_site_data]
                        else:
                            features = []

                        self.logger.info(f"[DEBUG] V9 Site: Features array: {features}")

                        for feature in features:
                            if feature.get("properties", {}).get("typeCode") == "site-outline":
                                current_eid = feature.get("properties", {}).get("eid")
                                self.logger.info(f"[DEBUG] V9 Site: Found eid in target: {current_eid}")
                                if current_eid:
                                    # Preserve the target's existing external ID
                                    site_feature["properties"]["eid"] = current_eid
                                    self.logger.info(f"[DEBUG] V9 Site: Preserving target site's existing external ID: {current_eid}")
                                else:
                                    # Remove eid if target doesn't have one
                                    if "eid" in site_feature["properties"]:
                                        del site_feature["properties"]["eid"]
                                    self.logger.info(f"[DEBUG] V9 Site: Target site has no external ID to preserve")
                                break
                        else:
                            self.logger.info(f"[DEBUG] V9 Site: No site-outline feature found in target data")
                    else:
                        self.logger.info(f"[DEBUG] V9 Site: No feature data found in target site")
                except Exception as e:
                    self.logger.warning(f"[DEBUG] V9 Site: Failed to get current target site data for external ID preservation: {str(e)}")
                    # If we can't fetch the current data, remove eid to preserve target's current value
                    if "eid" in site_feature["properties"]:
                        del site_feature["properties"]["eid"]

        payload = {
            "type": "FeatureCollection",
            "features": [site_feature]
        }
        self.logger.info(f"[DEBUG] V9 Final site payload: {json.dumps(payload)[:1000]}...")
        try:
            self._make_request("PUT", endpoint, payload)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise
        return site_id

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        """
        Get a site by its FID.
        
        Args:
            site_fid: The site FID
            
        Returns:
            A SiteDTO object
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}"
        data = self._make_request("GET", endpoint)
        try:
            # Create a site DTO with the required fields explicitly set
            if "type" in data and data["type"] == "FeatureCollection" and "features" in data:
                if len(data["features"]) > 0:
                    feature = data["features"][0]
                    if "properties" in feature:
                        props = feature["properties"]
                        # Ensure required fields are present
                        if "fid" not in props or props["fid"] is None:
                            props["fid"] = site_fid  # Use the requested FID if missing
                        if "name" not in props or props["name"] is None:
                            props["name"] = f"Site {site_fid}"  # Use a default name if missing
                        if "typeCode" not in props or props["typeCode"] is None:
                            props["typeCode"] = "site-outline"  # Use default typeCode if missing
                        # Create a new site DTO with the fixed properties
                        site = SiteDTO(
                            fid=props["fid"],
                            name=props["name"],
                            typeCode=props["typeCode"],
                            extraData=props.get("extra", {})
                        )
                        # Add optional fields if present
                        if "eid" in props:
                            site.eid = props["eid"]
                        if "sid" in props:
                            site.sid = props["sid"]
                        return site
            # If we can't extract the site directly, try the normal parsing
            site = SiteDTO.from_api_json(data)
            return site
        except ValidationError as e:
            self.logger.error(f"Validation error parsing site {site_fid}: {str(e)}")
            raise V9ApiError(f"Failed to parse site: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing site {site_fid}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise V9ApiError(f"Failed to parse site: {str(e)}")

    def update_site_extra_data(self, site_fid: str, extra_data: Dict[str, Any]) -> bool:
        """
        Update the extra data for a site by updating the entire site.
        
        Args:
            site_fid: The FID of the site to update
            extra_data: The extra data to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the current site data
            endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}"
            current_site_data = self._make_request("GET", endpoint)
            
            if not current_site_data or "features" not in current_site_data:
                self.logger.error(f"Failed to get current site data for {site_fid}")
                return False
            
            # Find the site feature
            site_feature = None
            for feature in current_site_data["features"]:
                if feature.get("properties", {}).get("typeCode") == "site-outline":
                    site_feature = feature
                    break
            
            if not site_feature:
                self.logger.error(f"No site-outline feature found in current site data for {site_fid}")
                return False
            
            # Update the extra data in the feature
            if "properties" not in site_feature:
                site_feature["properties"] = {}
            
            site_feature["properties"]["extra"] = extra_data
            
            # Create the update payload
            payload = {
                "type": "FeatureCollection",
                "features": [site_feature]
            }
            
            # Make the update request
            self.logger.info(f"Updating site extra data for {site_fid}")
            self._make_request("PUT", endpoint, payload)
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating site extra data: {str(e)}")
            return False
