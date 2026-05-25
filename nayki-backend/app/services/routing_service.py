import uuid
from datetime import UTC, datetime

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import CoverageStatus
from app.domain.models import RouteEvaluation
from app.integrations.google_routes_client import GoogleRoutesClient
from app.integrations.graphhopper_client import GraphHopperClient
from app.repositories import routes_repo, safety_repo
from app.schemas.routes import (
    EvaluatedRouteDetail,
    RouteCompareRequest,
    RouteComparisonResponse,
    RouteGeometry,
    RouteSafetyBreakdownResponse,
)
from app.services import safety_engine


class RoutingService:
    """Service to generate route candidates, compute dynamic safety factors, and persist evaluations."""

    def __init__(self):
        self.graphhopper_client = GraphHopperClient()
        self.google_routes_client = GoogleRoutesClient()

    async def compare_routes(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None,
        request: RouteCompareRequest,
    ) -> RouteComparisonResponse:
        """Fetch candidate routes from routing systems, perform safety engine metrics, and store evaluation."""
        if not self.graphhopper_client.is_enabled():
            raise RuntimeError(
                "Routing service is currently degraded: GraphHopper integration is disabled."
            )

        origin_coords = (request.origin.lat, request.origin.lng)
        dest_coords = (request.destination.lat, request.destination.lng)

        # 1. Fetch candidate routing instructions from GraphHopper
        try:
            candidates = await self.graphhopper_client.get_candidate_routes(
                origin_coords, dest_coords
            )
        except Exception as e:
            raise RuntimeError(
                "Routing service is currently degraded: GraphHopper is offline. "
                f"Details: {e!s}"
            )

        if not candidates:
            raise ValueError(
                "No paths found between the specified origin and destination."
            )

        # 2. Extract intersection cell lists for all candidate routes
        all_cells = set()
        for cand in candidates:
            cells = safety_engine.extract_h3_cells_for_route(cand["geometry"])
            all_cells.update(cells)

        # 3. Retrieve localized safety evidence for all cells
        evidence_items = []
        if all_cells:
            evidence_items = (
                await safety_repo.get_safety_evidence_by_h3_indices(
                    db, list(all_cells)
                )
            )

        departure_time = request.departure_time or datetime.now(UTC)

        # 4. Evaluate safety scores for each route option
        evaluated_details = []
        for cand in candidates:
            evaluation = safety_engine.evaluate_route(
                cand["geometry"],
                departure_time=departure_time,
                evidence_items=evidence_items,
            )

            geom = RouteGeometry(
                type=cand["geometry"].get("type", "LineString"),
                coordinates=cand["geometry"].get("coordinates", []),
            )

            detail = EvaluatedRouteDetail(
                route_type=cand["route_type"],
                distance_meters=cand["distance_meters"],
                duration_seconds=cand["duration_seconds"],
                geometry=geom,
                instructions=cand["instructions"],
                safety_score=evaluation["safety_score"],
                confidence_level=evaluation["confidence_level"],
                risk_level=evaluation["risk_level"],
                risk_reasons=evaluation["risk_reasons"],
            )
            evaluated_details.append((detail, evaluation))

        # 5. Classify routes (fastest, lower-risk, balanced)
        # Fastest (sorted by duration)
        evaluated_details.sort(key=lambda x: x[0].duration_seconds)
        fastest = evaluated_details[0][0]

        # Lower-risk (sorted by safety score descending, treating null/unavailable as lowest safety)
        evaluated_details.sort(
            key=lambda x: x[0].safety_score if x[0].safety_score is not None else -1.0,
            reverse=True,
        )
        lower_risk = evaluated_details[0][0]

        # Balanced (simple safety score to duration coefficient ratio)
        max_duration = (
            max(x[0].duration_seconds for x in evaluated_details) or 1.0
        )
        evaluated_details.sort(
            key=lambda x: (x[0].safety_score or 0.0)
            + (1.0 - (x[0].duration_seconds / max_duration)),
            reverse=True,
        )
        balanced = evaluated_details[0][0]

        # Overall spatial coverage evaluation
        statuses = [x[1]["coverage_status"] for x in evaluated_details]
        if CoverageStatus.UNAVAILABLE in statuses:
            overall_coverage = CoverageStatus.UNAVAILABLE
        elif CoverageStatus.LIMITED in statuses:
            overall_coverage = CoverageStatus.LIMITED
        elif CoverageStatus.MODERATE in statuses:
            overall_coverage = CoverageStatus.MODERATE
        else:
            overall_coverage = CoverageStatus.STRONG

        # Narrative explanation
        overall_explanation = safety_engine.generate_route_explanation(
            lower_risk.risk_reasons, evaluated_details[0][1]["confidence_score"]
        )

        # 6. Persist evaluation into DB
        eval_id = uuid.uuid4()
        origin_point = from_shape(
            Point(request.origin.lng, request.origin.lat), srid=4326
        )
        dest_point = from_shape(
            Point(request.destination.lng, request.destination.lat), srid=4326
        )

        db_eval = RouteEvaluation(
            id=eval_id,
            user_id=user_id,
            origin=origin_point,
            destination=dest_point,
            selected_route_type="lower_risk",
            fastest_route=fastest.model_dump(),
            lower_risk_route=lower_risk.model_dump(),
            balanced_route=balanced.model_dump(),
            coverage_status=overall_coverage,
            created_at=datetime.now(UTC),
        )

        await routes_repo.create_route_evaluation(db, db_eval)

        return RouteComparisonResponse(
            fastest_route=fastest,
            lower_risk_route=lower_risk,
            balanced_route=balanced,
            coverage_status=overall_coverage,
            explanation=overall_explanation,
            route_evaluation_id=str(eval_id),
        )

    async def get_route_evaluation(
        self, db: AsyncSession, eval_id: uuid.UUID
    ) -> RouteEvaluation | None:
        """Fetch historical route evaluation records."""
        return await routes_repo.get_route_evaluation_by_id(db, eval_id)

    async def get_route_safety_breakdown(
        self, db: AsyncSession, eval_id: uuid.UUID
    ) -> RouteSafetyBreakdownResponse:
        """Generate high-fidelity safety calculations break-down for a stored route evaluation."""
        db_eval = await self.get_route_evaluation(db, eval_id)
        if not db_eval:
            raise ValueError(f"Route evaluation with ID {eval_id} not found.")

        lr_route = db_eval.lower_risk_route or {}
        safety_score = lr_route.get("safety_score")
        risk_reasons = lr_route.get("risk_reasons", [])

        route_risk = 1.0 - safety_score if safety_score is not None else 1.0
        confidence = 0.80 if safety_score is not None else 0.0

        return RouteSafetyBreakdownResponse(
            route_evaluation_id=str(eval_id),
            route_level_risk=route_risk,
            safety_score=safety_score,
            confidence=confidence,
            confidence_level=lr_route.get("confidence_level", "low"),
            coverage_status=db_eval.coverage_status,
            evidence_count=len(risk_reasons),
            risk_reasons=risk_reasons,
            high_risk_segments=[],
        )
