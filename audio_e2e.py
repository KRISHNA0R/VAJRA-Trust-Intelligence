"""VAJRA audio end-to-end test: login -> analyze 4 clips -> history -> PDF -> ZIP."""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def login():
    req = urllib.request.Request(
        BASE + "/api/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["access_token"]


def analyze(token, path, mime):
    with open(path, "rb") as f:
        payload = f.read()
    boundary = "BOUNDARY12345"
    body = (
        ("--" + boundary + "\r\n").encode()
        + ('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % path).encode()
        + ("Content-Type: %s\r\n\r\n" % mime).encode()
        + payload
        + ("\r\n--" + boundary + "--\r\n").encode()
    )
    req = urllib.request.Request(
        BASE + "/api/audio/analyze", data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary,
                 "Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def get(token, path, out=None):
    req = urllib.request.Request(BASE + path,
                                 headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
        if out:
            with open(out, "wb") as f:
                f.write(data)
        return r.status, data


if __name__ == "__main__":
    tok = login()
    print("login OK", flush=True)
    last_job = None
    for path, expected in [("test_real_en.wav", "REAL"), ("test_real_hi.wav", "REAL"),
                           ("test_fake_en.wav", "FAKE"), ("test_fake_hi.wav", "FAKE")]:
        d = analyze(tok, path, "audio/wav")
        ok = "OK " if d.get("verdict") == expected else "MISS"
        print(f"{ok} API {path}: verdict={d.get('verdict')} "
              f"fake_prob={d.get('fake_prob')} dur={d.get('duration_sec')}s "
              f"(expected {expected})", flush=True)
        last_job = d.get("job_id")
    s, hist = get(tok, "/api/history?limit=5")
    print("history:", s, flush=True)
    s, _ = get(tok, f"/api/reports/{last_job}/pdf", out="report_audio_test.pdf")
    import os
    print("audio pdf:", s, os.path.getsize("report_audio_test.pdf"), flush=True)
    with open("report_audio_test.pdf", "rb") as f:
        print("pdf magic:", f.read(5), flush=True)
    s, _ = get(tok, f"/api/reports/{last_job}/zip", out="report_audio_test.zip")
    print("audio zip:", s, os.path.getsize("report_audio_test.zip"), flush=True)
    with open("report_audio_test.zip", "rb") as f:
        print("zip magic:", f.read(4), flush=True)
    print("DONE", flush=True)
