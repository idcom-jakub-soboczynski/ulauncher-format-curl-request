import re
import json
import subprocess
from typing import Optional, Tuple

def is_curl_request(text: str) -> bool:
    """Check if the text starts with 'curl'."""
    return text.strip().startswith('curl')

def extract_request_url(curl_command: str) -> str:
    """Extract the URL from the cURL command."""
    url_match = re.search(r"'(https?://[^']+)'", curl_command)
    if url_match:
        return url_match.group(1)
    return ""

def extract_request_method(curl_command: str) -> str:
    """Extract the HTTP method from the cURL command."""
    # Check for explicit method with -X flag
    method_match = re.search(r'-X\s+(\w+)', curl_command)
    if method_match:
        return method_match.group(1)

    # If there's data being sent, it's likely POST
    if any(flag in curl_command for flag in ['--data-raw', '--data', '-d', '--data-binary']):
        return "POST"

    # Default to GET
    return "GET"

def extract_payload(curl_command: str) -> str:
    """Extract the payload from the cURL command."""
    payload_match = re.search(r"--data-raw\s+'([^']*)'", curl_command)
    if payload_match:
        return payload_match.group(1)
    return ""

def format_json(json_str: str) -> str:
    """Format JSON string with proper indentation."""
    if not json_str:
        return ""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json_str

def execute_curl_command(curl_command: str) -> str:
    """Execute the cURL command and return the response."""
    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.SubprocessError:
        return ""

def format_curl_request(curl_command: str) -> Tuple[bool, str]:
    """Format a cURL request and return the formatted output."""
    if not is_curl_request(curl_command):
        return False, "Error: Not a cURL request."

    request_url = extract_request_url(curl_command)
    request_method = extract_request_method(curl_command)
    payload = extract_payload(curl_command)

    # Format payload if present
    formatted_payload = format_json(payload)

    # Execute the curl command
    response = execute_curl_command(curl_command)
    formatted_response = format_json(response)

    # Format the result
    result = f"""Request URL: {request_url}
Request Method: {request_method}

Payload: {formatted_payload}

Response: {formatted_response}"""

    return True, result

def main():
    # For testing purposes
    test_curl = """curl 'https://api.example.com/data' -X POST --data-raw '{"key": "value"}'"""
    success, result = format_curl_request(test_curl)
    print(result)

if __name__ == "__main__":
    main()
