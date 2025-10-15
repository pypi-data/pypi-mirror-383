# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .job_param import JobParam
from .options_param import OptionsParam
from .weights_param import WeightsParam
from .relation_param import RelationParam
from .resource_param import ResourceParam

__all__ = ["VrpSuggestParams", "CustomDistanceMatrices"]


class VrpSuggestParams(TypedDict, total=False):
    jobs: Required[Iterable[JobParam]]
    """List of jobs/tasks to be assigned to resources.

    Each job specifies service requirements, location, time constraints, duration,
    and resource preferences. Jobs represent the work that needs to be scheduled and
    optimized. At least one job is required, with a maximum of 10,000 jobs per
    request.
    """

    resources: Required[Iterable[ResourceParam]]
    """
    List of available resources (vehicles, drivers, workers) that can be assigned to
    perform jobs. Each resource defines their working schedules, location
    constraints, capacity limits, and capabilities. At least one resource is
    required, with a maximum of 2000 resources per request.
    """

    millis: Optional[str]

    custom_distance_matrices: Annotated[Optional[CustomDistanceMatrices], PropertyInfo(alias="customDistanceMatrices")]
    """
    Custom distance matrix configuration for multi-profile and multi-slice scenarios
    """

    hook: Optional[str]
    """
    Optional webhook URL that will receive a POST request with the job ID when the
    optimization is complete. This enables asynchronous processing where you can
    submit a request and be notified when results are ready, rather than waiting for
    the synchronous response.
    """

    label: Optional[str]

    options: Optional[OptionsParam]
    """Options to tweak the routing engine"""

    relations: Optional[Iterable[RelationParam]]

    weights: Optional[WeightsParam]
    """OnRoute Weights"""


class CustomDistanceMatrices(TypedDict, total=False):
    matrix_service_url: Annotated[Optional[str], PropertyInfo(alias="matrixServiceUrl")]
    """Optional URL for external distance matrix service endpoint.

    If not provided, uses the default system service.
    """

    profile_matrices: Annotated[Optional[Dict[str, Dict[str, str]]], PropertyInfo(alias="profileMatrices")]
    """Map of vehicle profile names (CAR, BIKE, TRUCK) to time slice hour mappings.

    Each time slice hour maps to a matrix ID that should be fetched from the
    distance matrix service. Time slice hours correspond to: 6=MORNING_RUSH,
    9=MORNING, 12=MIDDAY, 14=AFTERNOON, 16=EVENING_RUSH, 20=NIGHT.
    """
