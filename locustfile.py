import uuid

from locust import HttpUser, task

sing_in_route = "/api/sign_up/"


class AuthUser(HttpUser):
    @task
    def register_user(self):
        data = {"email": f"user{uuid.uuid4().time}@mail.ru", "password": "superpassword"}
        self.client.post(url=sing_in_route, json=data)
