#!/usr/bin/env python3
import argparse
import requests
import json
import sys
from typing import Dict, Any, List, Optional

class DarkOSINT:
    def __init__(self, base_url: str = "http://172.174.228.24:10506/v1/proxy"):
        self.base_url = base_url
        self.client_key = "demo-client-key-1"
    
    def search_mobile(self, mobile_number: str) -> Optional[List[Dict[str, Any]]]:
        """
        Search for mobile number information via the API
        """
        try:
            params = {
                'term': mobile_number,
                'type': 'mobile',
                'client': self.client_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return None

# Make the class easily importable
dark_osint = DarkOSINT()

def main():
    parser = argparse.ArgumentParser(description='Fast OSINT Mobile Lookup')
    parser.add_argument('-s', '--search', required=True, help='Mobile number to search for')
    
    args = parser.parse_args()
    results = dark_osint.search_mobile(args.search)
    
    if results is not None:
        print(json.dumps(results, indent=2))
    else:
        print(json.dumps({"error": "Failed to fetch data"}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
