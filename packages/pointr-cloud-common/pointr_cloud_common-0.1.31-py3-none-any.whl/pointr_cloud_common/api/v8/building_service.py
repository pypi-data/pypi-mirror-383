from typing import Dict, Any, List, Optional
import logging

from pointr_cloud_common.dto.v9 import BuildingDTO, LevelDTO
from pointr_cloud_common.dto.v9.validation import ensure_dict, ValidationError
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError


DEFAULT_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[0.0, 0.0], [0.0, 0.001], [0.001, 0.001], [0.001, 0.0], [0.0, 0.0]]],
}


class BuildingApiService(BaseApiService):
    """Service for building-related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def _fetch_source_geometry(
        self, fid: str, site_fid: str, source_api_service: Any
    ) -> Optional[Dict[str, Any]]:
        """Fetch geometry for the given building fid from the source API service."""
        try:
            data = source_api_service._make_request(
                "GET", f"api/v8/buildings/{fid}/draft"
            )
            result = data.get("result", data)
            geometry = result.get("geometry")
            if geometry:
                self.logger.info(
                    f"Successfully retrieved geometry for building {fid} from source API"
                )
                return geometry
            self.logger.warning(
                f"No geometry found for building {fid} in source API"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve geometry for building {fid} from source API: {str(e)}"
            )
        return None

    def _level_from_v8(self, data: Dict[str, Any], site_fid: str, building_fid: str) -> LevelDTO:
        try:
            return LevelDTO(
                fid=str(data.get("levelIndex")),
                name=data.get("levelLongTitle", ""),
                shortName=data.get("levelShortTitle"),
                levelNumber=data.get("levelIndex"),
                typeCode="level-outline",
                sid=site_fid,
                bid=building_fid,
            )
        except ValidationError as e:
            raise V8ApiError(f"Failed to parse level: {str(e)}")

    def _building_from_v8(self, data: Dict[str, Any], site_fid: str) -> BuildingDTO:
        self.logger.info(f"[DEBUG] _building_from_v8 input data: {data}")
        self.logger.info(f"[DEBUG] _building_from_v8 input data keys: {list(data.keys()) if isinstance(data, dict) else 'NOT_A_DICT'}")

        levels = [self._level_from_v8(l, site_fid, str(data.get("buildingInternalIdentifier"))) for l in data.get("levels", [])]
        try:
            building_dto = BuildingDTO(
                fid=str(data.get("buildingInternalIdentifier")),
                name=data.get("buildingTitle", ""),
                typeCode="building-outline",
                sid=site_fid,
                bid=data.get("buildingExternalIdentifier"),
                extraData=ensure_dict(data.get("buildingExtraData"), "buildingExtraData"),
                levels=levels,
            )
            self.logger.info(f"[DEBUG] _building_from_v8 created DTO with bid: {building_dto.bid}")
            return building_dto
        except ValidationError as e:
            raise V8ApiError(f"Failed to parse building: {str(e)}")

    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        endpoint = f"api/v8/sites/{site_fid}/buildings/draft"
        data = self._make_request("GET", endpoint)
        results = data.get("results", []) if isinstance(data, dict) else []
        buildings = [self._building_from_v8(b, site_fid) for b in results]
        return buildings

    def get_building_by_fid(self, site_fid: str, building_fid: str) -> BuildingDTO:
        endpoint = f"api/v8/buildings/{building_fid}/draft"
        data = self._make_request("GET", endpoint)
        self.logger.info(f"[DEBUG] get_building_by_fid raw response: {data}")
        result = data.get("result", data)
        self.logger.info(f"[DEBUG] get_building_by_fid result field: {result}")
        building_dto = self._building_from_v8(result, site_fid)
        self.logger.info(f"[DEBUG] get_building_by_fid parsed DTO: {building_dto}")
        return building_dto

    def create_building(
        self,
        site_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
    ) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(building.fid, site_fid, source_api_service)
            if fetched:
                geometry = fetched
                
        payload = {
            "buildingTitle": building.name,
            "buildingExternalIdentifier": building.bid,
            "buildingExtraData": building.extraData,
            "geometry": geometry,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        
        endpoint = f"api/v8/sites/{site_fid}/buildings"
        
        try:
            data = self._make_request("POST", endpoint, payload)
            result_fid = str(data.get("result", {}).get("buildingInternalIdentifier", ""))
            return result_fid
        except Exception as e:
            print(f"[DEBUG][CREATE_BUILDING] Error creating building: {str(e)}")
            print(f"[DEBUG][CREATE_BUILDING] Error type: {type(e).__name__}")
            raise

    def update_building(
        self,
        site_fid: str,
        building_fid: str,
        building: BuildingDTO,
        source_api_service: Optional[Any] = None,
        migration_options: Optional[Dict[str, Any]] = None,
    ) -> str:
        geometry = DEFAULT_GEOMETRY
        if source_api_service:
            fetched = self._fetch_source_geometry(building.fid, site_fid, source_api_service)
            if fetched:
                geometry = fetched

        # Handle external ID migration options
        migrate_external_id = True  # Default value
        if migration_options:
            migrate_external_id = migration_options.get("migrate_building_external_id", True)
            self.logger.info(f"Migration options received: {migration_options}")
            self.logger.info(f"migrate_building_external_id from options: {migrate_external_id}")

        payload = {
            "buildingTitle": building.name,
            "buildingExtraData": building.extraData,
            "geometry": geometry,
        }

        # Handle external ID migration
        self.logger.info(f"[DEBUG] migrate_external_id: {migrate_external_id}, building.bid: {building.bid}")
        if migrate_external_id and building.bid:
            # When migrating, use source's external ID
            payload["buildingExternalIdentifier"] = building.bid
            self.logger.info(f"[DEBUG] Migrating source building's external ID: {building.bid}")
        elif not migrate_external_id:
            # When not migrating, try to preserve target's existing external ID
            self.logger.info(f"[DEBUG] Attempting to preserve target's existing external ID for building {building_fid}")
            try:
                # Try using the DTO method first, which handles response parsing
                self.logger.info(f"[DEBUG] V8: Trying DTO method for building {building_fid}")
                try:
                    current_building_dto = self.get_building_by_fid(site_fid, building_fid)
                    self.logger.info(f"[DEBUG] V8: DTO method succeeded: {current_building_dto}")
                    if current_building_dto and hasattr(current_building_dto, 'bid') and current_building_dto.bid:
                        payload["buildingExternalIdentifier"] = current_building_dto.bid
                        self.logger.info(f"[DEBUG] V8: Preserving target building's existing external ID from DTO: {current_building_dto.bid}")
                    else:
                        self.logger.info(f"[DEBUG] V8: DTO has no external ID or DTO is None")
                except Exception as dto_error:
                    self.logger.warning(f"[DEBUG] V8: DTO method failed: {str(dto_error)}, trying direct API call")

                    # Fallback to direct API call
                    endpoint = f"api/v8/buildings/{building_fid}/draft"
                    self.logger.info(f"[DEBUG] V8: Fetching from endpoint: {endpoint}")
                    current_data = self._make_request("GET", endpoint)
                    self.logger.info(f"[DEBUG] V8: Raw current data: {current_data}")

                    # Handle different response formats
                    if current_data:
                        self.logger.info(f"[DEBUG] V8: Current data keys: {list(current_data.keys())}")
                        self.logger.info(f"[DEBUG] V8: Current data result field: {current_data.get('result', 'NO_RESULT_FIELD')}")

                        # Check if it's wrapped in a "result" field
                        if "result" in current_data:
                            if current_data["result"]:
                                building_data = current_data["result"]
                                self.logger.info(f"[DEBUG] V8: Using result field: {building_data}")
                            else:
                                self.logger.info(f"[DEBUG] V8: Result field exists but is empty")
                                building_data = current_data  # fallback to entire response
                        else:
                            building_data = current_data
                            self.logger.info(f"[DEBUG] V8: No result field, using entire response")

                        self.logger.info(f"[DEBUG] V8: Building data keys: {list(building_data.keys()) if isinstance(building_data, dict) else 'NOT_A_DICT'}")

                        if isinstance(building_data, dict) and "buildingExternalIdentifier" in building_data:
                            external_id = building_data["buildingExternalIdentifier"]
                            self.logger.info(f"[DEBUG] V8: Found buildingExternalIdentifier: {external_id}")
                            if external_id:
                                payload["buildingExternalIdentifier"] = external_id
                                self.logger.info(f"[DEBUG] V8: Preserving target building's existing external ID: {external_id}")
                            else:
                                self.logger.info(f"[DEBUG] V8: buildingExternalIdentifier is empty/null")
                        else:
                            self.logger.info(f"[DEBUG] V8: No buildingExternalIdentifier field found in building data")
                    else:
                        self.logger.info(f"[DEBUG] V8: No current data received from API")
            except Exception as e:
                self.logger.warning(f"[DEBUG] V8: Failed to get current target building data for external ID preservation: {str(e)}")
                # If we can't fetch the current data, don't set any external ID
                # This preserves whatever is currently in the target

        payload = {k: v for k, v in payload.items() if v is not None}
        self.logger.info(f"[DEBUG] Final V8 building payload: {payload}")
        endpoint = f"api/v8/buildings/{building_fid}"
        self._make_request("PATCH", endpoint, payload)
        return building_fid
