"""
NIA API Client for communicating with production NIA API
"""
import os
import httpx
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
import json
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API errors with status code."""
    def __init__(self, message: str, status_code: int = None, detail: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

class NIAApiClient:
    """Client for interacting with NIA's production API."""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        # Remove trailing slash from base URL to prevent double slashes
        self.base_url = (base_url or os.getenv("NIA_API_URL", "https://apigcp.trynia.ai")).rstrip('/')
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "nia-mcp-server/1.0.27",
                "Content-Type": "application/json"
            },
            timeout=720.0  # 12 minute timeout for deep research operations
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _handle_api_error(self, e: httpx.HTTPStatusError) -> APIError:
        """Convert HTTP errors to more specific API errors."""
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", error_detail)
        except (json.JSONDecodeError, ValueError):
            # Failed to parse JSON response, keep original error_detail
            pass
        
        status_code = e.response.status_code
        
        # Log the full error for debugging
        logger.error(f"API error - Status: {status_code}, Response: {error_detail}")
        
        # Handle specific error cases
        if status_code == 401:
            return APIError(
                "Invalid or missing API key. Please check your API key at https://trynia.ai/api-keys",
                status_code,
                error_detail,
            )
        elif status_code == 403:
            # Check for various forms of usage limit errors
            error_lower = error_detail.lower()
            if any(
                phrase in error_lower
                for phrase in [
                    "lifetime limit",
                    "no chat credits",
                    "free api requests",
                    "3 free",
                    "usage limit",
                ]
            ):
                # Use the exact error message from the API for clarity
                return APIError(error_detail, status_code, error_detail)
            else:
                return APIError(
                    f"Access forbidden: {error_detail}", status_code, error_detail
                )
        elif status_code == 429:
            return APIError(f"Rate limit exceeded: {error_detail}", status_code, error_detail)
        elif status_code == 404:
            return APIError(f"Resource not found: {error_detail}", status_code, error_detail)
        elif status_code == 500:
            # For 500 errors, try to extract more meaningful error details
            if error_detail:
                error_lower = error_detail.lower()
                # Check if it's actually a wrapped error from middleware or API
                if any(
                    phrase in error_lower
                    for phrase in [
                        "lifetime limit",
                        "free api requests",
                        "3 free",
                        "usage limit",
                    ]
                ):
                    return APIError(error_detail, 403, error_detail)
                else:
                    return APIError(f"Server error: {error_detail}", status_code, error_detail)
            else:
                return APIError(
                    "Internal server error. Please try again later.",
                    status_code,
                    error_detail,
                )
        else:
            return APIError(
                f"API error (status {status_code}): {error_detail}",
                status_code,
                error_detail,
            )
    async def validate_api_key(self) -> bool:
        """Validate the API key by making a test request."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/repositories")
            return response.status_code == 200
        except httpx.HTTPStatusError as e:
            # Log the specific error but return False for validation
            error = self._handle_api_error(e)
            logger.error(f"API key validation failed: {error}")
            return False
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """List all indexed repositories."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/repositories")
            response.raise_for_status()
            data = response.json()
            
            # Ensure we always return a list
            if not isinstance(data, list):
                logger.error(f"Unexpected response type from list_repositories: {type(data)}, data: {data}")
                # If it's a dict with an error message, raise it
                if isinstance(data, dict) and "error" in data:
                    raise APIError(f"API returned error: {data['error']}")
                # Otherwise return empty list
                return []
            
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Caught HTTPStatusError in list_repositories: status={e.response.status_code}, detail={e.response.text}")
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            raise APIError(f"Failed to list repositories: {str(e)}")
    
    async def index_repository(self, repo_url: str, branch: str = None) -> Dict[str, Any]:
        """Index a GitHub repository."""
        try:
            # Handle different input formats
            if "github.com" in repo_url:
                # Remove query parameters and fragments
                clean_url = repo_url.split('?')[0].split('#')[0]
                
                # Check if it's a folder URL (contains /tree/)
                if "/tree/" in clean_url:
                    # Extract everything after github.com/
                    parts = clean_url.split('github.com/', 1)
                    if len(parts) > 1:
                        repository_path = parts[1].rstrip('/')
                    else:
                        repository_path = repo_url
                else:
                    # Regular repo URL - extract owner/repo
                    parts = clean_url.rstrip('/').split('/')
                    if len(parts) >= 2:
                        repo_name = parts[-1]
                        # Remove .git suffix if present
                        if repo_name.endswith('.git'):
                            repo_name = repo_name[:-4]
                        repository_path = f"{parts[-2]}/{repo_name}"
                    else:
                        repository_path = repo_url
            else:
                # Assume it's already in the right format
                repository_path = repo_url
            
            payload = {
                "repository": repository_path,
                "branch": branch
            }
            
            response = await self.client.post(
                f"{self.base_url}/v2/repositories",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to index repository: {str(e)}")
    
    async def get_repository_status(self, owner_repo: str) -> Dict[str, Any]:
        """Get the status of a repository."""
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, list all repositories to find the matching one
                repos = await self.list_repositories()
                
                # Extract base repository path for matching
                # Handle both "owner/repo" and "owner/repo/folder" formats
                base_repo = owner_repo
                if owner_repo.count('/') > 1:
                    # This might be a folder path like "owner/repo/folder"
                    # Extract just the owner/repo part
                    parts = owner_repo.split('/')
                    base_repo = f"{parts[0]}/{parts[1]}"
                
                # Look for a repository matching this owner/repo
                matching_repo = None
                for repo in repos:
                    repo_path = repo.get("repository", "")
                    # Check exact match first
                    if repo_path == owner_repo:
                        matching_repo = repo
                        break
                    # Then check if it's the base repository
                    elif repo_path == base_repo:
                        matching_repo = repo
                        break
                    # Also check if the stored repo is a folder path that starts with our base
                    elif repo_path.startswith(base_repo + "/"):
                        matching_repo = repo
                        break
                
                if not matching_repo:
                    logger.warning(f"Repository {owner_repo} not found in list")
                    return None
                
                # Use the repository_id from the matched repo
                repo_id = matching_repo.get("repository_id") or matching_repo.get("id")
                if not repo_id:
                    logger.error(f"No repository ID found for {owner_repo}")
                    return None
                    
                # Now get the status using the ID
                response = await self.client.get(f"{self.base_url}/v2/repositories/{repo_id}")
                response.raise_for_status()
                
                # Merge the response with what we know
                status = response.json()
                # Ensure repository field is included for consistency
                if "repository" not in status:
                    status["repository"] = owner_repo
                return status
            else:
                # Assume it's already a repository ID
                response = await self.client.get(f"{self.base_url}/v2/repositories/{owner_repo}")
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get repository status: {e}")
            return None
    
    async def query_repositories(
        self,
        messages: List[Dict[str, str]],
        repositories: List[str],
        stream: bool = True,
        include_sources: bool = True
    ) -> AsyncIterator[str]:
        """Query indexed repositories with streaming support."""
        try:
            # Format repositories for the API
            repo_list = []
            for repo in repositories:
                if "/" in repo:
                    repo_list.append({"repository": repo})
                else:
                    # Assume it's a project ID or other identifier
                    repo_list.append({"repository": repo})
            
            payload = {
                "messages": messages,
                "repositories": repo_list,
                "stream": stream,
                "include_sources": include_sources
            }
            
            if stream:
                async with self.client.stream(
                    "POST",
                    f"{self.base_url}/v2/query",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data == "[DONE]":
                                    break
                                yield data
            else:
                response = await self.client.post(
                    f"{self.base_url}/v2/query",
                    json=payload
                )
                response.raise_for_status()
                yield json.dumps(response.json())
                
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Query failed: {str(e)}")
    
    async def wait_for_indexing(self, owner_repo: str, timeout: int = 600) -> Dict[str, Any]:
        """Wait for a repository to finish indexing."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_repository_status(owner_repo)
            
            if not status:
                raise Exception(f"Repository {owner_repo} not found")
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Indexing failed: {status.get('error', 'Unknown error')}")
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception(f"Indexing timeout after {timeout} seconds")
            
            # Wait before next check
            await asyncio.sleep(2)
    
    async def delete_repository(self, owner_repo: str) -> bool:
        """Delete an indexed repository."""
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, get the repository ID
                status = await self.get_repository_status(owner_repo)
                if not status:
                    logger.warning(f"Repository {owner_repo} not found")
                    return False
                
                # Extract the repository ID from status
                repo_id = status.get("repository_id") or status.get("id")
                if not repo_id:
                    # Try to get it from list as fallback
                    repos = await self.list_repositories()
                    for repo in repos:
                        if repo.get("repository") == owner_repo:
                            repo_id = repo.get("repository_id") or repo.get("id")
                            break
                
                if not repo_id:
                    logger.error(f"No repository ID found for {owner_repo}")
                    return False
                    
                # Delete using the ID
                response = await self.client.delete(f"{self.base_url}/v2/repositories/{repo_id}")
                response.raise_for_status()
                return True
            else:
                # Assume it's already a repository ID
                response = await self.client.delete(f"{self.base_url}/v2/repositories/{owner_repo}")
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete repository: {e}")
            return False
    
    async def rename_repository(self, owner_repo: str, new_name: str) -> Dict[str, Any]:
        """Rename a repository's display name."""
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, get the repository ID
                status = await self.get_repository_status(owner_repo)
                if not status:
                    raise APIError(f"Repository {owner_repo} not found", 404)
                
                # Extract the repository ID from status
                repo_id = status.get("repository_id") or status.get("id")
                if not repo_id:
                    # Try to get it from list as fallback
                    repos = await self.list_repositories()
                    for repo in repos:
                        if repo.get("repository") == owner_repo:
                            repo_id = repo.get("repository_id") or repo.get("id")
                            break
                
                if not repo_id:
                    raise APIError(f"No repository ID found for {owner_repo}", 404)
                    
                # Rename using the ID
                response = await self.client.patch(
                    f"{self.base_url}/v2/repositories/{repo_id}/rename",
                    json={"new_name": new_name}
                )
                response.raise_for_status()
                return response.json()
            else:
                # Assume it's already a repository ID
                response = await self.client.patch(
                    f"{self.base_url}/v2/repositories/{owner_repo}/rename",
                    json={"new_name": new_name}
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Failed to rename repository: {e}")
            raise APIError(f"Failed to rename repository: {str(e)}")
            
    async def get_github_tree(
        self,
        owner_repo: str,
        branch: Optional[str] = None,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        file_extensions: Optional[List[str]] = None,
        exclude_extensions: Optional[List[str]] = None,
        show_full_paths: bool = False
    ) -> Dict[str, Any]:
        """Get file tree directly from GitHub API (no FalkorDB dependency).

        Args:
            owner_repo: Repository in owner/repo format or repository ID
            branch: Optional branch name (defaults to repository's default branch)
            include_paths: Only include files in these paths (e.g., ["src/", "lib/"])
            exclude_paths: Exclude files in these paths (e.g., ["node_modules/", "dist/"])
            file_extensions: Only include these file extensions (e.g., [".py", ".js"])
            exclude_extensions: Exclude these file extensions (e.g., [".md", ".lock"])
            show_full_paths: Show full file paths instead of hierarchical tree

        Returns:
            GitHub tree structure with files, directories, and stats
        """
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, get the repository ID
                status = await self.get_repository_status(owner_repo)
                if not status:
                    raise APIError(f"Repository {owner_repo} not found", 404)

                # Extract the repository ID from status
                repo_id = status.get("repository_id") or status.get("id")
                if not repo_id:
                    # Try to get it from list as fallback
                    repos = await self.list_repositories()
                    for repo in repos:
                        if repo.get("repository") == owner_repo:
                            repo_id = repo.get("repository_id") or repo.get("id")
                            break

                if not repo_id:
                    raise APIError(f"No repository ID found for {owner_repo}", 404)

                # Get tree using the ID
                params = {}
                if branch:
                    params["branch"] = branch
                if include_paths:
                    params["include_paths"] = ",".join(include_paths)
                if exclude_paths:
                    params["exclude_paths"] = ",".join(exclude_paths)
                if file_extensions:
                    params["file_extensions"] = ",".join(file_extensions)
                if exclude_extensions:
                    params["exclude_extensions"] = ",".join(exclude_extensions)
                if show_full_paths:
                    params["show_full_paths"] = "true"

                response = await self.client.get(
                    f"{self.base_url}/v2/repositories/{repo_id}/github-tree",
                    params=params
                )
                response.raise_for_status()
                return response.json()
            else:
                # Assume it's already a repository ID
                params = {}
                if branch:
                    params["branch"] = branch
                if include_paths:
                    params["include_paths"] = ",".join(include_paths)
                if exclude_paths:
                    params["exclude_paths"] = ",".join(exclude_paths)
                if file_extensions:
                    params["file_extensions"] = ",".join(file_extensions)
                if exclude_extensions:
                    params["exclude_extensions"] = ",".join(exclude_extensions)
                if show_full_paths:
                    params["show_full_paths"] = "true"

                response = await self.client.get(
                    f"{self.base_url}/v2/repositories/{owner_repo}/github-tree",
                    params=params
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Failed to get GitHub tree: {e}")
            raise APIError(f"Failed to get GitHub tree: {str(e)}")

    # Data Source methods
    
    async def create_data_source(
        self, 
        url: str, 
        url_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        max_age: int = None,
        only_main_content: bool = True,
        wait_for: int = None,
        include_screenshot: bool = None,
        check_llms_txt: bool = None,
        llms_txt_strategy: str = None
    ) -> Dict[str, Any]:
        """Create a new documentation/web data source."""
        try:
            payload = {
                "url": url,
                "url_patterns": url_patterns or [],
                "exclude_patterns": exclude_patterns or []
            }
            
            # Add optional parameters
            if max_age is not None:
                payload["max_age"] = max_age
            # Don't hardcode formats - let backend defaults apply
            # This allows screenshots to be captured by default
            if only_main_content is not None:
                payload["only_main_content"] = only_main_content
            if wait_for is not None:
                payload["wait_for"] = wait_for
            if include_screenshot is not None:
                payload["include_screenshot"] = include_screenshot
            if check_llms_txt is not None:
                payload["check_llms_txt"] = check_llms_txt
            if llms_txt_strategy is not None:
                payload["llms_txt_strategy"] = llms_txt_strategy
            
            response = await self.client.post(
                f"{self.base_url}/v2/data-sources",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to create data source: {str(e)}")
    
    async def list_data_sources(self) -> List[Dict[str, Any]]:
        """List all data sources for the authenticated user."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/data-sources")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to list data sources: {e}")
            raise APIError(f"Failed to list data sources: {str(e)}")
    
    async def get_data_source_status(self, source_id: str) -> Dict[str, Any]:
        """Get the status of a data source."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/data-sources/{source_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get data source status: {e}")
            return None
    
    async def delete_data_source(self, source_id: str) -> bool:
        """Delete a data source."""
        try:
            response = await self.client.delete(f"{self.base_url}/v2/data-sources/{source_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete data source: {e}")
            return False
    
    async def rename_data_source(self, source_id: str, new_name: str) -> Dict[str, Any]:
        """Rename a data source's display name."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/v2/data-sources/{source_id}/rename",
                json={"new_name": new_name}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to rename data source: {e}")
            raise APIError(f"Failed to rename data source: {str(e)}")
    
    async def query_unified(
        self,
        messages: List[Dict[str, str]],
        repositories: List[str] = None,
        data_sources: List[str] = None,
        search_mode: str = "unified",
        stream: bool = True,
        include_sources: bool = True
    ) -> AsyncIterator[str]:
        """Query across repositories and/or documentation sources."""
        try:
            # Build repository list
            repo_list = []
            if repositories:
                for repo in repositories:
                    repo_list.append({"repository": repo})
            
            # Build data source list
            source_list = []
            if data_sources:
                for source in data_sources:
                    # Handle flexible identifier formats:
                    # 1. String directly (display_name, URL, or source_id) - NEW
                    # 2. Dict with "source_id" (backwards compatible)
                    # 3. Dict with "identifier" (new format)
                    if isinstance(source, str):
                        # Pass string directly - backend will resolve it
                        source_list.append(source)
                    elif isinstance(source, dict):
                        # Keep dict format as-is (backwards compatible)
                        source_list.append(source)
                    else:
                        # Convert other types to string
                        source_list.append(str(source))
            
            # Validate at least one source
            if not repo_list and not source_list:
                raise Exception("No repositories or data sources specified")
            
            payload = {
                "messages": messages,
                "repositories": repo_list,
                "data_sources": source_list,
                "search_mode": search_mode,
                "stream": stream,
                "include_sources": include_sources
            }
            
            if stream:
                async with self.client.stream(
                    "POST",
                    f"{self.base_url}/v2/query",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data == "[DONE]":
                                    break
                                yield data
            else:
                response = await self.client.post(
                    f"{self.base_url}/v2/query",
                    json=payload
                )
                response.raise_for_status()
                yield json.dumps(response.json())
                
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Query failed: {str(e)}")
    
    async def web_search(
        self,
        query: str,
        num_results: int = 5,
        category: Optional[str] = None,
        days_back: Optional[int] = None,
        find_similar_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform AI-powered web search."""
        try:
            payload = {
                "query": query,
                "num_results": min(num_results, 10),
            }
            
            # Add optional parameters
            if category:
                payload["category"] = category
            if days_back:
                payload["days_back"] = days_back
            if find_similar_to:
                payload["find_similar_to"] = find_similar_to
            
            response = await self.client.post(
                f"{self.base_url}/v2/web-search",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Web search failed: {str(e)}")
    
    async def deep_research(
        self,
        query: str,
        output_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform deep research using AI agent."""
        try:
            payload = {
                "query": query,
            }

            if output_format:
                payload["output_format"] = output_format

            response = await self.client.post(
                f"{self.base_url}/v2/deep-research",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Deep research failed: {str(e)}")

    async def regex_search(
        self,
        repositories: List[str],
        query: str,
        pattern: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        max_results: int = 50,
        include_context: bool = True,
        context_lines: int = 3
    ) -> Dict[str, Any]:
        """
        Perform regex pattern search over indexed repository source code.

        Args:
            repositories: List of repositories to search (owner/repo format)
            query: Natural language query or regex pattern
            pattern: Optional explicit regex pattern (overrides query extraction)
            file_extensions: File extensions to filter (e.g., [".js", ".tsx"])
            languages: Programming languages to filter
            max_results: Maximum number of results to return
            include_context: Include surrounding context lines
            context_lines: Number of context lines before/after match

        Returns:
            Search results with matched patterns and locations
        """
        try:
            # Build repository list
            repo_list = []
            for repo in repositories:
                if isinstance(repo, dict):
                    repo_list.append(repo)
                else:
                    repo_list.append({"repository": repo})

            payload = {
                "repositories": repo_list,
                "query": query,
                "max_results": max_results,
                "include_context": include_context,
                "context_lines": context_lines
            }

            # Add optional parameters
            if pattern:
                payload["pattern"] = pattern
            if file_extensions:
                payload["file_extensions"] = file_extensions
            if languages:
                payload["languages"] = languages

            response = await self.client.post(
                f"{self.base_url}/v2/regex-search",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Regex search failed: {str(e)}")

    async def get_source_content(
        self,
        source_type: str,
        source_identifier: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get full content of a specific source file or document."""
        try:
            payload = {
                "source_type": source_type,
                "source_identifier": source_identifier,
                "metadata": metadata or {}
            }

            response = await self.client.post(
                f"{self.base_url}/v2/sources/content",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to get source content: {str(e)}")

    async def submit_bug_report(
        self,
        description: str,
        bug_type: str = "bug",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a bug report or feature request."""
        try:
            payload = {
                "description": description,
                "bug_type": bug_type,
                "additional_context": additional_context
            }

            response = await self.client.post(
                f"{self.base_url}/v2/bug-report",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to submit bug report: {str(e)}")
    
    async def index_local_filesystem(
        self,
        directory_path: str,
        inclusion_patterns: List[str] = None,
        exclusion_patterns: List[str] = None,
        max_file_size_mb: int = 50
    ) -> Dict[str, Any]:
        """Index a local filesystem directory."""
        try:
            payload = {
                "directory_path": directory_path,
                "inclusion_patterns": inclusion_patterns or [],
                "exclusion_patterns": exclusion_patterns or [],
                "max_file_size_mb": max_file_size_mb
            }
            
            response = await self.client.post(
                f"{self.base_url}/v2/local-filesystem",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to index local filesystem: {str(e)}")
    
    async def scan_local_filesystem(
        self,
        directory_path: str,
        inclusion_patterns: List[str] = None,
        exclusion_patterns: List[str] = None,
        max_file_size_mb: int = 50
    ) -> Dict[str, Any]:
        """Scan a local filesystem directory to preview what would be indexed."""
        try:
            payload = {
                "directory_path": directory_path,
                "inclusion_patterns": inclusion_patterns or [],
                "exclusion_patterns": exclusion_patterns or [],
                "max_file_size_mb": max_file_size_mb
            }
            
            response = await self.client.post(
                f"{self.base_url}/v2/local-filesystem/scan",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to scan local filesystem: {str(e)}")
    
    async def check_local_filesystem_status(self, source_id: str) -> Dict[str, Any]:
        """Check the indexing status of a local filesystem source."""
        try:
            response = await self.client.get(
                f"{self.base_url}/v2/local-filesystem/{source_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to check local filesystem status: {str(e)}")

    # ========================================================================
    # CHROMA PACKAGE SEARCH METHODS
    # ========================================================================

    async def package_search_grep(
        self,
        registry: str,
        package_name: str,
        pattern: str,
        version: Optional[str] = None,
        language: Optional[str] = None,
        filename_sha256: Optional[str] = None,
        a: Optional[int] = None,
        b: Optional[int] = None,
        c: Optional[int] = None,
        head_limit: Optional[int] = None,
        output_mode: str = "content"
    ) -> Dict[str, Any]:
        """Execute grep search on package source code via Chroma."""
        try:
            payload = {
                "registry": registry,
                "package_name": package_name,
                "pattern": pattern,
                "version": version,
                "language": language,
                "filename_sha256": filename_sha256,
                "a": a,
                "b": b,
                "c": c,
                "head_limit": head_limit,
                "output_mode": output_mode
            }

            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            response = await self.client.post(
                f"{self.base_url}/v2/package-search/grep",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to search package with grep: {str(e)}")

    async def package_search_hybrid(
        self,
        registry: str,
        package_name: str,
        semantic_queries: List[str],
        version: Optional[str] = None,
        filename_sha256: Optional[str] = None,
        pattern: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute hybrid semantic search on package source code via Chroma."""
        try:
            payload = {
                "registry": registry,
                "package_name": package_name,
                "semantic_queries": semantic_queries,
                "version": version,
                "filename_sha256": filename_sha256,
                "pattern": pattern,
                "language": language
            }

            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            response = await self.client.post(
                f"{self.base_url}/v2/package-search/hybrid",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to search package with hybrid search: {str(e)}")

    async def package_search_read_file(
        self,
        registry: str,
        package_name: str,
        filename_sha256: str,
        start_line: int,
        end_line: int,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read specific lines from a package file via Chroma."""
        try:
            payload = {
                "registry": registry,
                "package_name": package_name,
                "filename_sha256": filename_sha256,
                "start_line": start_line,
                "end_line": end_line,
                "version": version
            }

            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            response = await self.client.post(
                f"{self.base_url}/v2/package-search/read-file",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to read package file: {str(e)}")

    # ========================================================================
    # CONTEXT SHARING METHODS
    # ========================================================================

    async def save_context(
        self,
        title: str,
        summary: str,
        content: str,
        agent_source: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        nia_references: Optional[Dict[str, Any]] = None,
        edited_files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Save a conversation context for cross-agent sharing."""
        try:
            payload = {
                "title": title,
                "summary": summary,
                "content": content,
                "agent_source": agent_source,
                "tags": tags or [],
                "metadata": metadata or {}
            }

            # Add new structured fields if provided
            if nia_references is not None:
                payload["nia_references"] = nia_references
            if edited_files is not None:
                payload["edited_files"] = edited_files

            response = await self.client.post(
                f"{self.base_url}/v2/contexts",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to save context: {str(e)}")

    async def list_contexts(
        self,
        limit: int = 20,
        offset: int = 0,
        tags: Optional[str] = None,
        agent_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """List user's conversation contexts with pagination and filtering."""
        try:
            params = {
                "limit": limit,
                "offset": offset
            }

            if tags:
                params["tags"] = tags
            if agent_source:
                params["agent_source"] = agent_source

            response = await self.client.get(
                f"{self.base_url}/v2/contexts",
                params=params
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to list contexts: {str(e)}")

    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """Get a specific conversation context by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/contexts/{context_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to get context: {str(e)}")

    async def update_context(
        self,
        context_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update an existing conversation context."""
        try:
            payload = {}

            if title is not None:
                payload["title"] = title
            if summary is not None:
                payload["summary"] = summary
            if content is not None:
                payload["content"] = content
            if tags is not None:
                payload["tags"] = tags
            if metadata is not None:
                payload["metadata"] = metadata

            response = await self.client.put(
                f"{self.base_url}/v2/contexts/{context_id}",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to update context: {str(e)}")

    async def delete_context(self, context_id: str) -> bool:
        """Delete a conversation context."""
        try:
            response = await self.client.delete(f"{self.base_url}/v2/contexts/{context_id}")
            response.raise_for_status()
            return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to delete context: {e}")
            return False

    async def search_contexts(
        self,
        query: str,
        limit: int = 20,
        tags: Optional[str] = None,
        agent_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search conversation contexts by content, title, or summary."""
        try:
            params = {
                "q": query,
                "limit": limit
            }

            if tags:
                params["tags"] = tags
            if agent_source:
                params["agent_source"] = agent_source

            response = await self.client.get(
                f"{self.base_url}/v2/contexts/search",
                params=params
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to search contexts: {str(e)}")