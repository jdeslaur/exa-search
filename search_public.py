import requests
import json
import os
from datetime import datetime, timedelta
import argparse
import csv
import concurrent.futures

# Configuration
workingDir = "/Your/directory"
tokenUrl = "https://api.us-west.exabeam.cloud/auth/v1/token"
tokenFile = "/FILE/PATH/token_cache.json"
tokenExpiration = timedelta(hours=4)
searchUrl = "https://api.us-west.exabeam.cloud/search/v2/events"
now = datetime.now()
yesterday = now - timedelta(days=1)
yesterday_formatted = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")
now_formatted = now.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_cached_token():
    if os.path.exists(tokenFile):
        with open(tokenFile, 'r+') as file:
            tokenData = json.load(file)
            tokenTime = datetime.fromisoformat(tokenData['timestamp'])
            if datetime.now() - tokenTime < tokenExpiration:
                return tokenData['token']
    return None

def cache_token(token):
    with open(tokenFile, 'w') as file:
        tokenData = {
            'token': token,
            'timestamp': datetime.now().isoformat()
        }
        json.dump(tokenData, file)

def generate_new_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": "token_id",
        "client_secret": "token_secret"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(tokenUrl, json=payload, headers=headers)
    response.raise_for_status()
    token = response.json()
    bearer_token = token['access_token']
    cache_token(bearer_token)
    return bearer_token

def get_bearer_token():
    token = get_cached_token()
    if token is None:
        token = generate_new_token()
    return token

bearer_token = get_bearer_token()
print(bearer_token)

def parse_args():
    parser = argparse.ArgumentParser(description="A script that accepts query arguments, primarily for data validation.")
    parser.add_argument('-f', '--field', type=str, required=True, help='The type of query to run, which field are we going to validate')
    return parser.parse_args()

def run_query(payload, headers, output_file, fieldnames):
    response = requests.post(searchUrl, json=payload, headers=headers)
    response.raise_for_status()
    rawData = response.json()
    with open(output_file, 'w+', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if isinstance(rawData, dict) and 'rows' in rawData:
            for data in rawData['rows']:
                writer.writerow(data)

def main():
    args = parse_args()
    common_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {bearer_token}"
    }
    tasks = []

    if args.field == 'user':
        user_payload = {
            "limit": 1000,
            "groupBy": ["user","msg_type"],
            "orderBy": ["count DESC"],
            "distinct": True,
            "filter": "NOT user: null AND user: RGX(\"[^A-Za-z0-9]\") AND NOT user: RGX(\"\.|\$$\")",
            "fields": ["user", "count(user) as count", "msg_type"],
            "startTime": f"{yesterday_formatted}",
            "endTime": f"{now_formatted}"
        }
        tasks.append(("user_field_output", user_payload, ["user", "count", "msg_type"]))

    if args.field == 'dest_ip':
        dest_ip_payload = {
            "limit": 1000,
            "groupBy": ["dest_ip","msg_type"],
            "orderBy": ["count DESC"],
            "distinct": True,
            "filter": "NOT dest_ip: null AND NOT dest_ip: RGX(\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\") AND NOT (dest_ip: RGX(\"([0-9a-fA-F]{1,4}:)\") OR dest_ip: WLD(\"::\"))",
            "fields": ["dest_ip", "count(dest_ip) as count", "msg_type"],
            "startTime": f"{yesterday_formatted}",
            "endTime": f"{now_formatted}"
        }
        tasks.append(("dest_ip_field_output", dest_ip_payload, ["dest_ip", "count", "msg_type"]))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_query, payload, common_headers, f"{workingDir}/{name}_{now_formatted}.txt", fieldnames)
            for name, payload, fieldnames in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
