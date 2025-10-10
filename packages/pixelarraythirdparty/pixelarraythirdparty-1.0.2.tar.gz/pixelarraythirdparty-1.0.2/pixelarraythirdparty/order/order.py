from pixelarraythirdparty.client import Client


class OrderManager(Client):
    def create_order(
        self,
        product_name: str,
        product_id: str,
        amount: float,
        body: str,
        remark: str,
        payment_channel: str,
    ):
        data = {
            "product_name": product_name,
            "product_id": product_id,
            "amount": amount,
            "body": body,
            "remark": remark,
            "payment_channel": payment_channel,
        }
        data, success = self._request("POST", "/api/orders/create", json=data)
        if not success:
            return {}, False
        return data, True

    def list_order(
        self,
        page: int = 1,
        page_size: int = 10,
        payment_status: str = None,
        order_no: str = None,
    ):
        params = {
            "page": page,
            "page_size": page_size,
            "payment_status": payment_status,
            "order_no": order_no,
        }
        data, success = self._request("GET", "/api/orders/list", params=params)
        if not success:
            return {}, False
        return data, True

    def get_order_detail(self, order_no: str):
        data, success = self._request("GET", f"/api/orders/{order_no}")
        if not success:
            return {}, False
        return data, True

    def update_order(
        self,
        order_no: str,
        payment_status: str,
        wx_order_no: str,
        transaction_id: str,
        openid: str,
        trade_type: str,
        bank_type: str,
        fee_type: str,
        is_subscribe: str,
        time_end: str,
        remark: str,
    ):
        data = {
            "payment_status": payment_status,
            "wx_order_no": wx_order_no,
            "transaction_id": transaction_id,
            "openid": openid,
            "trade_type": trade_type,
            "bank_type": bank_type,
            "fee_type": fee_type,
            "is_subscribe": is_subscribe,
            "time_end": time_end,
            "remark": remark,
        }
        data, success = self._request("PUT", f"/api/orders/{order_no}", json=data)
        if not success:
            return {}, False
        return data, True

    def delete_order(self, order_no: str):
        data, success = self._request("DELETE", f"/api/orders/{order_no}")
        if not success:
            return {}, False
        return data, True

    def get_order_stats(self):
        data, success = self._request("GET", "/api/orders/stats/summary")
        if not success:
            return {}, False
        return data, True
