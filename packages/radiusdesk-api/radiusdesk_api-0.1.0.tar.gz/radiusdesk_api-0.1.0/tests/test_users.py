"""Integration tests for user operations."""

import os
import pytest
import time
from radiusdesk_api import RadiusDeskClient


# Skip all tests if credentials are not provided
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('RADIUSDESK_URL'),
        os.getenv('RADIUSDESK_USERNAME'),
        os.getenv('RADIUSDESK_PASSWORD'),
        os.getenv('RADIUSDESK_CLOUD_ID'),
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
def test_user_config():
    """Fixture providing test user configuration."""
    return {
        'profile_id': int(os.getenv('RADIUSDESK_PROFILE_ID')),
        'realm_id': int(os.getenv('RADIUSDESK_REALM_ID'))
    }


def test_list_users(client):
    """Test listing permanent users."""
    result = client.users.list(limit=10)
    assert isinstance(result, dict)


def test_create_permanent_user(client, test_user_config):
    """Test creating a permanent user."""
    # Generate unique username using timestamp
    username = f"test_user_{int(time.time())}"
    password = "testpassword123"

    result = client.users.create(
        username=username,
        password=password,
        realm_id=test_user_config['realm_id'],
        profile_id=test_user_config['profile_id'],
        name="Test",
        surname="User",
        email="test@example.com"
    )
    assert isinstance(result, dict)


def test_create_user_with_minimal_params(client, test_user_config):
    """Test creating a user with only required parameters."""
    username = f"minimal_user_{int(time.time())}"
    password = "password123"

    result = client.users.create(
        username=username,
        password=password,
        realm_id=test_user_config['realm_id'],
        profile_id=test_user_config['profile_id']
    )
    assert isinstance(result, dict)


def test_list_users_with_pagination(client):
    """Test listing users with pagination parameters."""
    result = client.users.list(limit=5, page=1, start=0)
    assert isinstance(result, dict)


def test_add_data_topup(client, test_user_config):
    """Test adding data top-up to a permanent user."""
    # First create a user
    username = f"data_test_user_{int(time.time())}"
    password = "password123"

    user = client.users.create(
        username=username,
        password=password,
        realm_id=test_user_config['realm_id'],
        profile_id=test_user_config['profile_id']
    )

    # Extract user ID from response
    user_id = None
    if isinstance(user, dict):
        user_id = user.get('data', {}).get('id') or user.get('id')

    if user_id:
        # Add data top-up
        result = client.users.add_data(
            user_id=user_id,
            amount=2,
            unit="gb",
            comment="Test data top-up"
        )
        assert isinstance(result, dict)
        assert result.get('success') is True or 'data' in result


def test_add_time_topup(client, test_user_config):
    """Test adding time top-up to a permanent user."""
    # First create a user
    username = f"time_test_user_{int(time.time())}"
    password = "password123"

    user = client.users.create(
        username=username,
        password=password,
        realm_id=test_user_config['realm_id'],
        profile_id=test_user_config['profile_id']
    )

    # Extract user ID from response
    user_id = None
    if isinstance(user, dict):
        user_id = user.get('data', {}).get('id') or user.get('id')

    if user_id:
        # Add time top-up
        result = client.users.add_time(
            user_id=user_id,
            amount=60,
            unit="minutes",
            comment="Test time top-up"
        )
        assert isinstance(result, dict)
        assert result.get('success') is True or 'data' in result


def test_add_data_topup_to_existing_user(client):
    """Test adding data top-up to an existing user."""
    # Get list of users
    users = client.users.list(limit=1)

    if users.get('items') and len(users['items']) > 0:
        user_id = users['items'][0]['id']

        # Add data top-up
        result = client.users.add_data(
            user_id=user_id,
            amount=1,
            unit="gb",
            comment="Integration test data top-up"
        )
        assert isinstance(result, dict)


def test_add_time_topup_to_existing_user(client):
    """Test adding time top-up to an existing user."""
    # Get list of users
    users = client.users.list(limit=1)

    if users.get('items') and len(users['items']) > 0:
        user_id = users['items'][0]['id']

        # Add time top-up
        result = client.users.add_time(
            user_id=user_id,
            amount=30,
            unit="minutes",
            comment="Integration test time top-up"
        )
        assert isinstance(result, dict)
