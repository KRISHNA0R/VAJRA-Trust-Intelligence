"""VAJRA smoke test: end-to-end /detect API call (image)."""
import json
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"


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


def detect(token, path, filename, mime):
    boundary = uuid.uuid4().hex
    with open(path, "rb") as f:
        payload = f.read()
    body = (
        ("--" + boundary + "\r\n").encode()
        + (
            'Content-Disposition: form-data; name="file"; filename="%s"\r\n'
            % filename
        ).encode()
        + ("Content-Type: %s\r\n\r\n" % mime).encode()
        + payload
        + ("\r\n--" + boundary + "--\r\n").encode()
    )
    req = urllib.request.Request(
        BASE + "/detect",
        data=body,
        headers={
            "Content-Type": "multipart/form-data; boundary=" + boundary,
            "Authorization": "Bearer " + token,
        },
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())


if __name__ == "__main__":
    tok = login()
    print("login OK", flush=True)
    d = detect(tok, "test_small.jpg", "test_small.jpg", "image/jpeg")
    print("API_DETECT status:", d.get("status"), flush=True)
    print(
        "decision:",
        d.get("decision"),
        "integrity:",
        round(d.get("integrity", -1), 4),
        flush=True,
    )
    print("job_id:", d.get("job_id"), flush=True)
    print("DONE", flush=True)
