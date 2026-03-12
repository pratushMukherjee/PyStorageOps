"""
AI Deployment Agent with tool-calling capability.

Uses OpenAI's function calling to analyze projects, generate Dockerfiles,
diagnose errors, and suggest optimizations.
"""

import json
import os
from dataclasses import dataclass

from openai import OpenAI

try:
    from .prompts import SYSTEM_PROMPT
    from .tools import TOOLS, execute_tool
except ImportError:
    from prompts import SYSTEM_PROMPT
    from tools import TOOLS, execute_tool


@dataclass
class AgentResponse:
    message: str
    tool_calls: list[dict]
    tokens_used: int


class DeploymentAgent:
    """AI agent for deployment assistance with tool-calling."""

    def __init__(self, api_key: str | None = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY", ""))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.conversation: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str) -> AgentResponse:
        """Send a message and handle tool calls if needed."""
        self.conversation.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        tool_results = []

        # Handle tool calls
        if msg.tool_calls:
            self.conversation.append(msg)

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                result = execute_tool(fn_name, fn_args)
                tool_results.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": result,
                })

                self.conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Get final response after tool execution
            follow_up = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation,
            )
            final_msg = follow_up.choices[0].message
            self.conversation.append({"role": "assistant", "content": final_msg.content})

            return AgentResponse(
                message=final_msg.content or "",
                tool_calls=tool_results,
                tokens_used=response.usage.total_tokens + follow_up.usage.total_tokens,
            )

        # No tool calls — direct response
        self.conversation.append({"role": "assistant", "content": msg.content})
        return AgentResponse(
            message=msg.content or "",
            tool_calls=[],
            tokens_used=response.usage.total_tokens,
        )

    def reset(self):
        """Clear conversation history."""
        self.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
