import requests

def test_func():
    # This should be flagged by b-side-effects-02 (Network)
    response = requests.get("https://example.com")
    print(response.status_code)
