import os
import urllib.request
import urllib.error
import json

# Disable system proxy settings for localhost (vital for Zscaler/corporate networks)
os.environ['no_proxy'] = 'localhost,127.0.0.1,127.0.0.1:5000,localhost:5000'
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,127.0.0.1:5000,localhost:5000'

proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

API_URL = "https://calculator-server-1gfl.onrender.com"

def send_calculation_request(math_expr, angle_mode="DEG"):
    """
    Sends the math equation to the API server via an HTTP POST request.
    Returns the calculated result string.
    """
    url = f"{API_URL}/calculate"
    payload = {"expression": math_expr, "angle_mode": angle_mode}
    json_data = json.dumps(payload).encode('utf-8')
    
    request = urllib.request.Request(
        url,
        data=json_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            response_json = json.loads(response.read().decode('utf-8'))
            return response_json.get("result", "Error")
    except Exception as e:
        print(f"DEBUG - Calculation request failed: {e}")
        return "Server Offline"

def fetch_history_request():
    """
    Fetches the last 10 calculations from the API server via an HTTP GET request.
    Returns a list of calculation strings.
    """
    url = f"{API_URL}/history"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            response_json = json.loads(response.read().decode('utf-8'))
            return response_json.get("history", [])
    except Exception as e:
        print(f"DEBUG - History request failed: {e}")
        return ["Server Offline"]
