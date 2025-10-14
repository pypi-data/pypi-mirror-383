from typing import Dict, Any, List
import json
import logging
from pointr_cloud_common.dto.v9.building_dto import BuildingDTO
from pointr_cloud_common.dto.v9.create_response_dto import CreateResponseDTO
from pointr_cloud_common.dto.v9.validation import ValidationError
from pointr_cloud_common.api.v9.base_service import BaseApiService, V9ApiError

class BuildingApiService(BaseApiService):
    """Service for building-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        """
        Get all buildings for a site.
        
        Args:
            site_fid: The site FID
            
        Returns:
            A list of BuildingDTO objects
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings"
        data = self._make_request("GET", endpoint)
        try:
            return BuildingDTO.list_from_api_json(data)
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse buildings: {str(e)}")
    
    def get_building_by_fid(self, site_fid: str, building_fid: str) -> BuildingDTO:
        """
        Get a building by its FID.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
        
        Returns:
            A BuildingDTO object
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved building data for {building_fid}")
        
        try:
            # Create a building DTO with the required fields explicitly set
            if "type" in data and data["type"] == "FeatureCollection" and "features" in data:
                if len(data["features"]) > 0:
                    feature = data["features"][0]
                    if "properties" in feature:
                        props = feature["properties"]
                        
                        # Ensure required fields are present
                        if "fid" not in props or props["fid"] is None:
                            props["fid"] = building_fid  # Use the requested FID if missing
                            
                        if "name" not in props or props["name"] is None:
                            props["name"] = f"Building {building_fid}"  # Use a default name if missing
                            
                        if "typeCode" not in props or props["typeCode"] is None:
                            props["typeCode"] = "building-outline"  # Use default typeCode if missing
                        
                        # Extract extra data and add buildingType to it if present
                        extra_data = props.get("extra", {})
                        if not isinstance(extra_data, dict):
                            extra_data = {}
                            
                        # If buildingType exists, add it to extraData
                        if "buildingType" in props:
                            extra_data["buildingType"] = props["buildingType"]
                            
                        # Create a new building DTO with the fixed properties
                        building = BuildingDTO(
                            fid=props["fid"],
                            name=props["name"],
                            typeCode=props["typeCode"],
                            sid=props.get("sid", site_fid),  # Use site_fid if sid is missing
                            extraData=extra_data
                        )
                        
                        # Add optional fields if present
                        if "bid" in props:
                            building.bid = props["bid"]
                            
                        return building
        
            # If we can't extract the building directly, try the normal parsing
            return BuildingDTO.from_api_json(data)
        except ValidationError as e:
            self.logger.error(f"Validation error parsing building {building_fid}: {str(e)}")
            raise V9ApiError(f"Failed to parse building: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing building {building_fid}: {str(e)}")
            raise V9ApiError(f"Failed to parse building: {str(e)}")
    
    def create_building(self, site_fid: str, building: BuildingDTO, source_api_service=None) -> str:
        """
        Create a building in the target environment.
        
        Args:
            site_fid: The site FID
            building: The building DTO to create
            source_api_service: Optional source API service to fetch geometry data from
            
        Returns:
            The FID of the created building
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings"
        
        # Get the building data from the source environment
        building_feature = None
        
        # If a source API service is provided, use it to fetch the source building data
        if source_api_service:
            try:
                self.logger.info(f"Fetching source building data for {building.fid} from source environment")
                source_building_data = source_api_service._make_request(
                    "GET", 
                    f"api/v9/content/draft/clients/{source_api_service.client_id}/sites/{site_fid}/buildings/{building.fid}"
                )
                
                # Extract the building feature from the source data
                if source_building_data and "features" in source_building_data:
                    for feature in source_building_data["features"]:
                        if feature.get("properties", {}).get("typeCode") == "building-outline":
                            building_feature = feature
                            self.logger.info(f"Successfully retrieved geometry for building {building.fid} from source environment")
                            break
            except Exception as e:
                self.logger.error(f"Failed to retrieve source building data from source environment: {str(e)}")
        
        # If we couldn't find a building feature, create a minimal one
        if not building_feature:
            self.logger.warning(f"No building geometry found for building {building.fid}, creating minimal geometry")
            
            # Get buildingType from extraData if available, otherwise use default
            building_type = building.extraData.get("buildingType", "office")
            
            # Create a minimal building feature with the data we have
            building_feature = {
                "type": "Feature",
                "properties": {
                    "typeCode": "building-outline",
                    "name": building.name,
                    "fid": building.fid,
                    "sid": site_fid,
                    "buildingType": building_type,
                    "extra": building.extraData
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
            if hasattr(building, 'bid') and building.bid:
                building_feature["properties"]["bid"] = building.bid
        
        # Create a new feature collection with just the building feature
        payload = {
            "type": "FeatureCollection",
            "features": [building_feature]
        }
        
        self.logger.info(f"Creating building with payload: {json.dumps(payload)[:1000]}...")
        data = self._make_request("POST", endpoint, payload)
        try:
            return CreateResponseDTO.from_api_json(data).fid
        except ValidationError as e:
            raise V9ApiError(f"Failed to parse create response: {str(e)}")
    
    def update_building(self, site_fid: str, building_fid: str, building: BuildingDTO, source_api_service=None, migration_options=None) -> str:
        """
        Update a building in the target environment.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            building: The building DTO with updated data
            source_api_service: Optional source API service to fetch geometry data from
            
        Returns:
            The FID of the updated building
        """
        endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}"
        
        # Get the source building data to extract geometry
        building_feature = None
        
        # If a source API service is provided, use it to fetch the source building data
        if source_api_service:
            try:
                self.logger.info(f"Fetching source building data for {building.fid} from source environment")
                source_building_data = source_api_service._make_request(
                    "GET", 
                    f"api/v9/content/draft/clients/{source_api_service.client_id}/sites/{site_fid}/buildings/{building.fid}"
                )
                
                # Extract the building feature from the source data
                if source_building_data and "features" in source_building_data:
                    for feature in source_building_data["features"]:
                        if feature.get("properties", {}).get("typeCode") == "building-outline":
                            building_feature = feature
                            # Update the feature with the target building ID
                            feature["properties"]["fid"] = building_fid
                            self.logger.info(f"Successfully retrieved geometry for building {building.fid} from source environment")
                            break
            except Exception as e:
                self.logger.error(f"Failed to retrieve source building data from source environment: {str(e)}")
        
        if not building_feature:
            self.logger.error(f"No building-outline feature found in source data for building {building.fid}")
            raise V9ApiError(f"No building-outline feature found in source data for building {building.fid}")
        
        # Handle external ID migration options
        if migration_options:
            migrate_external_id = migration_options.get("migrate_building_external_id", True)

            if not migrate_external_id:
                # When not migrating, try to preserve target's existing external ID
                self.logger.info(f"[DEBUG] V9: Attempting to preserve target's existing external ID for building {building_fid}")
                try:
                    # Get the current target building data to preserve its external ID
                    # For V9, use the building-specific endpoint
                    features_endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}"
                    self.logger.info(f"[DEBUG] V9: Fetching from endpoint: {features_endpoint}")
                    current_feature_data = self._make_request("GET", features_endpoint)
                    self.logger.info(f"[DEBUG] V9: Raw current feature data: {current_feature_data}")

                    if current_feature_data:
                        # Handle different response formats for V9
                        if "features" in current_feature_data:
                            features = current_feature_data["features"]
                        elif isinstance(current_feature_data, dict) and any("type" in str(v) for v in current_feature_data.values()):
                            # Might be a single feature response
                            features = [current_feature_data]
                        else:
                            features = []

                        self.logger.info(f"[DEBUG] V9: Features array: {features}")

                        for feature in features:
                            if feature.get("properties", {}).get("typeCode") == "building-outline":
                                current_eid = feature.get("properties", {}).get("eid")
                                self.logger.info(f"[DEBUG] V9: Found eid in target: {current_eid}")
                                if current_eid:
                                    # Preserve the target's existing external ID
                                    building_feature["properties"]["eid"] = current_eid
                                    self.logger.info(f"[DEBUG] V9: Preserving target building's existing external ID: {current_eid}")
                                else:
                                    # Remove eid if target doesn't have one
                                    if "eid" in building_feature["properties"]:
                                        del building_feature["properties"]["eid"]
                                    self.logger.info(f"[DEBUG] V9: Target building has no external ID to preserve")
                                break
                        else:
                            self.logger.info(f"[DEBUG] V9: No building-outline feature found in target data")
                    else:
                        self.logger.info(f"[DEBUG] V9: No feature data found in target building")
                except Exception as e:
                    self.logger.warning(f"[DEBUG] V9: Failed to get current target building data for external ID preservation: {str(e)}")
                    # If we can't fetch the current data, remove eid to preserve target's current value
                    if "eid" in building_feature["properties"]:
                        del building_feature["properties"]["eid"]

        # Create a new feature collection with just the building feature
        payload = {
            "type": "FeatureCollection",
            "features": [building_feature]
        }

        self.logger.info(f"[DEBUG] V9 Final building payload: {json.dumps(payload)[:1000]}...")
        self._make_request("PUT", endpoint, payload)
        return building_fid

    def update_building_extra_data(self, site_fid: str, building_fid: str, extra_data: Dict[str, Any]) -> bool:
        """
        Update the extra data for a building by updating the entire building.
        
        Args:
            site_fid: The site FID
            building_fid: The building FID
            extra_data: The extra data to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the current building data
            endpoint = f"api/v9/content/draft/clients/{self.client_id}/sites/{site_fid}/buildings/{building_fid}"
            current_building_data = self._make_request("GET", endpoint)
            
            if not current_building_data or "features" not in current_building_data:
                self.logger.error(f"Failed to get current building data for {building_fid}")
                return False
            
            # Find the building feature
            building_feature = None
            for feature in current_building_data["features"]:
                if feature.get("properties", {}).get("typeCode") == "building-outline":
                    building_feature = feature
                    break
            
            if not building_feature:
                self.logger.error(f"No building-outline feature found in current building data for {building_fid}")
                return False
            
            # Update the extra data in the feature
            if "properties" not in building_feature:
                building_feature["properties"] = {}
            
            building_feature["properties"]["extra"] = extra_data
            
            # Create the update payload
            payload = {
                "type": "FeatureCollection",
                "features": [building_feature]
            }
            
            # Make the update request
            self.logger.info(f"Updating building extra data for {building_fid}")
            self._make_request("PUT", endpoint, payload)
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating building extra data: {str(e)}")
            return False
