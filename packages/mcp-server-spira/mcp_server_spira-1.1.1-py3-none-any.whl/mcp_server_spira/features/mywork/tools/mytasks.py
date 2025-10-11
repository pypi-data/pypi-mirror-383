"""
Provides operations for working with the Spira tasks I have been assigned

This module provides MCP tools for retrieving and updating my assigned tasks.
"""

from mcp_server_spira.features.formatting import format_task
from mcp_server_spira.features.common import get_spira_client

def _get_my_tasks_impl(spira_client) -> str:
    """
    Implementation of retrieving my assigned Spira tasks.

    Args:
        spira_client: The Inflectra Spira API client instance
                
    Returns:
        Formatted string containing the list of assigned tasks
    """
    try:
        # Get the list of open tasks for the current user
        tasks_url = "tasks"
        tasks = spira_client.make_spira_api_get_request(tasks_url)

        if not tasks:
            return "The current user does not have any tasks."

        # Format the tasks into human readable data
        formatted_results = []
        for task in tasks[:25]:  # Only show first 25 tasks
            task_info = format_task(task)
            formatted_results.append(task_info)

        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"There was a problem using this tool: {e}"
    
def register_tools(mcp) -> None:
    """
    Register my work tools with the MCP server.
    
    Args:
        mcp: The FastMCP server instance
    """

    @mcp.tool()
    def get_my_tasks() -> str:
        """
        Retrieves a list of the open tasks that are assigned to me
        
        Use this tool when you need to:
        - View the complete details of a specific task
        - Examine the current state, assigned user, and other properties
        - Get information about multiple tasks at once
        - Access the full description and selected fields of tasks
                    
        Returns:
            Formatted string containing comprehensive information for the
            requested list of tasks, including name, id, description and key fields,
            formatted as markdown with clear section headings
        """
        try:
            spira_client = get_spira_client()
            return _get_my_tasks_impl(spira_client)
        except Exception as e:
            return f"Error: {str(e)}"
        