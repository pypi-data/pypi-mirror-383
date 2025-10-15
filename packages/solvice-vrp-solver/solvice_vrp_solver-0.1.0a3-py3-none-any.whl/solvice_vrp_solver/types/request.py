# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .job import Job
from .options import Options
from .weights import Weights
from .._models import BaseModel
from .relation import Relation
from .resource import Resource

__all__ = ["Request", "CustomDistanceMatrices"]


class CustomDistanceMatrices(BaseModel):
    matrix_service_url: Optional[str] = FieldInfo(alias="matrixServiceUrl", default=None)
    """Optional URL for external distance matrix service endpoint.

    If not provided, uses the default system service.
    """

    profile_matrices: Optional[Dict[str, Dict[str, str]]] = FieldInfo(alias="profileMatrices", default=None)
    """Map of vehicle profile names (CAR, BIKE, TRUCK) to time slice hour mappings.

    Each time slice hour maps to a matrix ID that should be fetched from the
    distance matrix service. Time slice hours correspond to: 6=MORNING_RUSH,
    9=MORNING, 12=MIDDAY, 14=AFTERNOON, 16=EVENING_RUSH, 20=NIGHT.
    """


class Request(BaseModel):
    jobs: List[Job]
    """List of jobs/tasks to be assigned to resources.

    Each job specifies service requirements, location, time constraints, duration,
    and resource preferences. Jobs represent the work that needs to be scheduled and
    optimized. At least one job is required, with a maximum of 10,000 jobs per
    request.
    """

    resources: List[Resource]
    """
    List of available resources (vehicles, drivers, workers) that can be assigned to
    perform jobs. Each resource defines their working schedules, location
    constraints, capacity limits, and capabilities. At least one resource is
    required, with a maximum of 2000 resources per request.
    """

    custom_distance_matrices: Optional[CustomDistanceMatrices] = FieldInfo(alias="customDistanceMatrices", default=None)
    """
    Custom distance matrix configuration for multi-profile and multi-slice scenarios
    """

    hook: Optional[str] = None
    """
    Optional webhook URL that will receive a POST request with the job ID when the
    optimization is complete. This enables asynchronous processing where you can
    submit a request and be notified when results are ready, rather than waiting for
    the synchronous response.
    """

    label: Optional[str] = None

    options: Optional[Options] = None
    """Options to tweak the routing engine"""

    relations: Optional[List[Relation]] = None

    weights: Optional[Weights] = None
    """OnRoute Weights"""
