# -*- coding: utf-8 -*-

"""
This module contains the core business logic (services) for the Account Pool CLI.
It uses the DataManager to fetch data and processes it according to the
application's rules, returning Result objects to the CLI commands.
"""

import random
from typing import Dict, List, Union, Optional
import typer

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful
from returns.maybe import Some, Nothing

from .data_manager import DataManager, CacheManager
from .display_manager import DisplayManager
from .result_types import AppError, data_not_found_error, validation_error, ResultHandler
from my_cli_utilities_common.config import ValidationUtils


class AccountService:
    """Core service for account management."""
    DEFAULT_ENV_NAME = "webaqaxmn"
    DEFAULT_BRAND = "1210"

    def __init__(self):
        self.data_manager = DataManager()
        self.display = DisplayManager()
        self.handler = ResultHandler()

    def get_random_account(self, account_type: str, env_name: str) -> None:
        """
        Fetches a list of accounts and returns a random one.
        Handles lookup by index from cache.
        """
        final_account_type = account_type
        if account_type.isdigit():
            cached_type = CacheManager.get_account_type_by_index(int(account_type))
            if not cached_type:
                raise typer.Exit(1)
            final_account_type = cached_type

        self.display.display_info(f"Searching for a random '{final_account_type}' account in '{env_name}'...")
        
        result = self.data_manager.get_accounts(env_name, final_account_type).bind(
            self._select_random_account
        )
        account = self.handler.handle_result(result)
        self.display.display_account_info(account)

    def _select_random_account(self, accounts: List[Dict]) -> Result[Dict, AppError]:
        """Selects a random account from a list."""
        if not accounts:
            return Failure(data_not_found_error("No matching accounts found for the given criteria."))
        return Success(random.choice(accounts))

    def get_account_by_id(self, account_id: str, env_name: str) -> None:
        """
        Wrapper for getting an account by its ID.
        """
        self.display.display_info(f"Looking up account by ID: {account_id}...")
        result = self.data_manager.get_account_by_id(account_id, env_name)
        account = self.handler.handle_result(result)
        self.display.display_account_info(account)

    def get_account_by_phone(self, main_number: Union[str, int], env_name: str) -> None:
        """
        Finds a specific account by its main phone number.
        """
        self.display.display_info(f"Looking up account by phone: {main_number}...")
        main_number_str = ValidationUtils.normalize_phone_number(main_number)
        if not main_number_str:
            err = validation_error("Invalid phone number format provided.")
            self.handler.handle_result(Failure(err))
            return

        result = self.data_manager.get_all_accounts_for_env(env_name).bind(
            lambda accounts: self._find_account_by_phone_in_list(accounts, main_number_str)
        )
        account = self.handler.handle_result(result)
        self.display.display_account_info(account)

    def _find_account_by_phone_in_list(self, accounts: List[Dict], phone_number: str) -> Result[Dict, AppError]:
        """Searches for an account by phone number in a list."""
        for account in accounts:
            if account.get("mainNumber") == phone_number:
                return Success(account)
        return Failure(data_not_found_error(f"No account found with phone number: {phone_number}"))

    def list_account_types(self, brand: str, filter_keyword: Optional[str] = None) -> None:
        """
        Gets account types, with an optional filter, and displays them.
        """
        self.display.display_info(f"Fetching account types for brand: {brand}...")
        result = self.data_manager.get_account_settings(brand).map(
            lambda settings: self._filter_settings(settings, filter_keyword)
        )
        
        types = self.handler.handle_result(result)
        
        # Cache the results for the 'get' command by index
        CacheManager.save_cache([t.get("accountType") for t in types], filter_keyword, brand)
        
        self.display.display_account_types(types, brand, filter_keyword)

    def _filter_settings(self, settings: List[Dict], filter_keyword: Optional[str] = None) -> List[Dict]:
        """Filters account settings by a keyword."""
        if not filter_keyword:
            return settings
        
        filter_lower = filter_keyword.lower()
        return [
            s for s in settings 
            if filter_lower in s.get("accountType", "").lower()
        ]

    def manage_cache(self, action: Optional[str]) -> None:
        """Manages the local cache."""
        if action and action.lower() == 'clear':
            CacheManager.clear_cache()
        else:
            self.display.display_cache_status() 