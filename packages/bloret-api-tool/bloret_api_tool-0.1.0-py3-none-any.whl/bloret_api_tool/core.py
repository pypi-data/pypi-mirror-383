"""Core module for Bloret API interactions."""
import json
import requests
from typing import Dict, Any, Optional


class Client:
    """Main client for interacting with the Bloret Launcher API."""
    
    def __init__(self, base_url: str = "https://api.bloret.com", token: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            base_url: The base URL for the API
            token: Authorization token for API requests
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[Any, Any]:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Data to send with the request
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = {"Content-Type": "application/json"}
        
        if method.upper() == "GET":
            response = self.session.get(url, headers=headers)
        elif method.upper() == "POST":
            response = self.session.post(url, headers=headers, data=json.dumps(data or {}))
        elif method.upper() == "PUT":
            response = self.session.put(url, headers=headers, data=json.dumps(data or {}))
        elif method.upper() == "DELETE":
            response = self.session.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json() if response.content else {}


def request_api(method: str, endpoint: str, data: Optional[Dict] = None, 
                base_url: str = "https://api.bloret.com", token: Optional[str] = None) -> Dict[Any, Any]:
    """
    Convenience function for making API requests.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint
        data: Data to send with the request
        base_url: The base URL for the API
        token: Authorization token for API requests
        
    Returns:
        Response data as dictionary
    """
    client = Client(base_url=base_url, token=token)
    return client.request(method, endpoint, data)