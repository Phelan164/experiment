import json
import requests
from time import sleep
import urllib3

def rest_client():
    # Configure session with longer timeout and SSL verification settings
    session = requests.Session()
    session.timeout = 30
    session.verify = False  # Disable SSL verification - only for testing/development
    
    # Suppress SSL verification warnings - only for testing/development
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        print("REST client ready. Type 'exit' to quit.")
        while True:
            text = input("\nEnter text to send (or 'exit'): ")
            if text.lower() == 'exit':
                break

            try:
                # Make the request
                response = session.post(
                    "http://localhost:8001/api/chat",
                    json={
                        "message": text,
                    },
                    params={"session_id": "34556"},
                    headers={"Content-Type": "application/json"},
                    stream=True  # Enable streaming response
                )
                
                # Check for errors
                response.raise_for_status()

                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            print("Message:", data.get("message", ""))
                        except json.JSONDecodeError as e:
                            print(f"Error decoding response: {e}")
                            continue

            except requests.Timeout:
                print("Request timed out. Please try again.")
            except requests.RequestException as e:
                print(f"Error making request: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

            # Small delay between requests
            sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        session.close()

if __name__ == "__main__":
    rest_client()
