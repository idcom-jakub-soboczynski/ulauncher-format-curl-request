import re
import json
import subprocess
from typing import Optional, Tuple
from status_codes import get_status_description

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
    # Support for both --data-raw and -d flags
    payload_patterns = [
        r"--data-raw\s+'([^']*)'",
        r"--data-raw\s+\"([^\"]*)\"",
        r"-d\s+'([^']*)'",
        r"-d\s+\"([^\"]*)\"",
        r"--data\s+'([^']*)'",
        r"--data\s+\"([^\"]*)\"",
    ]

    for pattern in payload_patterns:
        payload_match = re.search(pattern, curl_command)
        if payload_match:
            return payload_match.group(1)
    return ""

def format_json(json_str: str) -> str:
    """Format JSON string with proper indentation."""
    if not json_str or not json_str.strip():
        return ""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        return json_str

def execute_curl_command(curl_command: str) -> Tuple[str, int]:
    """Execute the cURL command and return the response and status code."""
    try:
        # Use %{http_code} for status and separate it with a special delimiter
        delimiter = "===STATUS_CODE==="
        # Add -s for silent mode and format the output to separate response from status
        modified_command = f"{curl_command} -s -w '{delimiter}%{{http_code}}'"
        result = subprocess.run(modified_command, shell=True, capture_output=True, text=True)

        # Split response and status code using the delimiter
        output = result.stdout
        if delimiter in output:
            response, status_part = output.rsplit(delimiter, 1)
            try:
                status_code = int(status_part.strip())
            except ValueError:
                status_code = 0
        else:
            response = output
            status_code = 0

        return response, status_code
    except subprocess.SubprocessError:
        return "", 0

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
    response, status_code = execute_curl_command(curl_command)
    formatted_response = format_json(response)

    # Build the result string conditionally
    result_parts = []

    if request_url:
        result_parts.append(f"Request URL: {request_url}")

    if request_method:
        result_parts.append(f"Request Method: {request_method}")

    # Add status with full description
    if status_code > 0:
        result_parts.append(f"Status: {get_status_description(status_code)}")

    if formatted_payload:
        result_parts.append(f"\nPayload: {formatted_payload}")

    if formatted_response:
        result_parts.append(f"\nResponse: {formatted_response}")

    # Join all parts with newlines
    result = "\n".join(result_parts)

    return True, result

def main():
    # For testing purposes
    test_curl = """curl 'https://api.example.com/data' -X POST --data-raw '{"key": "value"}'"""
    success, result = format_curl_request(test_curl)
    print(result)

if __name__ == "__main__":
    main()
