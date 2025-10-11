"""API client for communicating with SmartTest backend."""

import httpx
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass

from .config import Config
from .models import ScenarioDefinition, AuthConfigReference

class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass

class ApiClient:
    """HTTP client for SmartTest backend API with rate limiting awareness."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_url.rstrip('/')

        # Create HTTP client with configuration
        client_kwargs = config.get_request_kwargs()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Authorization': f'Bearer {config.token}',
                'User-Agent': 'SmartTest-CLI/1.0.0'
            },
            **client_kwargs
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and rate limiting awareness."""
        url = f"{self.base_url}{path}"

        try:
            response = await self.client.request(method, path, **kwargs)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")

            # Handle other HTTP errors
            response.raise_for_status()

            return response.json()

        except httpx.RequestError as e:
            raise Exception(f"Network error communicating with SmartTest API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Please check your SMARTTEST_TOKEN")
            elif e.response.status_code == 403:
                raise Exception("Access forbidden. Please check your permissions")
            else:
                raise Exception(f"API error ({e.response.status_code}): {e.response.text}")

    async def get_scenario_definition(self, scenario_id: int) -> Optional[ScenarioDefinition]:
        """
        Get scenario definition with auth config references (zero credential exposure).

        Returns scenario definition as specified in the MVP spec:
        - Contains ${auth_config_id} placeholders instead of resolved tokens
        - Includes auth_configs with metadata for local resolution
        """
        try:
            data = await self._request('GET', f'/scenario/{scenario_id}/definition')

            # Skip scenarios without validations
            if not data.get('validations'):
                return None

            return ScenarioDefinition.from_api_response(data)

        except Exception as e:
            print(f"⚠️  Failed to fetch scenario {scenario_id}: {e}")
            return None

    async def get_endpoint_scenarios(self, endpoint_id: int, only_with_validations: bool = False) -> List[ScenarioDefinition]:
        """Get all scenarios for an endpoint, optionally filtering to only those with validations."""
        try:
            params = {}
            if only_with_validations:
                params['only_with_validations'] = 'true'

            data = await self._request('GET', f'/endpoints/{endpoint_id}/scenarios', params=params)

            # Fetch full definitions for each scenario
            scenarios = []
            for scenario_info in data.get('scenarios', []):
                scenario_def = await self.get_scenario_definition(scenario_info['id'])
                if scenario_def:
                    scenarios.append(scenario_def)

            return scenarios

        except Exception as e:
            print(f"⚠️  Failed to fetch scenarios for endpoint {endpoint_id}: {e}")
            return []

    async def get_system_scenarios(self, system_id: int, only_with_validations: bool = False) -> List[ScenarioDefinition]:
        """Get all scenarios for a system, optionally filtering to only those with validations."""
        try:
            params = {}
            if only_with_validations:
                params['only_with_validations'] = 'true'

            data = await self._request('GET', f'/system/{system_id}/scenarios', params=params)

            # Fetch full definitions for each scenario
            scenarios = []
            for scenario_info in data.get('scenarios', []):
                scenario_def = await self.get_scenario_definition(scenario_info['id'])
                if scenario_def:
                    scenarios.append(scenario_def)

            return scenarios

        except Exception as e:
            print(f"⚠️  Failed to fetch scenarios for system {system_id}: {e}")
            return []

    async def submit_scenario_results(
        self,
        scenario_id: int,
        execution_data: Dict[str, Any],
        record_run: bool = True,
        increment_usage: bool = True
    ) -> Dict[str, Any]:
        """
        Submit scenario execution results for validation and persistence.

        Supports both successful executions and error cases as per MVP spec.
        """
        try:
            params = {}
            if record_run:
                params['record_run'] = 'true'
            if increment_usage:
                params['increment_usage'] = 'true'

            return await self._request(
                'POST',
                f'/scenario/{scenario_id}/check-validations',
                params=params,
                json=execution_data
            )

        except RateLimitError:
            # For rate limiting, implement retry logic
            await asyncio.sleep(10)  # Simple backoff
            return await self.submit_scenario_results(
                scenario_id, execution_data, record_run, increment_usage
            )
        except Exception as e:
            print(f"⚠️  Failed to submit results for scenario {scenario_id}: {e}")
            # Return a fallback result for graceful degradation
            return {
                'scenario_id': scenario_id,
                'execution_status': 'submission_error',
                'validations': [],
                'summary': {'passed': 0, 'failed': 0, 'submission_error': True},
                'error': str(e)
            }