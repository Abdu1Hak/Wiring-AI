import uuid

from sqlmodel import Session

from app.models import AIWiringPlan
from app.schemas.ai_planner_schema import AIPlannerResponse
from app.schemas.validation_schema import ValidationErrorItem
from app.schemas.wiring_schema import PlanResponse
from app.services.ai_wiring_planner_service import generate_wiring_plan
from app.services.backend_plan_validator_service import validate_ai_plan
from app.services.catalog_service import get_catalog_summary, get_components_context, get_known_rules
from app.services.fallback_service import fallback_message_for_status
from app.services.graph_builder_service import build_graph


async def run_plan_pipeline(
    session: Session,
    project_description: str,
    selected_component_ids: list[str],
    *,
    allow_repair: bool = True,
) -> PlanResponse:
    catalog_context = {
        "selectedComponents": get_components_context(session, selected_component_ids),
        "catalogSummary": get_catalog_summary(session),
        "knownRules": get_known_rules(session),
    }

    plan = await generate_wiring_plan(
        project_description=project_description,
        selected_component_ids=selected_component_ids,
        catalog_context=catalog_context,
    )

    plan_id = str(uuid.uuid4())
    log = AIWiringPlan(
        id=plan_id,
        input_component_ids=selected_component_ids,
        project_description=project_description,
        raw_ai_response_json=plan.model_dump(),
        status=plan.status,
    )
    session.add(log)

    if plan.status != "success":
        session.commit()
        return PlanResponse(
            status=plan.status,
            projectTitle=plan.projectTitle,
            projectSummary=plan.projectSummary,
            aiPlanAccepted=False,
            compatibilityFindings=plan.compatibilityFindings,
            assumptions=plan.assumptions,
            fallbackMessage=fallback_message_for_status(plan.status),
        )

    accepted, errors, warnings = validate_ai_plan(session, plan, selected_component_ids)

    if not accepted and allow_repair and errors:
        repairable = all(e.code in {"PIN_NOT_FOUND", "STEP_REFERENCE_INVALID", "STEP_MISSING_CONNECTION"} for e in errors)
        if repairable:
            plan = await generate_wiring_plan(
                project_description=f"{project_description}\nFix validation errors: {[e.model_dump() for e in errors]}",
                selected_component_ids=selected_component_ids,
                catalog_context=catalog_context,
            )
            accepted, errors, warnings = validate_ai_plan(session, plan, selected_component_ids)

    if not accepted:
        log.status = "no_valid_plan"
        log.errors_json = [e.model_dump() for e in errors]
        session.commit()
        return PlanResponse(
            status="no_valid_plan",
            projectTitle=plan.projectTitle,
            projectSummary=plan.projectSummary,
            aiPlanAccepted=False,
            compatibilityFindings=plan.compatibilityFindings,
            validationErrors=errors,
            warnings=[w.message for w in warnings],
            fallbackMessage=fallback_message_for_status("no_valid_plan"),
        )

    graph_component_ids = list(
        dict.fromkeys(
            selected_component_ids
            + [c.fromComponentId for c in plan.connections]
            + [c.toComponentId for c in plan.connections]
        )
    )
    graph = build_graph(session, graph_component_ids, plan.connections)

    log.status = "success"
    log.validated_plan_json = plan.model_dump()
    session.commit()

    return PlanResponse(
        status="success",
        projectTitle=plan.projectTitle,
        projectSummary=plan.projectSummary,
        aiPlanAccepted=True,
        compatibilityFindings=plan.compatibilityFindings,
        graph=graph,
        connections=plan.connections,
        steps=plan.steps,
        warnings=[w.message for w in warnings],
        assumptions=plan.assumptions,
    )


async def repair_plan(
    session: Session,
    project_description: str,
    selected_component_ids: list[str],
    previous_plan: dict,
    validation_errors: list[ValidationErrorItem],
) -> AIPlannerResponse:
    catalog_context = {
        "selectedComponents": get_components_context(session, selected_component_ids),
        "previousPlan": previous_plan,
        "validationErrors": [e.model_dump() for e in validation_errors],
        "knownRules": get_known_rules(session),
    }
    return await generate_wiring_plan(project_description, selected_component_ids, catalog_context)
