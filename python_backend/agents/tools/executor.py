"""
Tool Executor - Executes tools called by the LLM
"""

import asyncio
from typing import List, Dict, Any

from .registry import get_tool_function

class ToolExecutor:
    """
    Executes tools called by the LLM.
    Handles parallel execution and error handling.
    """
    
    async def execute_parallel(
        self, 
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls in parallel for speed.
        """
        tasks = [
            self._execute_single(tc)
            for tc in tool_calls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            {
                "tool_call_id": tc["tool_call_id"],
                "function_name": tc["function_name"],
                "result": result if not isinstance(result, Exception) else {
                    "error": str(result),
                    "message": f"Tool execution failed: {str(result)}"
                }
            }
            for tc, result in zip(tool_calls, results)
        ]
    
    async def _execute_single(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call"""
        function_name = tool_call["function_name"]
        arguments = tool_call["arguments"]
        
        tool_function = get_tool_function(function_name)
        
        if not tool_function:
            return {
                "error": f"Unknown tool: {function_name}",
                "message": f"I tried to use a tool called '{function_name}' but it's not available yet."
            }
        
        try:
            result = await tool_function(**arguments)
            return result
        except Exception as e:
            print(f"❌ Tool execution error ({function_name}): {e}")
            return {
                "error": str(e),
                "message": f"I had trouble running '{function_name}': {str(e)}"
            }

