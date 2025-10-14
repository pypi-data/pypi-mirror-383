#!/usr/bin/env python3
"""
MCP CLI - Comprehensive Command-Line Interface for MCP Server

Features:
- Search and use Prompts, Resources, and Tools
- Proper display for text, images, URLs, JSON
- Interactive mode and direct command mode
- Save responses to files
- Syntax highlighting and formatting
"""

import asyncio
import aiohttp
import json
import sys
import argparse
import base64
import webbrowser
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Try to import optional dependencies for better display
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️  Install 'rich' for better formatting: pip install rich")

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


class MCPCLIClient:
    """Extended MCP Client with support for prompts, resources, and tools"""

    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp"
        self.search_endpoint = f"{base_url}/search"
        self.capabilities_endpoint = f"{base_url}/capabilities"
        self.security_endpoint = f"{base_url}/security"
        self.console = Console() if HAS_RICH else None

    async def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a JSON-RPC request to MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Use single /mcp endpoint for all JSON-RPC requests
                async with session.post(
                    self.mcp_endpoint,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        return self._parse_sse_response(response_text)
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}: {error_text}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def _parse_sse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response"""
        if "data: " in response_text:
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        return json.loads(line[6:])
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON in response", "success": False}

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "Could not parse response", "success": False}

    async def search(self, query: str, filters: Optional[Dict] = None, max_results: int = 10) -> Dict[str, Any]:
        """Search across all MCP capabilities"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "max_results": max_results
                }
                if filters:
                    payload["filters"] = filters

                async with session.post(
                    self.search_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_prompt(self, name: str, arguments: Optional[Dict] = None) -> Dict[str, Any]:
        """Get a prompt with optional arguments"""
        return await self._make_mcp_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })

    async def call_tool(self, name: str, arguments: Optional[Dict] = None) -> Dict[str, Any]:
        """Call a tool"""
        return await self._make_mcp_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource"""
        return await self._make_mcp_request("resources/read", {
            "uri": uri
        })

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.capabilities_endpoint) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_security_levels(self) -> Dict[str, Any]:
        """Get security levels for all tools"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.security_endpoint}/levels") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}


