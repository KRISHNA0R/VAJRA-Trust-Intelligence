"""Final audio verification: Dhwani adapter on real EN/HI vs fake EN/HI.

Fixtures: test_real_{en,hi}.wav = genuine FLEURS speech;
          test_fake_{en,hi}.wav = MMS-TTS synthesized speech.
No server needed. Expected: 4/4 OK.
"""
from app.adapters.audio_adapter import AudioSpoofAdapter

a = AudioSpoofAdapter(model_dir="models/audio_dhwani")
print("model:", a.get_model_info()["model_name"], flush=True)

fails = 0
for path, expected in [("test_real_en.wav", "REAL"), ("test_real_hi.wav", "REAL"),
                       ("test_fake_en.wav", "FAKE"), ("test_fake_hi.wav", "FAKE")]:
    with open(path, "rb") as f:
        r = a.analyze(f.read(), path)
    ok = r.get("verdict") == expected
    fails += not ok
    print(f"{'OK ' if ok else 'MISS'} {path}: verdict={r.get('verdict')} "
          f"fake_prob={r.get('fake_prob')} dur={r.get('duration_sec')}s "
          f"(expected {expected})", flush=True)
print("RESULT:", "PASS 4/4" if fails == 0 else f"FAIL ({fails} misses)", flush=True)
