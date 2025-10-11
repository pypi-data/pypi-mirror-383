# -*- coding: utf-8 -*-

"""Data models for Service Parameter (SP) operations."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ServiceParameter:
    """Service parameter definition."""
    
    id: str
    description: str
    possible_values: Optional[str] = None


@dataclass
class ServiceParameterValue:
    """Service parameter value for a specific account."""
    
    id: int
    value: str
    account_id: str


@dataclass
class SPResult:
    """Result wrapper for SP operations."""
    
    success: bool
    data: Optional[Any] = None
    error_message: str = ""
    count: int = 0


class SPConfig:
    """Configuration for SP operations."""
    
    # GitLab API settings
    GITLAB_BASE_URL = "https://git.ringcentral.com/api/v4"
    GITLAB_PROJECT_ID = "24890"
    GITLAB_FILE_PATH = "assembly.json"
    GITLAB_BRANCH = "master"
    
    # Internal API settings
    INTAPI_BASE_URL = "http://intapi-webaqaxmn.int.rclabenv.com:8082"
    INTAPI_AUTH_HEADER = "IntApp cmVsLWFsbC1wZXJtaXNzaW9ucy1uby10aHJvdHRsaW5nOmo2OG05NzlCc20tUHJ5YWFxWUxhMlktdkpvVkRJaVdNajY4bWp4TENkd09QcnlhMEhvT3ZZWS1uby10aHJvdHRsaW5n"
    INTAPI_BRAND_ID = "1210"
    
    # Request settings
    DEFAULT_TIMEOUT = 30.0
    CACHE_TTL = 300  # 5 minutes
    
    # Display settings
    MAX_DESCRIPTION_LENGTH = 80
    SEARCH_RESULTS_LIMIT = 20
