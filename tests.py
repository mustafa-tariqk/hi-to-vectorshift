
import requests


sample_text = "I love FastAPI. It is a great web framework. It is easy to use and fast."
url = "http://localhost:80/analyze"  # replace with your actual URL
params = {
    "text": sample_text,
    "split_size": 5
}

response = requests.post(url, params=params)

print(response.json())