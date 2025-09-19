import json
import os
from pprint import pprint #used to import pretty print function to  print dictionaries in clean ,readable form


def siem_data(filepath: str) -> dict:
    """Loads the SIEM data from a single JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {} 
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        return {}


#  Parser 
def get_intent(query: str) -> str:
    """Parses a userr query to find keywords and determine the intent."""
    query_lower = query.lower()# conv uppr case to lower so that Malware and malware r treated same
    
    if "failed" in query_lower and "login" in query_lower:
        return "find_failed_logins"
    elif "malware" in query_lower:
        return "find_malware"
    elif ("count" in query_lower or "chart" in query_lower) and "host" in query_lower:
        return "count_alerts_by_host"
    else:
        return "unknown"

# main backend logic
def process_query(query: str, siem_data: dict) -> dict:
    """Main function to handle a query using the pre-loaded data."""
    intent = get_intent(query) # to figure out intent
    
    if intent == "unknown":
        return {"error": "Sorry, I could not understand the request."}
        
    data = siem_data.get(intent) # looks up the intent as a key in the  dictionary
    
    if not data:
        return {"error": f"Internal error: No data found for intent '{intent}'."}
        
    return {
        "intent": intent,
        "data": data
    }

# --- Example 
if __name__ == "__main__":
    # 1. Define the path to your single JSON file
    JSON_FILEPATH = "queries.json"
    
    # 2. Load all data from the file
    siem_data = siem_data(JSON_FILEPATH)
    
    # Only proceed if data was loaded successfully
    if siem_data:
        print("✅ Fake SIEM data loaded successfully!")
        print(f"   Loaded intents: {list(siem_data.keys())}\n")
        print("--- Testing Backend Logic ---\n")
        
        # 3. Process queries using the loaded data
        sample_queries = [
            "Show me all failed logins from today",
            "Was there any malware activity?",
            "Create a chart of alerts by host",
        ]
        
        for q in sample_queries:
            print(f"USER QUERY: '{q}'")
            result = process_query(q, siem_data)
            print("BACKEND RESPONSE:")
            pprint(result)
            print("-" * 30)