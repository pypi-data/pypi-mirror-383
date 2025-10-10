from pixelarraythirdparty.client import Client


class CeleryManager(Client):
    def get_celery_status(self):
        data, success = self._request("GET", "/api/celery/status")
        if not success:
            return {}, False
        return data, True

    def get_celery_tasks(self):
        data, success = self._request("GET", "/api/celery/tasks")
        if not success:
            return {}, False
        return data, True

    def get_celery_tasks_scheduled(self):
        data, success = self._request("GET", "/api/celery/tasks/scheduled")
        if not success:
            return {}, False
        return data, True

    def get_celery_tasks_detail(self, task_name: str):
        data, success = self._request("GET", f"/api/celery/tasks/{task_name}")
        if not success:
            return {}, False
        return data, True

    def trigger_celery_task(self, task_name: str, args: list, kwargs: dict):
        data, success = self._request(
            "POST",
            f"/api/celery/tasks/{task_name}/trigger",
            json={"args": args, "kwargs": kwargs},
        )
        if not success:
            return {}, False
        return data, True
