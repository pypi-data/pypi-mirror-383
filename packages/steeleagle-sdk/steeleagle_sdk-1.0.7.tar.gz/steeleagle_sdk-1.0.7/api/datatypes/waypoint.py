from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel
import logging

from ...dsl.compiler.registry import register_data
from ...tools.map.partitioner.algos.corridor import CorridorPartition
from ...tools.map.partitioner.algos.edge import EdgePartition
from ...tools.map.partitioner.algos.survey import SurveyPartition
from ...tools.map.partitioner.geopoints import GeoPoints
from ...tools.map.partitioner.utils import parse_kml_file

logger = logging.getLogger(__name__)

MISSION_MAP: Any = None

class RelativePoint(BaseModel):
    pass 


@register_data
class Waypoints(BaseModel):
    alt: float
    area: str
    algo: Literal["edge", "survey", "corridor"]
    spacing: Optional[float] = None
    angle_degrees: Optional[float] = None
    trigger_distance: Optional[float] = None

    def calculate(self) -> Dict[str, List[Dict[str, float]]]:
        if MISSION_MAP is None:
            raise ValueError("MISSION_MAP is not set. Set map_mod.MISSION_MAP to a fastkml.kml.KML before calling calculate().")

        raw_map: Dict[str, GeoPoints] = parse_kml_file(MISSION_MAP)
        if not raw_map:
            logger.warning("No valid areas found in mission map (KML).")
            return {}

        if self.area not in raw_map:
            available = ", ".join(sorted(raw_map.keys()))
            raise ValueError(f"Area '{self.area}' not found in mission map. Available areas: {available}")

        raw: GeoPoints = raw_map[self.area]
        if len(raw) < 3:
            logger.warning("Area %s has < 3 points; skipping.", self.area)
            return {}

        # Choose partitioner
        if self.algo == "edge":
            partition = EdgePartition()
        elif self.algo == "survey":
            if self.spacing is None or self.angle_degrees is None or self.trigger_distance is None:
                raise ValueError("For 'survey' algo, 'spacing', 'angle_degrees', and 'trigger_distance' must be set.")
            partition = SurveyPartition(
                spacing=self.spacing,
                angle_degrees=self.angle_degrees,
                trigger_distance=self.trigger_distance,
            )
        elif self.algo == "corridor":
            if self.spacing is None or self.angle_degrees is None:
                raise ValueError("For 'corridor' algo, 'spacing' and 'angle_degrees' must be set.")
            partition = CorridorPartition(
                spacing=self.spacing,
                angle_degrees=self.angle_degrees,
            )
        else:
            raise ValueError("Unknown algo '%s'. Expected one of: 'edge', 'survey', 'corridor'." % self.algo)

        origin_wgs = raw.centroid()
        projected = raw.convert_to_projected()
        poly = projected.to_polygon()

        parts_m = partition.generate_partitioned_geopoints(poly)  
        parts_wgs = [GeoPoints(p).inverse_project_from(origin_wgs) for p in parts_m]

        # Flatten segments to per-point waypoints
        waypoints: List[Dict[str, float]] = []
        for gp in parts_wgs:
            for lon, lat in gp:
                waypoints.append({"lat": float(lat), "lon": float(lon), "alt": float(self.alt)})

        logger.info(
            "Partitioned '%s' with %s: %d segment(s), %d point(s)",
            self.area, self.algo, len(parts_wgs), len(waypoints),
        )

        return {self.area: waypoints}
