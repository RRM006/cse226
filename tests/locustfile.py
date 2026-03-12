from locust import HttpUser, task, between
import os

TEST_CSV_PATH = "tests/BSCSE/L3/L3_BSCSE_001_complete.csv"


class AuditUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.jwt = os.getenv("TEST_JWT", "")

    @task(3)
    def run_csv_audit(self):
        if not self.jwt:
            return
        with open(TEST_CSV_PATH, "rb") as f:
            self.client.post(
                "/api/v1/audit/csv",
                headers={"Authorization": f"Bearer {self.jwt}"},
                files={"file": f},
                data={"program": "BSCSE", "audit_level": "3"}
            )

    @task(1)
    def get_history(self):
        if not self.jwt:
            return
        self.client.get(
            "/api/v1/history",
            headers={"Authorization": f"Bearer {self.jwt}"}
        )
