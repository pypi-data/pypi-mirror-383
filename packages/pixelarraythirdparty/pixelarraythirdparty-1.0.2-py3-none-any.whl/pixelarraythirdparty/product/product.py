from pixelarraythirdparty.client import Client


class ProductManager(Client):
    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        data, success = self._request("POST", "/api/products/create", json=data)
        if not success:
            return {}, False
        return data, True

    def list_product(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None,
        category: str = None,
        name: str = None,
    ):
        params = {
            "page": page,
            "page_size": page_size,
            "status": status,
            "category": category,
            "name": name,
        }
        if status is not None:
            params["status"] = status
        if category is not None:
            params["category"] = category
        if name is not None:
            params["name"] = name
        data, success = self._request("GET", "/api/products/list", params=params)
        if not success:
            return {}, False
        return data, True

    def get_product_detail(self, product_id: str):
        data, success = self._request("GET", f"/api/products/{product_id}")
        if not success:
            return {}, False
        return data, True

    def update_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        data, success = self._request("PUT", f"/api/products/{product_id}", json=data)
        if not success:
            return {}, False
        return data, True

    def delete_product(self, product_id: str):
        data, success = self._request("DELETE", f"/api/products/{product_id}")
        if not success:
            return {}, False
        return data, True

    def get_product_categories(self):
        data, success = self._request("GET", "/api/products/categories/list")
        if not success:
            return {}, False
        return data, True
