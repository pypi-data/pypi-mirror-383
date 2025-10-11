# -*- coding: utf-8 -*-
"""
A Python wrapper for the Email Octopus V2 API.
"""
import requests
from typing import Generator, Optional, Dict, Any, List

__version__ = "0.2.0"

class ApiError(Exception):
    """Custom exception for API-related errors."""
    pass

class Client:
    """
    The main client for interacting with the Email Octopus API.
    """
    BASE_URL = "https://api.emailoctopus.com"

    def __init__(self, api_key: str):
        """
        Initializes the API client.

        Args:
            api_key: Your Email Octopus API key.
        """
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None):
        """
        Internal method to handle API requests.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (e.g., /lists).
            params: URL parameters.
            data: JSON body for the request.

        Returns:
            The JSON response from the API, or None for 204 responses.

        Raises:
            ApiError: If the API returns a non-2xx status code.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, params=params, json=data)
            response.raise_for_status()
            
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_message = str(e)
            try:
                error_details = e.response.json()
                if e.response.status_code == 422 and 'errors' in error_details:
                    formatted_errors = []
                    for error in error_details.get('errors', []):
                        pointer = error.get('pointer', 'N/A').lstrip('/')
                        detail = error.get('detail', 'No detail provided.')
                        formatted_errors.append(f"Field '{pointer}': {detail}")
                    main_detail = error_details.get('detail', 'Validation failed.')
                    error_message = f"{main_detail} Details: {'; '.join(formatted_errors)}"
                elif 'error' in error_details and 'message' in error_details['error']:
                    error_message = error_details['error']['message']
            except requests.exceptions.JSONDecodeError:
                if e.response and e.response.text:
                    error_message = e.response.text
            raise ApiError(f"API Error ({e.response.status_code}): {error_message}") from e
        except requests.exceptions.RequestException as e:
            raise ApiError(f"Request failed: {e}") from e

    def _paginated_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Internal generator to handle paginated API requests.
        """
        if params is None:
            params = {}

        while True:
            response_data = self._request("GET", endpoint, params=params)
            if 'data' in response_data and response_data['data']:
                yield from response_data['data']
            
            next_cursor = response_data.get('paging', {}).get('next', {}).get('starting_after')
            if next_cursor:
                params['starting_after'] = next_cursor
            else:
                break

    # --- Lists API ---
    def get_all_lists(self, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Gets all mailing lists, handling pagination automatically.
        This is a generator, so you can iterate over the results.

        Args:
            limit: The number of results to return per page (max 100).

        Yields:
            dict: A dictionary representing a single list.
        """
        yield from self._paginated_request("/lists", params={"limit": limit})

    def create_list(self, name: str) -> Dict[str, Any]:
        """
        Creates a new mailing list.

        Args:
            name: The name of the list.

        Returns:
            A dictionary representing the newly created list.
        """
        return self._request("POST", "/lists", data={"name": name})

    def get_list(self, list_id: str) -> Dict[str, Any]:
        """Gets a specific mailing list by its ID."""
        return self._request("GET", f"/lists/{list_id}")

    def update_list(self, list_id: str, name: str) -> Dict[str, Any]:
        """
        Updates a mailing list's name.

        Args:
            list_id: The ID of the list to update.
            name: The new name for the list.

        Returns:
            A dictionary representing the updated list.
        """
        return self._request("PUT", f"/lists/{list_id}", data={"name": name})

    def delete_list(self, list_id: str) -> None:
        """Deletes a mailing list."""
        self._request("DELETE", f"/lists/{list_id}")

    # --- List Fields API ---
    def create_list_field(self, list_id: str, label: str, tag: str, type: str, fallback: Optional[str] = None, choices: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Creates a new field on a list.

        Args:
            list_id: The ID of the list.
            label: A human-readable label for the field.
            tag: The ID used to reference the field.
            type: The type of the field ('text', 'number', 'date', 'choice_single', 'choice_multiple').
            fallback: A default value for the field.
            choices: A list of choices for 'choice' type fields.

        Returns:
            A dictionary representing the newly created field.
        """
        data = {"label": label, "tag": tag, "type": type}
        if fallback:
            data["fallback"] = fallback
        if choices:
            data["choices"] = choices
        return self._request("POST", f"/lists/{list_id}/fields", data=data)

    def update_list_field(self, list_id: str, tag: str, label: str, fallback: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates a field on a list. Note: only label and fallback can be updated.

        Args:
            list_id: The ID of the list.
            tag: The tag of the field to update.
            label: The new label for the field.
            fallback: The new fallback value for the field.

        Returns:
            A dictionary representing the updated field.
        """
        data = {"label": label}
        if fallback:
            data["fallback"] = fallback
        return self._request("PUT", f"/lists/{list_id}/fields/{tag}", data=data)

    def delete_list_field(self, list_id: str, tag: str) -> None:
        """Deletes a field from a list."""
        self._request("DELETE", f"/lists/{list_id}/fields/{tag}")

    # --- List Tags API ---
    def get_all_list_tags(self, list_id: str, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Gets all tags for a list, handling pagination automatically.

        Args:
            list_id: The ID of the list.
            limit: The number of results to return per page.

        Yields:
            A dictionary representing a single tag.
        """
        yield from self._paginated_request(f"/lists/{list_id}/tags", params={"limit": limit})

    def create_list_tag(self, list_id: str, tag: str) -> Dict[str, Any]:
        """
        Creates a new tag on a list.

        Args:
            list_id: The ID of the list.
            tag: The name of the tag to create.

        Returns:
            A dictionary representing the new tag.
        """
        return self._request("POST", f"/lists/{list_id}/tags", data={"tag": tag})

    def update_list_tag(self, list_id: str, old_tag: str, new_tag: str) -> Dict[str, Any]:
        """
        Updates a tag on a list.

        Args:
            list_id: The ID of the list.
            old_tag: The current name of the tag.
            new_tag: The new name for the tag.

        Returns:
            A dictionary representing the updated tag.
        """
        return self._request("PUT", f"/lists/{list_id}/tags/{old_tag}", data={"tag": new_tag})

    def delete_list_tag(self, list_id: str, tag: str) -> None:
        """Deletes a tag from a list."""
        self._request("DELETE", f"/lists/{list_id}/tags/{tag}")

    # --- Contacts API ---
    def get_all_contacts(self, list_id: str, limit: int = 100, **filters: Any) -> Generator[Dict[str, Any], None, None]:
        """
        Gets all contacts in a given list, handling pagination automatically.

        Args:
            list_id: The ID of the list.
            limit: The number of results to return per page.
            **filters: Optional filters such as 'tag', 'status', 'created_at_lte', etc.

        Yields:
            A dictionary representing a single contact.
        """
        params = {"limit": limit}
        params.update(filters)
        yield from self._paginated_request(f"/lists/{list_id}/contacts", params=params)
    
    def get_subscribed_contacts(self, list_id: str, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Gets all subscribed contacts in a given list, handling pagination automatically.
        This is a generator, so you can iterate over the results.

        Args:
            list_id: The ID of the list.
            limit: The number of results to return per page (max 100).

        Yields:
            dict: A dictionary representing a single subscribed contact.
        """
        yield from self._paginated_request(f"/lists/{list_id}/contacts/subscribed", params={"limit": limit})

    def create_contact(self, list_id: str, email_address: str, fields: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None, status: str = "SUBSCRIBED") -> Dict[str, Any]:
        """Creates a new contact in a list."""
        data = { "email_address": email_address, "status": status }
        if fields: data["fields"] = fields
        if tags: data["tags"] = tags
        return self._request("POST", f"/lists/{list_id}/contacts", data=data)

    def create_or_update_contact(self, list_id: str, email_address: str, fields: Optional[Dict[str, Any]] = None, tags: Optional[Dict[str, bool]] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Upsert endpoint: creates a contact if they don't exist, or updates them if they do.

        Args:
            list_id: The ID of the list.
            email_address: The email address of the contact.
            fields: An object of field key/value pairs. Use null to unset a field.
            tags: An object of tag names to booleans (true to add, false to remove).
            status: The status of the contact ('pending', 'subscribed', 'unsubscribed').

        Returns:
            A dictionary representing the created or updated contact.
        """
        data = {"email_address": email_address}
        if fields is not None: data["fields"] = fields
        if tags is not None: data["tags"] = tags
        if status: data["status"] = status
        return self._request("PUT", f"/lists/{list_id}/contacts", data=data)
    
    def update_contacts_batch(self, list_id: str, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates multiple contacts in a single request.

        Args:
            list_id: The ID of the list.
            contacts: A list of contact objects to update. Each must have an 'id'.

        Returns:
            A dictionary containing lists of successful and failed updates.
        """
        return self._request("PUT", f"/lists/{list_id}/contacts/batch", data={"contacts": contacts})

    def update_contacts_in_batches(self, list_id: str, contacts: Generator[Dict[str, Any], None, None], batch_size: int = 100, fields: Optional[Dict[str, Any]] = None, tags: Optional[Dict[str, bool]] = None, status: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        """
        Applies a uniform update to a generator of contacts in batches.

        This is useful for updating a large number of contacts, for example, from
        the result of `get_all_contacts`, without loading them all into memory.

        Args:
            list_id: The ID of the list.
            contacts: A generator of contact objects to update.
            batch_size: The number of contacts to include in each batch request.
            fields: A dictionary of fields to apply to every contact.
            tags: A dictionary of tags to apply to every contact.
            status: A new status to apply to every contact.

        Yields:
            A dictionary from each batch update call, containing lists of successful and failed updates.
        """
        if not any([fields, tags, status]):
            raise ValueError("At least one of 'fields', 'tags', or 'status' must be provided for the batch update.")

        batch = []
        for contact in contacts:
            update_payload = {'id': contact['id']}
            if fields:
                update_payload['fields'] = fields
            if tags:
                update_payload['tags'] = tags
            if status:
                update_payload['status'] = status
            
            batch.append(update_payload)
            if len(batch) >= batch_size:
                yield self.update_contacts_batch(list_id, batch)
                batch = []
        
        if batch:
            yield self.update_contacts_batch(list_id, batch)

    def get_contact(self, list_id: str, contact_id: str) -> Dict[str, Any]:
        """Gets a specific contact by their ID or hashed email address."""
        return self._request("GET", f"/lists/{list_id}/contacts/{contact_id}")

    def update_contact(self, list_id: str, contact_id: str, email_address: Optional[str] = None, fields: Optional[Dict[str, Any]] = None, status: Optional[str] = None, tags: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Updates a specific contact."""
        data = {}
        if email_address: data['email_address'] = email_address
        if fields: data['fields'] = fields
        if status: data['status'] = status
        if tags: data['tags'] = tags
        if not data:
            raise ValueError("At least one field to update must be provided.")
        return self._request("PUT", f"/lists/{list_id}/contacts/{contact_id}", data=data)

    def delete_contact(self, list_id: str, contact_id: str) -> None:
        """Deletes a contact from a list permanently."""
        self._request("DELETE", f"/lists/{list_id}/contacts/{contact_id}")

    # --- Campaigns API ---
    def get_all_campaigns(self, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Gets all campaigns, handling pagination automatically.

        Args:
            limit: The number of results to return per page (max 100).

        Yields:
            A dictionary representing a single campaign.
        """
        yield from self._paginated_request("/campaigns", params={"limit": limit})

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Gets a specific campaign by its ID."""
        return self._request("GET", f"/campaigns/{campaign_id}")

    # --- Campaign Reports API ---
    def get_campaign_contact_report(self, campaign_id: str, status: str, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Gets a paginated report of contacts for a given campaign and status.

        Args:
            campaign_id: The ID of the campaign.
            status: The report status to retrieve ('bounced', 'clicked', 'complained', etc.).
            limit: The number of results to return per page.

        Yields:
            A dictionary representing a contact in the report.
        """
        params = {"status": status, "limit": limit}
        yield from self._paginated_request(f"/campaigns/{campaign_id}/reports", params=params)

    def get_campaign_links_report(self, campaign_id: str) -> Dict[str, Any]:
        """Gets a report on the performance of links in a campaign."""
        return self._request("GET", f"/campaigns/{campaign_id}/reports/links")

    def get_campaign_summary_report(self, campaign_id: str) -> Dict[str, Any]:
        """Gets a summary report for a campaign."""
        return self._request("GET", f"/campaigns/{campaign_id}/reports/summary")

    # --- Automations API ---
    def start_automation_for_contact(self, automation_id: str, contact_id: str) -> None:
        """
        Starts an automation for a specific contact.

        Args:
            automation_id: The ID of the automation.
            contact_id: The ID of the contact, or an MD5 hash of their email.
        """
        self._request("POST", f"/automations/{automation_id}/queue", data={"contact_id": contact_id})