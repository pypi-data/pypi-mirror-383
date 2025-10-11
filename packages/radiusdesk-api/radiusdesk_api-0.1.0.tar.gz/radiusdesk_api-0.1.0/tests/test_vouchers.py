"""Integration tests for voucher operations."""

import os
import pytest
from radiusdesk_api import RadiusDeskClient


# Skip all tests if credentials are not provided
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('RADIUSDESK_URL'),
        os.getenv('RADIUSDESK_USERNAME'),
        os.getenv('RADIUSDESK_PASSWORD'),
        os.getenv('RADIUSDESK_CLOUD_ID'),
        os.getenv('RADIUSDESK_REALM_ID'),
        os.getenv('RADIUSDESK_PROFILE_ID')
    ]),
    reason="RadiusDesk credentials not provided in environment variables"
)


@pytest.fixture
def client():
    """Fixture providing an authenticated RadiusDesk client."""
    return RadiusDeskClient(
        base_url=os.getenv('RADIUSDESK_URL'),
        username=os.getenv('RADIUSDESK_USERNAME'),
        password=os.getenv('RADIUSDESK_PASSWORD'),
        cloud_id=os.getenv('RADIUSDESK_CLOUD_ID')
    )


@pytest.fixture
def test_voucher_config():
    """Fixture providing test voucher configuration."""
    return {
        'realm_id': int(os.getenv('RADIUSDESK_REALM_ID')),
        'profile_id': int(os.getenv('RADIUSDESK_PROFILE_ID'))
    }


def test_list_vouchers(client):
    """Test listing vouchers."""
    result = client.vouchers.list(limit=10)
    assert isinstance(result, dict)
    assert 'items' in result or 'data' in result


def test_create_single_voucher(client, test_voucher_config):
    """Test creating a single voucher."""
    voucher = client.vouchers.create(
        realm_id=test_voucher_config['realm_id'],
        profile_id=test_voucher_config['profile_id'],
        quantity=1
    )
    assert isinstance(voucher, str)
    assert len(voucher) > 0


def test_create_multiple_vouchers(client, test_voucher_config):
    """Test creating multiple vouchers."""
    result = client.vouchers.create(
        realm_id=test_voucher_config['realm_id'],
        profile_id=test_voucher_config['profile_id'],
        quantity=3
    )
    assert isinstance(result, dict)
    assert 'data' in result


def test_get_voucher_details(client, test_voucher_config):
    """Test getting voucher details and usage statistics."""
    # First create a voucher
    voucher_code = client.vouchers.create(
        realm_id=test_voucher_config['realm_id'],
        profile_id=test_voucher_config['profile_id'],
        quantity=1
    )

    # Get its details (includes usage statistics)
    details = client.vouchers.get_details(voucher_code)
    assert isinstance(details, dict)


def test_list_vouchers_with_pagination(client):
    """Test listing vouchers with pagination parameters."""
    result = client.vouchers.list(limit=5, page=1, start=0)
    assert isinstance(result, dict)
