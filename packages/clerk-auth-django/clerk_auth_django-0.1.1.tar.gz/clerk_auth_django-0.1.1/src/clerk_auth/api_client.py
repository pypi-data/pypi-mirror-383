"""API client for Clerk Management API."""

from typing import Any, Dict, List, Optional
import requests

from .utils import get_clerk_config


class ClerkAPIClient:
    """
    Python client for Clerk Management API.

    Provides methods for user management, organization management,
    and metadata operations.

    Usage:
        client = ClerkAPIClient()
        users = client.list_users()
        user = client.get_user('user_123')
        client.update_user_metadata('user_123', {'plan': 'premium'})
    """

    BASE_URL = "https://api.clerk.com/v1"

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize Clerk API client.

        Args:
            secret_key: Clerk secret key (defaults to config value)
        """
        self.secret_key = secret_key or get_clerk_config("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("Clerk secret key is required")

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.secret_key}"})

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Clerk API."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Clerk API request failed: {str(e)}") from e

    # User Management

    def list_users(
        self,
        limit: int = 100,
        offset: int = 0,
        email_address: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all users.

        Args:
            limit: Number of results to return (max 500)
            offset: Offset for pagination
            email_address: Filter by email address

        Returns:
            List of user objects
        """
        params = {"limit": limit, "offset": offset}
        if email_address:
            params["email_address"] = email_address

        response = self._request("GET", "/users", params=params)
        return response.get("data", [])

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user by ID.

        Args:
            user_id: Clerk user ID

        Returns:
            User object
        """
        return self._request("GET", f"/users/{user_id}")

    def update_user_metadata(
        self,
        user_id: str,
        public_metadata: Optional[Dict[str, Any]] = None,
        private_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update user metadata.

        Args:
            user_id: Clerk user ID
            public_metadata: Public metadata (accessible in JWT)
            private_metadata: Private metadata (not in JWT)

        Returns:
            Updated user object
        """
        payload = {}
        if public_metadata is not None:
            payload["public_metadata"] = public_metadata
        if private_metadata is not None:
            payload["private_metadata"] = private_metadata

        return self._request("PATCH", f"/users/{user_id}", json=payload)

    def delete_user(self, user_id: str) -> None:
        """
        Delete user.

        Args:
            user_id: Clerk user ID
        """
        self._request("DELETE", f"/users/{user_id}")

    # Organization Management

    def list_organizations(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List all organizations.

        Args:
            limit: Number of results to return
            offset: Offset for pagination

        Returns:
            List of organization objects
        """
        params = {"limit": limit, "offset": offset}
        response = self._request("GET", "/organizations", params=params)
        return response.get("data", [])

    def get_organization(self, org_id: str) -> Dict[str, Any]:
        """
        Get organization by ID.

        Args:
            org_id: Clerk organization ID

        Returns:
            Organization object
        """
        return self._request("GET", f"/organizations/{org_id}")

    def create_organization(
        self,
        name: str,
        slug: Optional[str] = None,
        public_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create new organization.

        Args:
            name: Organization name
            slug: Organization slug (URL-friendly identifier)
            public_metadata: Public metadata

        Returns:
            Created organization object
        """
        payload = {"name": name}
        if slug:
            payload["slug"] = slug
        if public_metadata:
            payload["public_metadata"] = public_metadata

        return self._request("POST", "/organizations", json=payload)

    def update_organization_metadata(
        self,
        org_id: str,
        public_metadata: Optional[Dict[str, Any]] = None,
        private_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update organization metadata.

        Args:
            org_id: Clerk organization ID
            public_metadata: Public metadata
            private_metadata: Private metadata

        Returns:
            Updated organization object
        """
        payload = {}
        if public_metadata is not None:
            payload["public_metadata"] = public_metadata
        if private_metadata is not None:
            payload["private_metadata"] = private_metadata

        return self._request("PATCH", f"/organizations/{org_id}", json=payload)

    def delete_organization(self, org_id: str) -> None:
        """
        Delete organization.

        Args:
            org_id: Clerk organization ID
        """
        self._request("DELETE", f"/organizations/{org_id}")

    # Organization Membership

    def list_organization_memberships(
        self,
        org_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List organization members.

        Args:
            org_id: Clerk organization ID
            limit: Number of results to return
            offset: Offset for pagination

        Returns:
            List of membership objects
        """
        params = {"limit": limit, "offset": offset}
        response = self._request(
            "GET", f"/organizations/{org_id}/memberships", params=params
        )
        return response.get("data", [])

    def create_organization_membership(
        self,
        org_id: str,
        user_id: str,
        role: str = "member",
    ) -> Dict[str, Any]:
        """
        Add user to organization.

        Args:
            org_id: Clerk organization ID
            user_id: Clerk user ID
            role: Organization role (e.g., 'admin', 'member')

        Returns:
            Created membership object
        """
        payload = {"user_id": user_id, "role": role}
        return self._request(
            "POST", f"/organizations/{org_id}/memberships", json=payload
        )

    def update_organization_membership(
        self,
        org_id: str,
        user_id: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Update organization member role.

        Args:
            org_id: Clerk organization ID
            user_id: Clerk user ID
            role: New role

        Returns:
            Updated membership object
        """
        payload = {"role": role}
        return self._request(
            "PATCH", f"/organizations/{org_id}/memberships/{user_id}", json=payload
        )

    def delete_organization_membership(self, org_id: str, user_id: str) -> None:
        """
        Remove user from organization.

        Args:
            org_id: Clerk organization ID
            user_id: Clerk user ID
        """
        self._request("DELETE", f"/organizations/{org_id}/memberships/{user_id}")
