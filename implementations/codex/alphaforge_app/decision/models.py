from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _reject_boolean_number(value):
    """Reject booleans before Pydantic can coerce them to zero or one."""
    if isinstance(value, bool):
        raise ValueError("Une valeur numérique ne peut pas être un booléen.")
    return value


NumericFloat = Annotated[float, BeforeValidator(_reject_boolean_number)]
NumericInt = Annotated[int, BeforeValidator(_reject_boolean_number)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Holding(StrictModel):
    ticker: str = Field(min_length=1, max_length=40)
    weight: NumericFloat = Field(ge=0, le=1)


class Scenario(StrictModel):
    id: str
    label: str
    returns: dict[str, NumericFloat]
    kind: Literal["hypothetical"]
    horizon_months: NumericFloat = Field(gt=0)


class Assumption(StrictModel):
    id: str
    text: str
    origin: Literal["assumed", "declared"]


class Clarification(StrictModel):
    field: str
    question: str
    blocking: bool


class Comparison(StrictModel):
    ticker: str
    target_weight: NumericFloat = Field(ge=0, le=1)


class HistoricalWindow(StrictModel):
    kind: Literal["all_common_available", "specified_window"]
    start_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class HistoricalPolicy(StrictModel):
    redistribution: Literal["proportional_other_holdings", "other"]
    window: HistoricalWindow


class ProblemSpec(StrictModel):
    decision_type: Literal["reserve_allocation", "historical_comparison", "explanation", "unsupported"] = "unsupported"
    question: str = ""
    currency: Literal["CAD"] | None = None
    capital_cad: NumericFloat | None = Field(default=None, gt=0, le=1e12)
    holdings: list[Holding] = Field(default_factory=list, max_length=100)
    withdrawal_cad: NumericFloat | None = Field(default=None, ge=0)
    withdrawal_months: NumericFloat | None = Field(default=None, gt=0)
    horizon_years: NumericFloat | None = Field(default=None, gt=0)
    max_asset_weights: dict[str, NumericFloat] = Field(default_factory=dict)
    scenario_loss_limit_cad: NumericFloat | None = Field(default=None, ge=0)
    scenarios: list[Scenario] = Field(default_factory=list, max_length=30)
    objective: Literal["minimize_reallocated_capital", "compare_historical", "explain", "unknown"] = "unknown"
    comparison: Comparison | None = None
    historical_policy: HistoricalPolicy | None = None
    reserve_policy: Literal["abstract_nominal", "real_instrument_unknown"] | None = None
    knowledge_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    assumptions: list[Assumption] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    clarifications: list[Clarification] = Field(default_factory=list)


class NewDossier(StrictModel):
    prompt: str = Field(min_length=1, max_length=16000)
    facts: dict = Field(default_factory=dict)
    use_ai: bool = True


class RevisionRequest(StrictModel):
    message: str = Field(min_length=1, max_length=16000)
    changes: dict = Field(default_factory=dict)
    intent: Literal["replace", "variant"] = "replace"
    base_revision: NumericInt = Field(ge=0)


class DisplayRequest(StrictModel):
    view_ref: str


class Write(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_.-]+$")
    type: Literal["assertion", "problem", "research", "analysis", "view", "review", "questions"]
    content: dict
    input_refs: list[str]


class ChangeSet(StrictModel):
    run_id: str
    task_id: str
    role: Literal["agent0", "agent1", "agent2", "agent3"]
    read_set: list[str]
    writes: list[Write]
    next_role: Literal["agent0", "agent1", "agent2", "agent3"] | None = None
    status: Literal["running", "waiting", "complete"] = "running"
    reason: str


OWNERS = {
    "agent0": {"assertion", "problem", "questions"},
    "agent1": {"research", "review", "questions"},
    "agent2": {"analysis", "review", "questions"},
    "agent3": {"view", "review", "questions"},
}
