import httpx
import json

payload = {
    "duration_minutes": 120,
    "people": [
        {
            "name": "Smruti",
            "favourite_movie": "Interstellar — the father daughter story and the scale of space hit differently",
            "mood": "Something recent, last 5 years",
            "vibe": "Serious and emotional"
        },
        {
            "name": "Mana",
            "favourite_movie": "Everything Everywhere All at Once — chaotic but deeply emotional",
            "mood": "Doesn't matter, new or classic both fine",
            "vibe": "Mix of fun and serious"
        },
        {
            "name": "Raj",
            "favourite_movie": "RRR — insane action and the bromance was brilliant",
            "mood": "Something new, last 3 years",
            "vibe": "Fun and high energy"
        }
    ]
}

resp = httpx.post("http://localhost:7070/recommend", json=payload, timeout=120.0)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))