class MCPCLIDisplay:
    """Handle display of different content types"""

    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and HAS_RICH
        self.console = Console() if self.use_rich else None

    def print_header(self, text: str):
        """Print a header"""
        if self.use_rich:
            self.console.print(f"\n[bold cyan]{text}[/bold cyan]")
        else:
            print(f"\n{'=' * 60}")
            print(text)
            print('=' * 60)

    def print_json(self, data: Dict[str, Any], title: str = None):
        """Pretty print JSON data"""
        if title:
            self.print_header(title)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if self.use_rich:
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            print(json_str)

    def print_text(self, text: str, title: str = None):
        """Print text content"""
        if title:
            self.print_header(title)

        if self.use_rich:
            self.console.print(text)
        else:
            print(text)

    def print_markdown(self, md_text: str):
        """Print markdown content"""
        if self.use_rich:
            md = Markdown(md_text)
            self.console.print(md)
        else:
            print(md_text)

    def print_table(self, data: List[Dict[str, Any]], title: str = None):
        """Print data as a table"""
        if not data:
            self.print_text("No data to display")
            return

        if self.use_rich:
            table = Table(title=title, show_header=True, header_style="bold magenta")

            # Get all keys from first item
            keys = list(data[0].keys())
            for key in keys:
                table.add_column(key, style="cyan")

            for item in data:
                row = [str(item.get(k, "")) for k in keys]
                table.add_row(*row)

            self.console.print(table)
        else:
            # Simple text table
            if title:
                print(f"\n{title}")
            keys = list(data[0].keys())

            # Header
            header = " | ".join(keys)
            print(header)
            print("-" * len(header))

            # Rows
            for item in data:
                row = " | ".join(str(item.get(k, "")) for k in keys)
                print(row)

    def print_search_results(self, results: List[Dict[str, Any]]):
        """Print search results in a formatted way"""
        if not results:
            self.print_text("No results found")
            return

        for idx, result in enumerate(results, 1):
            name = result.get('name', 'Unknown')
            type_ = result.get('type', 'Unknown')
            desc = result.get('description', 'No description')
            score = result.get('similarity_score', 0)

            if self.use_rich:
                panel_content = f"[bold]Type:[/bold] {type_}\n"
                panel_content += f"[bold]Description:[/bold] {desc[:200]}\n"
                if score:
                    panel_content += f"[bold]Score:[/bold] {score:.3f}"

                panel = Panel(
                    panel_content,
                    title=f"[{idx}] {name}",
                    border_style="green"
                )
                self.console.print(panel)
            else:
                print(f"\n[{idx}] {name}")
                print(f"  Type: {type_}")
                print(f"  Description: {desc[:200]}")
                if score:
                    print(f"  Score: {score:.3f}")

    def print_image_info(self, image_data: str, display: bool = True):
        """Print image information and optionally display"""
        # Detect if it's a URL or base64
        if image_data.startswith('http'):
            self.print_text(f"Image URL: {image_data}")
            if display:
                self.print_text("Opening in browser...")
                webbrowser.open(image_data)
        elif image_data.startswith('data:image'):
            # Base64 encoded image
            self.print_text("Base64 encoded image detected")
            self.print_text(f"Data: {image_data[:100]}...")

            # Option to save
            save = input("Save to file? (y/n): ").lower() == 'y'
            if save:
                filename = input("Filename (default: image.png): ").strip() or "image.png"
                self._save_base64_image(image_data, filename)
        else:
            self.print_text(f"Unknown image format: {image_data[:100]}...")

    def _save_base64_image(self, data_url: str, filename: str):
        """Save base64 image to file"""
        try:
            # Extract base64 part
            if ';base64,' in data_url:
                base64_data = data_url.split(';base64,')[1]
            else:
                base64_data = data_url

            # Decode and save
            image_data = base64.b64decode(base64_data)
            with open(filename, 'wb') as f:
                f.write(image_data)
            self.print_text(f"✅ Saved to {filename}")
        except Exception as e:
            self.print_text(f"❌ Error saving image: {e}")

    def print_error(self, error: str):
        """Print error message"""
        if self.use_rich:
            self.console.print(f"[bold red]❌ Error:[/bold red] {error}")
        else:
            print(f"❌ Error: {error}")

    def print_success(self, message: str):
        """Print success message"""
        if self.use_rich:
            self.console.print(f"[bold green]✅ {message}[/bold green]")
        else:
            print(f"✅ {message}")


