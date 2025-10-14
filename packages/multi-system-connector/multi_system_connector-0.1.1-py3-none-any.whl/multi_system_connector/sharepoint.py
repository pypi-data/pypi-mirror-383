# multi_system_connector/sharepoint.py

import requests
from datetime import datetime
from .utils import SYSTEMS, validate_entities_for_intent

def get_sharepoint_access_token():
    config = SYSTEMS["SHAREPOINT"]
    token_url = f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()
    return response.json()["access_token"]


def execute_sharepoint_request(method: str, data: dict = None):
    config = SYSTEMS["SHAREPOINT"]
    try:
        access_token = get_sharepoint_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        site_url = f"{config['base_url']}/sites/{config.get('site_id') or config['site_hostname'] + ':' + config['site_path']}"
        list_name = data.get("list_name", config.get("list_name"))

        if method == "GET":
            url = f"{site_url}/lists/{list_name}/items?expand=fields"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        elif method == "POST":
            url = f"{site_url}/lists/{list_name}/items"
            now = datetime.now().isoformat()
            item_data = {"fields": {"Title": data.get("vendor_name", "Unknown Vendor"), "VendorName": data.get("vendor_name"), "Country": data.get("country"), "CreatedDate": now, "LastModified": now}}
            response = requests.post(url, headers=headers, json=item_data)
            response.raise_for_status()
            return response.json()
        else:
            raise ValueError(f"Unsupported SharePoint method: {method}")

    except Exception as e:
        return {"error": str(e)}
