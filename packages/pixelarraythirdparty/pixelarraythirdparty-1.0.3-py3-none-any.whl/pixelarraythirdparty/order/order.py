from pixelarraythirdparty.client import Client


class OrderManager(Client):
    def create_order(
        self,
        product_id: str,
        body: str = None,
        remark: str = None,
        payment_channel: str = "WECHAT",
    ):
        data = {
            "product_id": product_id,
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
        out_trade_no: str = None,
    ):
        params = {
            "page": page,
            "page_size": page_size,
            "payment_status": payment_status,
            "out_trade_no": out_trade_no,
        }
        data, success = self._request("GET", "/api/orders/list", params=params)
        if not success:
            return {}, False
        return data, True

    def get_order_detail(self, out_trade_no: str):
        data, success = self._request("GET", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    def update_order_status(
        self,
        out_trade_no: str,
        payment_status: str,
    ):
        data = {
            "payment_status": payment_status,
        }
        data, success = self._request(
            "PUT", f"/api/orders/{out_trade_no}/status", json=data
        )
        if not success:
            return {}, False
        return data, True

    def delete_order(self, out_trade_no: str):
        data, success = self._request("DELETE", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    def get_order_stats(self):
        data, success = self._request("GET", "/api/orders/stats/summary")
        if not success:
            return {}, False
        return data, True

    def generate_qr_code(
        self,
        out_trade_no: str,
        payment_channel: str = "WECHAT",
    ):
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/generate_qr_code"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/generate_qr_code"
        else:
            raise ValueError("Invalid payment channel")
        data, success = self._request(
            "POST",
            url,
            json={
                "out_trade_no": out_trade_no,
            },
        )
        if not success:
            return {}, False
        return data, True

    def refund_order(self, out_trade_no: str, payment_channel: str = "WECHAT"):
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/refund"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/refund"
        else:
            raise ValueError("Invalid payment channel")
        data, success = self._request(
            "POST",
            url,
            json={"out_trade_no": out_trade_no},
        )
        if not success:
            return {}, False
        return data, True
