"""MCP (Model Context Protocol) service for tool integration."""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
import os
import glob as glob_module
import httpx

logger = logging.getLogger(__name__)


class MCPService:
    """Service for managing MCP servers and tools."""

    def __init__(self, config_path: str = "config/mcp_servers.yaml"):
        # Convert to Path and make it relative to project root (parent of backend directory)
        self.config_path = Path(__file__).parent.parent.parent / config_path
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.active_servers: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load MCP server configuration from YAML."""
        try:
            if not self.config_path.exists():
                logger.warning(f"MCP config file not found: {self.config_path}")
                self.servers = {}
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.servers = config.get('servers', {})
                logger.info(f"Loaded {len(self.servers)} MCP server configurations")

                # Auto-start enabled servers
                for server_name, server_config in self.servers.items():
                    if server_config.get('enabled', False):
                        # Set environment variables from config
                        env_vars = server_config.get('env', {})
                        for key, value in env_vars.items():
                            os.environ[key] = value
                            logger.info(f"Set environment variable {key} for server {server_name}")

                        # Mark as active (for filesystem, we don't need actual process)
                        self.active_servers[server_name] = {
                            'config': server_config,
                            'status': 'running'
                        }
                        logger.info(f"Auto-started enabled MCP server: {server_name}")
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self.servers = {}

    def save_config(self):
        """Save MCP server configuration to YAML."""
        try:
            config = {'servers': self.servers}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            logger.info("Saved MCP configuration")
        except Exception as e:
            logger.error(f"Failed to save MCP config: {e}")

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all configured MCP servers."""
        return [
            {
                'name': name,
                'enabled': config.get('enabled', False),
                'description': config.get('description', ''),
                'command': config.get('command', ''),
            }
            for name, config in self.servers.items()
        ]

    async def enable_server(self, server_name: str) -> bool:
        """Enable an MCP server."""
        if server_name not in self.servers:
            logger.error(f"Server not found: {server_name}")
            return False

        try:
            self.servers[server_name]['enabled'] = True
            self.save_config()

            # Auto-start the server
            await self.start_server(server_name)

            logger.info(f"Enabled MCP server: {server_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable server {server_name}: {e}")
            return False

    async def disable_server(self, server_name: str) -> bool:
        """Disable an MCP server."""
        if server_name not in self.servers:
            logger.error(f"Server not found: {server_name}")
            return False

        try:
            self.servers[server_name]['enabled'] = False
            self.save_config()

            # Stop server if running
            if server_name in self.active_servers:
                await self.stop_server(server_name)

            logger.info(f"Disabled MCP server: {server_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable server {server_name}: {e}")
            return False

    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server process."""
        if server_name not in self.servers:
            logger.error(f"Server not found: {server_name}")
            return False

        if not self.servers[server_name].get('enabled', False):
            logger.warning(f"Server not enabled: {server_name}")
            return False

        try:
            config = self.servers[server_name]
            command = config.get('command')
            args = config.get('args', [])
            env_vars = config.get('env', {})

            # Set environment variables from config
            for key, value in env_vars.items():
                os.environ[key] = value
                logger.info(f"Set environment variable {key} for server {server_name}")

            # Note: Actual MCP server process management would go here
            # For now, we'll mark it as active in memory
            self.active_servers[server_name] = {
                'config': config,
                'status': 'running'
            }

            logger.info(f"Started MCP server: {server_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start server {server_name}: {e}")
            return False

    async def stop_server(self, server_name: str) -> bool:
        """Stop an MCP server process."""
        if server_name not in self.active_servers:
            logger.warning(f"Server not running: {server_name}")
            return True

        try:
            # Note: Actual process termination would go here
            del self.active_servers[server_name]
            logger.info(f"Stopped MCP server: {server_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop server {server_name}: {e}")
            return False

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from enabled and started MCP servers."""
        tools = []

        # Get tools from active servers
        for server_name, server_data in self.active_servers.items():
            config = self.servers.get(server_name, {})

            # Check if server is also enabled
            if not config.get('enabled', False):
                continue

            # Add tools based on server type
            if server_name == 'filesystem':
                tools.extend([
                    {
                        'name': 'list_directory',
                        'server': server_name,
                        'description': 'List files and directories in a specified path',
                        'parameters': {
                            'path': {'type': 'string', 'description': 'Directory path to list'}
                        }
                    },
                    {
                        'name': 'search_files',
                        'server': server_name,
                        'description': 'Search for files matching a pattern in a directory',
                        'parameters': {
                            'directory': {'type': 'string', 'description': 'Directory to search in'},
                            'pattern': {'type': 'string', 'description': 'File pattern (e.g., *.mp4, *.txt)'}
                        }
                    },
                    {
                        'name': 'read_file',
                        'server': server_name,
                        'description': 'Read contents of a file',
                        'parameters': {
                            'path': {'type': 'string', 'description': 'File path to read'}
                        }
                    }
                ])
            elif server_name == 'github':
                tools.extend([
                    {
                        'name': 'search_repositories',
                        'server': server_name,
                        'description': 'Search GitHub repositories',
                        'parameters': {
                            'query': {'type': 'string', 'description': 'Search query'}
                        }
                    }
                ])
            elif server_name == 'tavily':
                tools.extend([
                    {
                        'name': 'tavily_search',
                        'server': server_name,
                        'description': 'Search the web using Tavily API for current information',
                        'parameters': {
                            'query': {'type': 'string', 'description': 'Search query'},
                            'max_results': {'type': 'number', 'description': 'Maximum results (default: 5)', 'optional': True}
                        }
                    }
                ])
            elif server_name == 'weather':
                tools.extend([
                    {
                        'name': 'get_current_weather',
                        'server': server_name,
                        'description': 'Get current weather for a city',
                        'parameters': {
                            'city': {'type': 'string', 'description': 'City name (optional, default: Sydney)', 'optional': True},
                            'country': {'type': 'string', 'description': 'Country code (optional)', 'optional': True}
                        }
                    },
                    {
                        'name': 'get_weather_forecast',
                        'server': server_name,
                        'description': 'Get weather forecast for up to 7 days',
                        'parameters': {
                            'city': {'type': 'string', 'description': 'City name (optional, default: Sydney)', 'optional': True},
                            'country': {'type': 'string', 'description': 'Country code (optional)', 'optional': True},
                            'days': {'type': 'number', 'description': 'Number of days (1-7, default: 3)', 'optional': True}
                        }
                    },
                    {
                        'name': 'search_cities',
                        'server': server_name,
                        'description': 'Search for cities by name',
                        'parameters': {
                            'query': {'type': 'string', 'description': 'City name to search'}
                        }
                    }
                ])

        return tools

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        try:
            logger.info(f"Calling tool: {tool_name} with params: {parameters}")

            # Implement actual tool calls based on tool name
            if tool_name == 'list_directory':
                return await self._list_directory(parameters.get('path', '.'))
            elif tool_name == 'search_files':
                return await self._search_files(
                    parameters.get('directory', '.'),
                    parameters.get('pattern', '*')
                )
            elif tool_name == 'read_file':
                return await self._read_file(parameters.get('path'))
            elif tool_name == 'tavily_search':
                return await self._tavily_search(
                    parameters.get('query'),
                    parameters.get('max_results', 5)
                )
            elif tool_name == 'get_current_weather':
                return await self._get_current_weather(
                    parameters.get('city', 'Sydney'),
                    parameters.get('country')
                )
            elif tool_name == 'get_weather_forecast':
                return await self._get_weather_forecast(
                    parameters.get('city', 'Sydney'),
                    parameters.get('country'),
                    parameters.get('days', 3)
                )
            elif tool_name == 'search_cities':
                return await self._search_cities(parameters.get('query'))
            else:
                return {
                    'success': False,
                    'error': f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List contents of a directory."""
        try:
            dir_path = Path(path).expanduser().resolve()

            if not dir_path.exists():
                return {
                    'success': False,
                    'error': f"Directory not found: {path}"
                }

            if not dir_path.is_dir():
                return {
                    'success': False,
                    'error': f"Path is not a directory: {path}"
                }

            items = []
            for item in dir_path.iterdir():
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else None
                })

            return {
                'success': True,
                'result': f"Found {len(items)} items in {path}",
                'items': items
            }
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        try:
            dir_path = Path(directory).expanduser().resolve()

            if not dir_path.exists():
                return {
                    'success': False,
                    'error': f"Directory not found: {directory}"
                }

            # Use glob to search for files
            search_path = dir_path / '**' / pattern
            matching_files = []

            for file_path in glob_module.glob(str(search_path), recursive=True):
                file_obj = Path(file_path)
                if file_obj.is_file():
                    matching_files.append({
                        'name': file_obj.name,
                        'path': str(file_obj),
                        'size': file_obj.stat().st_size,
                        'parent': str(file_obj.parent)
                    })

            return {
                'success': True,
                'result': f"Found {len(matching_files)} files matching '{pattern}' in {directory}",
                'files': matching_files
            }
        except Exception as e:
            logger.error(f"Error searching files in {directory}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read contents of a file."""
        try:
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return {
                    'success': False,
                    'error': f"File not found: {path}"
                }

            if not file_path.is_file():
                return {
                    'success': False,
                    'error': f"Path is not a file: {path}"
                }

            # Read file contents
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'success': True,
                'result': f"Read {len(content)} characters from {path}",
                'content': content,
                'path': str(file_path)
            }
        except UnicodeDecodeError:
            return {
                'success': False,
                'error': f"File is not a text file: {path}"
            }
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _tavily_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web using Tavily API."""
        try:
            api_key = os.environ.get('TAVILY_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': 'TAVILY_API_KEY environment variable not set'
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.tavily.com/search',
                    json={
                        'api_key': api_key,
                        'query': query,
                        'max_results': max_results,
                        'include_answer': True
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Tavily API error: {response.status_code}"
                    }

                data = response.json()
                results = data.get('results', [])
                answer = data.get('answer', '')

                return {
                    'success': True,
                    'result': f"Found {len(results)} results for '{query}'",
                    'answer': answer,
                    'results': results
                }
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _get_current_weather(self, city: str = 'Sydney', country: Optional[str] = None) -> Dict[str, Any]:
        """Get current weather using Open-Meteo API."""
        try:
            # First, geocode the city
            geocode_result = await self._geocode_city(city, country)
            if not geocode_result['success']:
                return geocode_result

            lat = geocode_result['latitude']
            lon = geocode_result['longitude']
            location_name = geocode_result['name']

            # Get weather data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.open-meteo.com/v1/forecast',
                    params={
                        'latitude': lat,
                        'longitude': lon,
                        'current_weather': True,
                        'timezone': 'auto'
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Weather API error: {response.status_code}"
                    }

                data = response.json()
                current = data.get('current_weather', {})

                return {
                    'success': True,
                    'result': f"Current weather for {location_name}",
                    'weather': {
                        'location': location_name,
                        'temperature': current.get('temperature'),
                        'windspeed': current.get('windspeed'),
                        'winddirection': current.get('winddirection'),
                        'weathercode': current.get('weathercode'),
                        'time': current.get('time')
                    }
                }
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _get_weather_forecast(self, city: str = 'Sydney', country: Optional[str] = None, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast using Open-Meteo API."""
        try:
            # Limit days to 1-7
            days = max(1, min(7, days))

            # First, geocode the city
            geocode_result = await self._geocode_city(city, country)
            if not geocode_result['success']:
                return geocode_result

            lat = geocode_result['latitude']
            lon = geocode_result['longitude']
            location_name = geocode_result['name']

            # Get weather data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.open-meteo.com/v1/forecast',
                    params={
                        'latitude': lat,
                        'longitude': lon,
                        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
                        'forecast_days': days,
                        'timezone': 'auto'
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Weather API error: {response.status_code}"
                    }

                data = response.json()
                daily = data.get('daily', {})

                forecast_data = []
                for i in range(len(daily.get('time', []))):
                    forecast_data.append({
                        'date': daily['time'][i],
                        'max_temp': daily['temperature_2m_max'][i],
                        'min_temp': daily['temperature_2m_min'][i],
                        'precipitation': daily['precipitation_sum'][i],
                        'weathercode': daily['weathercode'][i]
                    })

                return {
                    'success': True,
                    'result': f"{days}-day forecast for {location_name}",
                    'forecast': {
                        'location': location_name,
                        'days': forecast_data
                    }
                }
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _search_cities(self, query: str) -> Dict[str, Any]:
        """Search for cities using Open-Meteo geocoding API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://geocoding-api.open-meteo.com/v1/search',
                    params={
                        'name': query,
                        'count': 10,
                        'language': 'en',
                        'format': 'json'
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Geocoding API error: {response.status_code}"
                    }

                data = response.json()
                results = data.get('results', [])

                cities = []
                for result in results:
                    cities.append({
                        'name': result.get('name'),
                        'country': result.get('country'),
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude'),
                        'admin1': result.get('admin1', ''),
                        'population': result.get('population', 0)
                    })

                return {
                    'success': True,
                    'result': f"Found {len(cities)} cities matching '{query}'",
                    'cities': cities
                }
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _geocode_city(self, city: str, country: Optional[str] = None) -> Dict[str, Any]:
        """Geocode a city name to coordinates."""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'name': city,
                    'count': 1,
                    'language': 'en',
                    'format': 'json'
                }

                response = await client.get(
                    'https://geocoding-api.open-meteo.com/v1/search',
                    params=params,
                    timeout=10.0
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Geocoding API error: {response.status_code}"
                    }

                data = response.json()
                results = data.get('results', [])

                if not results:
                    return {
                        'success': False,
                        'error': f"City not found: {city}"
                    }

                result = results[0]
                return {
                    'success': True,
                    'latitude': result.get('latitude'),
                    'longitude': result.get('longitude'),
                    'name': result.get('name'),
                    'country': result.get('country')
                }
        except Exception as e:
            logger.error(f"Error geocoding city: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def close(self):
        """Cleanup MCP service resources."""
        for server_name in list(self.active_servers.keys()):
            await self.stop_server(server_name)
        logger.info("MCP service closed")
