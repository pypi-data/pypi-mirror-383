"""Voucher management for RadiusDesk API."""

import logging
from typing import Dict, Any, Union
import requests

from .exceptions import APIError
from .utils import build_headers, generate_timestamp

logger = logging.getLogger(__name__)


class VoucherManager:
    """Manages voucher operations for RadiusDesk API."""

    def __init__(self, base_url: str, auth_manager, cloud_id: str):
        """
        Initialize VoucherManager.

        Args:
            base_url: Base URL of the RadiusDesk instance
            auth_manager: AuthManager instance for authentication
            cloud_id: Cloud ID for the RadiusDesk instance
        """
        self.base_url = base_url.rstrip('/')
        self.auth_manager = auth_manager
        self.cloud_id = cloud_id

    def list(self, limit: int = 100, page: int = 1, start: int = 0) -> Dict[str, Any]:
        """
        Fetch vouchers from the RadiusDesk API.

        Args:
            limit: Maximum number of vouchers to fetch
            page: Page number
            start: Starting offset

        Returns:
            Dictionary containing vouchers data

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}/vouchers/index.json"
        token = self.auth_manager.token

        params = {
            "_dc": generate_timestamp(),
            "page": page,
            "start": start,
            "limit": limit,
            "token": token,
            "sel_language": "4_4",
            "cloud_id": self.cloud_id,
        }
        cookies = {"Token": token}

        logger.info(f"Fetching vouchers from {url}")

        try:
            response = requests.get(
                url,
                headers=build_headers(),
                params=params,
                cookies=cookies,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            status_code = None
            if hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', None)
            raise APIError(f"Failed to fetch vouchers: {str(e)}", status_code=status_code)

    def get_details(self, voucher_code: str, limit: int = 150) -> Dict[str, Any]:
        """
        Fetch the usage details and statistics for a specific voucher.

        This method retrieves accounting records (radaccts) for a voucher,
        which includes connection history, data usage, and session information.

        Args:
            voucher_code: The voucher code to fetch details for
            limit: Maximum number of records to fetch

        Returns:
            Dictionary containing voucher usage details and statistics

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}/radaccts/index.json"
        token = self.auth_manager.token

        params = {
            "_dc": generate_timestamp(),
            "username": voucher_code,
            "page": 1,
            "start": 0,
            "limit": limit,
            "token": token,
            "sel_language": "4_4",
            "cloud_id": self.cloud_id,
        }
        cookies = {"Token": token}

        logger.info(f"Fetching voucher details for {voucher_code}")

        try:
            response = requests.get(
                url,
                headers=build_headers(),
                params=params,
                cookies=cookies,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            status_code = None
            if hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', None)
            raise APIError(f"Failed to fetch voucher details: {str(e)}", status_code=status_code)

    def create(
        self,
        realm_id: int,
        profile_id: int,
        quantity: int = 1,
        never_expire: bool = True,
        extra_name: str = "",
        extra_value: str = ""
    ) -> Union[str, Dict[str, Any]]:
        """
        Create voucher(s) in the RadiusDesk API.

        Args:
            realm_id: ID of the realm
            profile_id: ID of the profile
            quantity: Number of vouchers to create
            never_expire: Whether vouchers should never expire
            extra_name: Extra name field
            extra_value: Extra value field

        Returns:
            If quantity=1, returns the voucher code (string)
            If quantity>1, returns the full response (dict)

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}/vouchers/add.json"
        token = self.auth_manager.token

        payload = {
            "single_field": "true",
            "realm_id": realm_id,
            "profile_id": profile_id,
            "quantity": quantity,
            "never_expire": "on" if never_expire else "off",
            "extra_name": extra_name,
            "extra_value": extra_value,
            "token": token,
            "sel_language": "4_4",
            "cloud_id": self.cloud_id,
        }

        cookies = {"Token": token}

        logger.info(f"Creating {quantity} voucher(s)")

        try:
            response = requests.post(
                url,
                headers=build_headers(),
                data=payload,
                cookies=cookies,
                timeout=30
            )
            response.raise_for_status()

            response_data = response.json()

            if quantity == 1:
                voucher = response_data["data"][0]['name']
                logger.info(f"Created voucher: {voucher}")
                return voucher
            else:
                logger.info(f"Created {quantity} vouchers")
                return response_data

        except requests.exceptions.RequestException as e:
            status_code = None
            if hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', None)
            raise APIError(f"Failed to create voucher: {str(e)}", status_code=status_code)
        except (KeyError, IndexError) as e:
            raise APIError(f"Invalid response format: {str(e)}")
