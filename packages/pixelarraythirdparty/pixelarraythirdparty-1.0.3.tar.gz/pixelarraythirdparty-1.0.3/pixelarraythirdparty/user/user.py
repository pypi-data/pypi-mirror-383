import aiohttp
from typing import Optional
from pixelarraythirdparty.client import Client


class UserManager(Client):
    def list_user(
        self,
        page: int = 1,
        page_size: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ):
        params = {"page": page, "page_size": page_size}
        if role is not None:
            params["role"] = role
        if is_active is not None:
            params["is_active"] = is_active
        data, success = self._request("GET", "/api/users/list", params=params)
        if not success:
            return {}, False
        return data, True

    def create_user(self, username: str, password: str, email: str, role: str):
        data = {
            "username": username,
            "password": password,
            "email": email,
            "role": role,
        }
        data, success = self._request("POST", "/api/users/create", json=data)
        if not success:
            return {}, False
        return data, True

    def update_user(
        self, user_id: int, username: str, email: str, role: str, is_active: bool
    ):
        data = {
            "username": username,
            "email": email,
            "role": role,
            "is_active": is_active,
        }
        data, success = self._request("PUT", f"/api/users/{user_id}", json=data)
        if not success:
            return {}, False
        return data, True

    def delete_user(self, user_id: int):
        data, success = self._request("DELETE", f"/api/users/{user_id}")
        if not success:
            return {}, False
        return data, True

    def get_user_detail(self, user_id: int):
        data, success = self._request("GET", f"/api/users/{user_id}")
        if not success:
            return {}, False
        return data, True

    def reset_user_password(self, user_id: int, new_password: str):
        data = {"new_password": new_password}
        data, success = self._request(
            "POST", f"/api/users/{user_id}/reset-password", json=data
        )
        if not success:
            return {}, False
        return data, True
