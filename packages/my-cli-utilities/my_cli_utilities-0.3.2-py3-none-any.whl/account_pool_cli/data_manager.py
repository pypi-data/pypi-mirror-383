# -*- coding: utf-8 -*-

"""DataManager handling data fetching, caching, and configuration."""

import json
import logging
import time
import os
from typing import Dict, List, Any, Optional

from returns.result import Result, Success, Failure
from rich.console import Console

from my_cli_utilities_common.config import BaseConfig
from my_cli_utilities_common.http_helpers import make_sync_request
from .result_types import AppError, network_error, data_not_found_error, cache_error

logger = logging.getLogger(__name__)
console = Console()


class Config(BaseConfig):
    """Configuration constants for Account Pool CLI."""
    BASE_URL = "https://account-pool-mthor.int.rclabenv.com"
    ACCOUNTS_ENDPOINT = f"{BASE_URL}/accounts"
    ACCOUNT_SETTINGS_ENDPOINT = f"{BASE_URL}/accountSettings"
    CACHE_FILE = BaseConfig.get_cache_file("account_pool_cli_cache.json")
    DISPLAY_WIDTH = 80


class CacheManager:
    """Manages a simple file-based cache for account types."""

    @staticmethod
    def save_cache(account_types: List[str], filter_keyword: Optional[str], brand: str) -> None:
        """Saves the list of account types to a cache file."""
        cache_data = {"account_types": account_types, "filter_keyword": filter_keyword, "brand": brand}
        try:
            with open(Config.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    @staticmethod
    def load_cache() -> Optional[Dict[str, Any]]:
        """Loads account types from the cache file."""
        if not os.path.exists(Config.CACHE_FILE):
            return None
        try:
            with open(Config.CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to load cache: {e}")
            return None
            
    @staticmethod
    def get_account_type_by_index(index: int) -> Optional[str]:
        """Retrieves a single account type from the cache by its 1-based index."""
        cache_data = CacheManager.load_cache()
        if not cache_data:
            console.print("❌ No cached account types found. Please run 'ap types' first.", style="red")
            return None
        
        account_types = cache_data.get("account_types", [])
        if 1 <= index <= len(account_types):
            return account_types[index - 1]
        
        console.print(f"❌ Index {index} is out of range. Available indices: 1-{len(account_types)}", style="red")
        console.print("💡 Please run 'ap types' again to refresh the cache.")
        return None
            
    @staticmethod
    def clear_cache() -> bool:
        """Clears the cache file."""
        try:
            if os.path.exists(Config.CACHE_FILE):
                os.remove(Config.CACHE_FILE)
                console.print("✅ Cache cleared successfully", style="green")
                return True
            console.print("ℹ️ No cache file to clear.", style="yellow")
            return False
        except Exception as e:
            console.print(f"❌ Failed to clear cache: {e}", style="red")
            return False


class DataManager:
    """Manages data fetching and caching with robust error handling."""

    def __init__(self, cache_timeout: int = 300):
        self._settings_cache: List[Dict] = []
        self._settings_cache_time = 0
        self.cache_timeout = cache_timeout

    def _is_cache_expired(self) -> bool:
        """Check if the cache has expired."""
        return time.time() - self._settings_cache_time > self.cache_timeout

    def _fetch_from_api(self, endpoint: str, params: Dict = None) -> Result[Any, AppError]:
        """Fetch data from an API endpoint with synchronous, robust error handling."""
        try:
            response_data = make_sync_request(endpoint, params=params)
            if response_data is None:
                return Failure(network_error("No response from API", f"Endpoint: {endpoint}"))
            return Success(response_data)
        except Exception as e:
            logger.error(f"API request to {endpoint} failed: {e}")
            return Failure(network_error("API request failed", str(e)))

    def get_account_settings(self, brand: str, force_refresh: bool = False) -> Result[List[Dict], AppError]:
        """Get account settings, using cache if available."""
        if not force_refresh and self._settings_cache and not self._is_cache_expired():
            return Success(self._settings_cache)

        return self._fetch_from_api(
            Config.ACCOUNT_SETTINGS_ENDPOINT, params={"brand": brand}
        ).bind(self._process_and_cache_settings)

    def _process_and_cache_settings(self, response_data: Dict) -> Result[List[Dict], AppError]:
        """Process the API response and cache the account settings."""
        settings = response_data.get("accountSettings")
        if settings is None:
            return Failure(data_not_found_error("'accountSettings' not found in API response"))
        
        self._settings_cache = settings
        self._settings_cache_time = time.time()
        logger.debug(f"Cached {len(settings)} account settings.")
        return Success(settings)

    def get_accounts(self, env_name: str, account_type: str) -> Result[List[Dict], AppError]:
        """Fetch a list of accounts matching the criteria."""
        params = {"envName": env_name, "accountType": account_type}
        return self._fetch_from_api(Config.ACCOUNTS_ENDPOINT, params=params).bind(
            self._extract_accounts_from_response
        )

    def get_account_by_id(self, account_id: str, env_name: str) -> Result[Dict, AppError]:
        """Fetch a single account by its ID."""
        url = f"{Config.ACCOUNTS_ENDPOINT}/{account_id}"
        params = {"envName": env_name}
        return self._fetch_from_api(url, params=params)

    def get_all_accounts_for_env(self, env_name: str) -> Result[List[Dict], AppError]:
        """Fetch all accounts for a specific environment."""
        params = {"envName": env_name}
        return self._fetch_from_api(Config.ACCOUNTS_ENDPOINT, params=params).bind(
            self._extract_accounts_from_response
        )

    def _extract_accounts_from_response(self, response_data: Dict) -> Result[List[Dict], AppError]:
        """Extracts the list of accounts from the API response."""
        accounts = response_data.get("accounts")
        if accounts is None:
            return Failure(data_not_found_error("'accounts' field not found in response"))
        return Success(accounts) 