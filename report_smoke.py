"""VAJRA smoke test: history + PDF + ZIP report downloads."""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"
JOB_ID = "trufor_c083431ad498_1791219979"


def login():
    req = urllib.request.Request(
        BASE + "/api/auth/login",
        data=json.dumps(
            {"username": "vajra_tester", "password": "Test1234"}
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["access_token"]


def get(token, path, out=None):
    req = urllib.request.Request(
        BASE + path, headers={"Authorization": "Bearer " + token}
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
        if out:
            with open(out, "wb") as f:
                f.write(data)
        return r.status, data


if __name__ == "__main__":
    tok = login()
    s, hist = get(tok, "/api/history?limit=5")
    h = json.loads(hist)
    jobs = h.get("jobs", h) if isinstance(h, dict) else h
    print("history status:", s, "entries:", len(jobs) if isinstance(jobs, list) else h.keys(), flush=True)
    s, _ = get(tok, f"/api/reports/{JOB_ID}/pdf", out="report_test.pdf")
    import os
    print("pdf status:", s, "size:", os.path.getsize("report_test.pdf"), flush=True)
    with open("report_test.pdf", "rb") as f:
        print("pdf magic:", f.read(5), flush=True)
    s, _ = get(tok, f"/api/reports/{JOB_ID}/zip", out="report_test.zip")
    print("zip status:", s, "size:", os.path.getsize("report_test.zip"), flush=True)
    with open("report_test.zip", "rb") as f:
        print("zip magic:", f.read(4), flush=True)
    print("DONE", flush=True)