class MCPCLI:
    """Main MCP CLI application"""

    def __init__(self, base_url: str = "http://localhost:8081"):
        self.client = MCPCLIClient(base_url)
        self.display = MCPCLIDisplay()
        self.history = []

    async def search_command(self, query: str, type_filter: Optional[str] = None, max_results: int = 10):
        """Search for prompts, resources, or tools"""
        self.display.print_header(f"🔍 Searching for: {query}")

        filters = {}
        if type_filter:
            filters["types"] = [type_filter]

        result = await self.client.search(query, filters, max_results)

        if result.get('status') == 'success':
            results = result.get('results', [])
            self.display.print_search_results(results)
            return results
        else:
            self.display.print_error(result.get('error', 'Search failed'))
            return []

    async def get_prompt_command(self, name: str, args: Optional[Dict] = None):
        """Get a prompt"""
        self.display.print_header(f"📝 Getting prompt: {name}")

        result = await self.client.get_prompt(name, args)

        if 'result' in result:
            messages = result['result'].get('messages', [])
            if messages:
                for msg in messages:
                    content = msg.get('content', {})
                    text = content.get('text', '')
                    self.display.print_text(text, "Prompt Content")
        else:
            self.display.print_json(result, "Prompt Response")

    async def call_tool_command(self, name: str, args: Optional[Dict] = None):
        """Call a tool"""
        self.display.print_header(f"🔧 Calling tool: {name}")

        result = await self.client.call_tool(name, args)

        if 'result' in result:
            content_list = result['result'].get('content', [])
            if content_list:
                for content in content_list:
                    if content.get('type') == 'text':
                        text = content.get('text', '')
                        try:
                            # Try to parse as JSON
                            parsed = json.loads(text)
                            self.display.print_json(parsed, "Tool Response")
                        except:
                            self.display.print_text(text, "Tool Response")
        else:
            self.display.print_json(result, "Tool Response")

    async def read_resource_command(self, uri: str):
        """Read a resource"""
        self.display.print_header(f"📚 Reading resource: {uri}")

        result = await self.client.read_resource(uri)

        if 'result' in result:
            contents = result['result'].get('contents', [])
            if contents:
                for content in contents:
                    text = content.get('text', '')
                    mime_type = content.get('mimeType', 'text/plain')

                    if mime_type == 'application/json':
                        try:
                            parsed = json.loads(text)
                            self.display.print_json(parsed, "Resource Content")
                        except:
                            self.display.print_text(text, "Resource Content")
                    else:
                        # Check if it looks like markdown or JSON
                        if text.strip().startswith('{') or text.strip().startswith('['):
                            try:
                                parsed = json.loads(text)
                                self.display.print_json(parsed, "Resource Content")
                            except:
                                self.display.print_markdown(text)
                        elif text.strip().startswith('#'):
                            self.display.print_markdown(text)
                        else:
                            self.display.print_text(text, "Resource Content")
        else:
            self.display.print_json(result, "Resource Response")

    async def capabilities_command(self):
        """Show server capabilities"""
        self.display.print_header("📋 Server Capabilities")

        result = await self.client.get_capabilities()

        if result.get('status') == 'success':
            caps = result.get('capabilities', {})

            # Show tools
            tools = caps.get('tools', {})
            if tools:
                self.display.print_text(f"\n🔧 Tools: {tools.get('count', 0)} available")

            # Show prompts
            prompts = caps.get('prompts', {})
            if prompts:
                self.display.print_text(f"📝 Prompts: {prompts.get('count', 0)} available")

            # Show resources
            resources = caps.get('resources', {})
            if resources:
                self.display.print_text(f"📚 Resources: {resources.get('count', 0)} available")

            self.display.print_json(caps, "Full Capabilities")
        else:
            self.display.print_error(result.get('error', 'Failed to get capabilities'))

    def _parse_natural_language(self, user_input: str) -> tuple:
        """Parse natural language input into command and args"""
        user_input_lower = user_input.lower()

        # Natural language patterns for storage
        if any(word in user_input_lower for word in ['store', 'save', 'add', 'upload', 'ingest']):
            if 'pdf' in user_input_lower or '.pdf' in user_input:
                return ('store_pdf', user_input)
            elif any(word in user_input_lower for word in ['knowledge', 'document', 'text']):
                return ('store_knowledge', user_input)

        # Natural language patterns for search
        if any(word in user_input_lower for word in ['search', 'find', 'look for', 'query']):
            query = user_input
            for word in ['search', 'find', 'look for', 'query', 'for']:
                query = query.replace(word, '').strip()
            return ('search', query)

        # Natural language patterns for RAG/Q&A
        if any(word in user_input_lower for word in ['what', 'how', 'why', 'when', 'who', 'explain', 'tell me']):
            return ('ask', user_input)

        # Natural language patterns for capabilities
        if any(word in user_input_lower for word in ['show me tools', 'list tools', 'what can you do', 'capabilities']):
            return ('capabilities', '')

        return (None, user_input)

    async def interactive_mode(self):
        """Run in interactive mode with natural language support"""
        self.display.print_header("🤖 ISA MCP CLI - Intelligent Assistant")
        self.display.print_text("Hi! I'm your ISA MCP assistant. I can help you:")
        self.display.print_text("  • Store knowledge (PDFs, documents, text)")
        self.display.print_text("  • Search your knowledge base")
        self.display.print_text("  • Answer questions using RAG")
        self.display.print_text("  • Explore available tools and capabilities")
        self.display.print_text("\nJust tell me what you need in natural language, or type 'help' for examples.\n")

        # Setup prompt toolkit if available
        if HAS_PROMPT_TOOLKIT:
            commands = ['search', 'prompt', 'tool', 'resource', 'capabilities', 'help', 'exit']
            completer = WordCompleter(commands, ignore_case=True)
            session = PromptSession(
                history=InMemoryHistory(),
                auto_suggest=AutoSuggestFromHistory(),
                completer=completer
            )

        while True:
            try:
                if HAS_PROMPT_TOOLKIT:
                    user_input = await session.prompt_async('You: ')
                else:
                    user_input = input('You: ')

                user_input = user_input.strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q', 'bye', 'goodbye']:
                    self.display.print_success("👋 Goodbye! Come back anytime.")
                    break

                if user_input.lower() in ['help', '?']:
                    self.show_help()
                    continue

                # Try to parse as natural language first
                nl_command, nl_args = self._parse_natural_language(user_input)

                if nl_command == 'search':
                    self.display.print_text(f"\n💭 I'll search for: {nl_args}\n")
                    await self.search_command(nl_args)

                elif nl_command == 'ask':
                    self.display.print_text(f"\n🤔 Let me find an answer to: {nl_args}\n")
                    # Use knowledge_response tool for questions
                    await self.call_tool_command('knowledge_response', {
                        'user_id': 'test_user_rag_page',
                        'query': nl_args,
                        'response_options': {
                            'use_pdf_context': True,
                            'context_limit': 3,
                            'model': 'gpt-4o-mini',
                            'provider': 'yyds'
                        }
                    })

                elif nl_command == 'store_pdf' or nl_command == 'store_knowledge':
                    self.display.print_text("\n📄 To store a PDF, please use the following format:")
                    self.display.print_text("tool store_knowledge {\"user_id\": \"test_user_rag_page\", \"content\": \"/path/to/file.pdf\", \"content_type\": \"pdf\", \"options\": {\"enable_vlm_analysis\": true, \"enable_minio_upload\": true}}")

                elif nl_command == 'capabilities':
                    self.display.print_text("\n📋 Here are my capabilities:\n")
                    await self.capabilities_command()

                else:
                    # Fall back to traditional command parsing
                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    args_str = parts[1] if len(parts) > 1 else ""

                    if command == 'search':
                        await self.search_command(args_str)
                    elif command == 'prompt':
                        # Format: prompt <name> [args_json]
                        name_and_args = args_str.split(maxsplit=1)
                        name = name_and_args[0]
                        args = json.loads(name_and_args[1]) if len(name_and_args) > 1 else None
                        await self.get_prompt_command(name, args)
                    elif command == 'tool':
                        # Format: tool <name> [args_json]
                        name_and_args = args_str.split(maxsplit=1)
                        name = name_and_args[0]
                        args = json.loads(name_and_args[1]) if len(name_and_args) > 1 else None
                        await self.call_tool_command(name, args)
                    elif command == 'resource':
                        # Format: resource <uri>
                        await self.read_resource_command(args_str)
                    elif command == 'capabilities':
                        await self.capabilities_command()
                    else:
                        self.display.print_text(f"\n💡 I'm not sure what you mean by '{user_input}'.")
                        self.display.print_text("Try asking me to:")
                        self.display.print_text("  • 'search for something'")
                        self.display.print_text("  • 'what is ...?' (I'll answer using RAG)")
                        self.display.print_text("  • 'show me tools' or 'capabilities'")
                        self.display.print_text("  • or use a specific command (type 'help')")

            except KeyboardInterrupt:
                self.display.print_text("\n\n💡 Tip: Type 'exit' or 'quit' to leave gracefully.")
                continue
            except Exception as e:
                self.display.print_error(f"Oops, something went wrong: {e}")
                self.display.print_text("Don't worry, I'm still here! Try again or type 'help'.")

    def show_help(self):
        """Show help information"""
        help_text = """
ISA MCP CLI - You can talk to me naturally or use specific commands!

🗣️  NATURAL LANGUAGE (Talk to me like Claude Code!):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • "search for web tools"
  • "find knowledge about AI"
  • "what is machine learning?"
  • "how do I create a customer?"
  • "show me what you can do"
  • "list all tools"

📝 TRADITIONAL COMMANDS (For precise control):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 search <query>              - Search for prompts, resources, and tools
🔧 tool <name> [args_json]     - Call a tool (with optional arguments as JSON)
📝 prompt <name> [args_json]   - Get a prompt (with optional arguments as JSON)
📚 resource <uri>              - Read a resource
📋 capabilities                - Show server capabilities
❓ help / ?                    - Show this help message
🚪 exit / quit / bye          - Exit the CLI

💡 QUICK EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Natural:
  search for knowledge tools
  what is偏差？
  show me tools

Specific Commands:
  tool store_knowledge {"user_id": "test_user_rag_page", "content": "/path/to/file.pdf", "content_type": "pdf", "options": {"enable_vlm_analysis": true}}
  tool search_knowledge {"user_id": "test_user_rag_page", "query": "样本采集", "search_options": {"top_k": 3}}
  tool knowledge_response {"user_id": "test_user_rag_page", "query": "什么是偏差？", "response_options": {"use_pdf_context": true}}

🎯 PRO TIP: I understand both Chinese and English! Try asking me anything.
"""
        self.display.print_text(help_text)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MCP CLI - Comprehensive command-line interface for MCP server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s

  # Search
  %(prog)s search "web search"

  # Call tool
  %(prog)s tool web_search '{"query": "AI", "count": 3}'

  # Get prompt
  %(prog)s prompt default_reason_prompt '{"user_message": "Hello"}'

  # Read resource
  %(prog)s resource event://status

  # Show capabilities
  %(prog)s capabilities
