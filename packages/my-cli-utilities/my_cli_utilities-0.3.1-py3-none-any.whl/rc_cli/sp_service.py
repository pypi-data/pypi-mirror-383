# -*- coding: utf-8 -*-

"""Service Parameter (SP) client service for RC CLI."""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
from .sp_models import ServiceParameter, ServiceParameterValue, SPResult, SPConfig
from my_cli_utilities_common.config import BaseConfig

logger = logging.getLogger(__name__)


class SPClientError(Exception):
    """Base exception for SP client errors."""
    pass


class SPConnectionError(SPClientError):
    """Exception raised when connection to SP service fails."""
    pass


class SPNotFoundError(SPClientError):
    """Exception raised when requested resource is not found."""
    pass


class SPService:
    """Service for interacting with Service Parameter API."""
    
    def __init__(self):
        """Initialize SP service with configuration."""
        self.gitlab_token: Optional[str] = None
        self.timeout = SPConfig.DEFAULT_TIMEOUT
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = SPConfig.CACHE_TTL
        
    def _get_gitlab_token(self) -> str:
        """Get GitLab token from environment variable."""
        token = os.environ.get('GITLAB_TOKEN')
        if not token:
            raise SPClientError(
                "GitLab token not found. Please set GITLAB_TOKEN environment variable."
            )
        return token
    
    async def get_all_service_parameters(self) -> SPResult:
        """
        Get all service parameter definitions from GitLab.
        
        Returns:
            SPResult containing all service parameters
        """
        try:
            # Get GitLab token if not already cached
            if not self.gitlab_token:
                self.gitlab_token = self._get_gitlab_token()
            
            url = f"{SPConfig.GITLAB_BASE_URL}/projects/{SPConfig.GITLAB_PROJECT_ID}/repository/files/{SPConfig.GITLAB_FILE_PATH}/raw"
            params = {"ref": SPConfig.GITLAB_BRANCH}
            headers = {"PRIVATE-TOKEN": self.gitlab_token}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                assembly_data = response.json()
                service_parameters = assembly_data.get("service-parameters", {})
                
                logger.info(f"Retrieved {len(service_parameters)} service parameters")
                
                return SPResult(
                    success=True,
                    data=service_parameters,
                    count=len(service_parameters)
                )
                
        except httpx.TimeoutException as e:
            return SPResult(
                success=False,
                error_message=f"Request timeout: {e}"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return SPResult(
                    success=False,
                    error_message="Service parameters not found in GitLab"
                )
            return SPResult(
                success=False,
                error_message=f"HTTP error {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            return SPResult(
                success=False,
                error_message=f"Request failed: {e}"
            )
        except Exception as e:
            return SPResult(
                success=False,
                error_message=f"Unexpected error: {e}"
            )
    
    async def get_service_parameter_value(self, sp_id: str, account_id: str) -> SPResult:
        """
        Get service parameter value for a specific account.
        
        Args:
            sp_id: Service parameter ID
            account_id: Account ID
            
        Returns:
            SPResult containing SP value information
        """
        try:
            url = f"{SPConfig.INTAPI_BASE_URL}/restapi/v1.0/internal/service-parameter/{sp_id}"
            params = {"accountId": account_id}
            headers = {
                "Authorization": SPConfig.INTAPI_AUTH_HEADER,
                "RCBrandId": SPConfig.INTAPI_BRAND_ID
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                sp_data = response.json()
                
                logger.info(f"Retrieved SP {sp_id} value for account {account_id}: {sp_data.get('value')}")
                
                return SPResult(
                    success=True,
                    data=sp_data,
                    count=1
                )
                
        except httpx.TimeoutException as e:
            return SPResult(
                success=False,
                error_message=f"Request timeout: {e}"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return SPResult(
                    success=False,
                    error_message=f"Service parameter {sp_id} or account {account_id} not found"
                )
            return SPResult(
                success=False,
                error_message=f"HTTP error {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            return SPResult(
                success=False,
                error_message=f"Request failed: {e}"
            )
        except Exception as e:
            return SPResult(
                success=False,
                error_message=f"Unexpected error: {e}"
            )
    
    async def search_service_parameters(self, query: str) -> SPResult:
        """
        Search service parameters by description.
        
        Args:
            query: Search query string
            
        Returns:
            SPResult containing matching service parameters
        """
        try:
            # Get all service parameters first
            all_sps_result = await self.get_all_service_parameters()
            if not all_sps_result.success:
                return all_sps_result
            
            all_sps = all_sps_result.data
            query_lower = query.lower()
            
            matching_sps = {
                sp_id: description 
                for sp_id, description in all_sps.items()
                if query_lower in description.lower()
            }
            
            logger.info(f"Found {len(matching_sps)} service parameters matching '{query}'")
            
            return SPResult(
                success=True,
                data=matching_sps,
                count=len(matching_sps)
            )
            
        except Exception as e:
            logger.error(f"Error searching service parameters: {e}")
            return SPResult(
                success=False,
                error_message=f"Search failed: {e}"
            )
    
    def format_service_parameter_display(self, sp_id: str, description: str) -> str:
        """Format service parameter for display."""
        # Truncate description if too long
        if len(description) > SPConfig.MAX_DESCRIPTION_LENGTH:
            description = description[:SPConfig.MAX_DESCRIPTION_LENGTH - 3] + "..."
        
        return f"  {sp_id:<20} {description}"
    
    def format_sp_value_display(self, sp_data: Dict[str, Any]) -> str:
        """Format service parameter value for display."""
        sp_id = sp_data.get('id', 'N/A')
        value = sp_data.get('value', 'N/A')
        account_id = sp_data.get('account_id', 'N/A')
        
        return f"  SP ID: {sp_id}\n  Value: {value}\n  Account: {account_id}"
    
    def clear_cache(self):
        """Clear the service cache."""
        self._cache.clear()
        logger.info("SP service cache cleared")


# Global SP service instance
sp_service = SPService()
