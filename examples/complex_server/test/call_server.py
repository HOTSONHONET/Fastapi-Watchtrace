import requests

urls = [
    "http://127.0.0.1:8000/dashboard/1",
    "http://127.0.0.1:8000/dashboard/1?include_recommendations=true&include_analytics=true",
    "http://127.0.0.1:8000/dashboard/2?include_recommendations=false",
    "http://127.0.0.1:8000/dashboard/3?include_analytics=false",
]

for url in urls:
    resp = requests.get(url, timeout=10)
    print(url)
    print(resp.status_code)
    print(resp.json())
    print("-" * 80)