"""
    )

    parser.add_argument('--url', default='http://localhost:8081',
                       help='MCP server URL (default: http://localhost:8081)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for prompts/resources/tools')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=['prompt', 'tool', 'resource'],
                              help='Filter by type')
    search_parser.add_argument('--max', type=int, default=10, help='Max results')

    # Prompt command
    prompt_parser = subparsers.add_parser('prompt', help='Get a prompt')
    prompt_parser.add_argument('name', help='Prompt name')
    prompt_parser.add_argument('args', nargs='?', help='Arguments as JSON')

    # Tool command
    tool_parser = subparsers.add_parser('tool', help='Call a tool')
    tool_parser.add_argument('name', help='Tool name')
    tool_parser.add_argument('args', nargs='?', help='Arguments as JSON')

    # Resource command
    resource_parser = subparsers.add_parser('resource', help='Read a resource')
    resource_parser.add_argument('uri', help='Resource URI')

    # Capabilities command
    subparsers.add_parser('capabilities', help='Show server capabilities')

    args = parser.parse_args()

    # Create CLI instance
    cli = MCPCLI(args.url)

    # Execute command or start interactive mode
    if args.command == 'search':
        await cli.search_command(args.query, args.type, args.max)
    elif args.command == 'prompt':
        prompt_args = json.loads(args.args) if args.args else None
        await cli.get_prompt_command(args.name, prompt_args)
    elif args.command == 'tool':
        tool_args = json.loads(args.args) if args.args else None
        await cli.call_tool_command(args.name, tool_args)
    elif args.command == 'resource':
        await cli.read_resource_command(args.uri)
    elif args.command == 'capabilities':
        await cli.capabilities_command()
    else:
        # No command - start interactive mode
        await cli.interactive_mode()


def cli_entry_point():
    """Entry point for console script (pip install)"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

if __name__ == '__main__':
    cli_entry_point()
