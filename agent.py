import os
import sys
import subprocess
import json
from dotenv import load_dotenv
from groq import Groq
from duckduckgo_search import DDGS
import requests

# Load environment variables from .env file
load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file.")
        print("Please create a .env file based on .env.example and add your API key.")
        return None
    return Groq(api_key=api_key)

# Tool Definitions
def download_image(url, save_path):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"Successfully downloaded image to {save_path}"
    except Exception as e:
        return f"Error downloading image from {url}: {str(e)}"

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error performing web search: {str(e)}"

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to {path}: {str(e)}"

def make_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory {path}: {str(e)}"

def git_operation(command_type, message=None, repo_url=None):
    username = os.getenv("GIT_USERNAME")
    token = os.getenv("GIT_TOKEN")
    default_repo = "https://git.meowcat.site/james/thing.git"
    
    if repo_url is None:
        repo_url = default_repo
        
    # Inject credentials into URL
    if username and token and "://" in repo_url and "@" not in repo_url:
        protocol, rest = repo_url.split("://", 1)
        cred_url = f"{protocol}://{username}:{token}@{rest}"
    else:
        cred_url = repo_url

    try:
        if command_type == "clone":
            cmd = f"git clone {cred_url} ."
        elif command_type == "init":
            cmd = "git init"
        elif command_type == "add":
            cmd = "git add ."
        elif command_type == "commit":
            cmd = f'git commit -m "{message or "Update"}"'
        elif command_type == "push":
            # For push, we need to ensure the remote is set with credentials
            subprocess.run("git remote remove origin", shell=True, capture_output=True)
            subprocess.run(f"git remote add origin {cred_url}", shell=True, capture_output=True)
            cmd = "git push -u origin master"
        elif command_type == "pull":
            cmd = "git pull origin master"
        else:
            return f"Unknown git operation: {command_type}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return f"Git {command_type} executed. Exit code: {result.returncode}\nOutput:\n{output}"
    except Exception as e:
        return f"Error executing git operation: {str(e)}"

def run_command(command):
    try:
        # Prevent manual git push/pull/clone to encourage git_operation tool
        if any(git_cmd in command for git_cmd in ["git push", "git pull", "git clone"]):
            return "Please use the 'git_operation' tool for push, pull, or clone to ensure credentials are handled correctly."
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return f"Command executed. Exit code: {result.returncode}\nOutput:\n{output}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates directories if they don't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to the file."},
                    "content": {"type": "string", "description": "The content to write."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_directory",
            "description": "Create a new directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to the directory."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to run."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information using DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_image",
            "description": "Download an image from a URL and save it locally.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL of the image to download."},
                    "save_path": {"type": "string", "description": "The local path where the image should be saved (e.g., 'assets/image.png')."}
                },
                "required": ["url", "save_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_operation",
            "description": "Perform a Git operation (clone, init, add, commit, push, pull) with automatic credential handling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command_type": {
                        "type": "string", 
                        "enum": ["clone", "init", "add", "commit", "push", "pull"],
                        "description": "The type of Git command to run."
                    },
                    "message": {
                        "type": "string", 
                        "description": "Commit message (required for 'commit')."
                    },
                    "repo_url": {
                        "type": "string", 
                        "description": "Optional repository URL. Defaults to the James Game repo."
                    }
                },
                "required": ["command_type"]
            }
        }
    }
]

class CodeAgent:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.client = get_groq_client()
        self.model = model
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a coding agent with tools. Build 'james game' (3D shooter) using web technologies. "
                    "First, make a new directory for the game. Use Git for everything via the 'git_operation' tool. "
                    "Use download_image to fetch textures and web_search for info. "
                    "APPLY the downloaded images as textures in your 3D scenes. "
                    "Use tools one by one. Use the function-calling API or write: tool_name{\"arg\": \"val\"} in your text. "
                    "\nTOOLS: web_search, download_image, write_file, make_directory, run_command, git_operation."
                )
            }
        ]

    def parse_and_execute_textual_tool_calls(self, text):
        import re
        # Look for patterns like tool_name{"arg": "val"}
        patterns = [
            r'(\w+)\s*(\{.*?\})', # name{"..."}
            r'(\w+)\((.*?)\)'    # name(...)
        ]
        
        executed_any = False
        results = []
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                func_name = match.group(1)
                args_str = match.group(2)
                
                # Check if it's actually one of our tools
                if any(t["function"]["name"] == func_name for t in tools):
                    try:
                        # Try to parse args as JSON
                        if args_str.startswith('{'):
                            args = json.loads(args_str)
                        else:
                            # Not handled: positional args in name(...)
                            continue
                            
                        print(f"  [FALLBACK ACTION] {func_name}({args})")
                        
                        if func_name == "write_file":
                            result = write_file(args.get("path"), args.get("content"))
                        elif func_name == "make_directory":
                            result = make_directory(args.get("path"))
                        elif func_name == "run_command":
                            result = run_command(args.get("command"))
                        elif func_name == "web_search":
                            result = web_search(args.get("query"))
                        elif func_name == "download_image":
                            result = download_image(args.get("url"), args.get("save_path"))
                        elif func_name == "git_operation":
                            result = git_operation(args.get("command_type"), args.get("message"), args.get("repo_url"))
                        else:
                            result = "Unknown tool"
                            
                        print(f"  [RESULT] {result}")
                        results.append({
                            "role": "assistant",
                            "content": f"Executed {func_name} with result: {result}"
                        })
                        executed_any = True
                    except Exception:
                        continue
        return executed_any, results

    def process_tool_calls(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Clean logging
            print(f"  [ACTION] {function_name}({args})")
            
            if function_name == "write_file":
                result = write_file(args.get("path"), args.get("content"))
            elif function_name == "make_directory":
                result = make_directory(args.get("path"))
            elif function_name == "run_command":
                result = run_command(args.get("command"))
            elif function_name == "web_search":
                result = web_search(args.get("query"))
            elif function_name == "download_image":
                result = download_image(args.get("url"), args.get("save_path"))
            elif function_name == "git_operation":
                result = git_operation(args.get("command_type"), args.get("message"), args.get("repo_url"))
            else:
                result = "Unknown tool"
            
            print(f"  [RESULT] {result}")
            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": result
            })
        return results

    def chat(self, user_input, verbose=True):
        if not self.client:
            return "Groq client not initialized. Check your .env file."

        self.messages.append({"role": "user", "content": user_input})

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                self.messages.append(response_message)

                if response_message.tool_calls:
                    tool_results = self.process_tool_calls(response_message.tool_calls)
                    self.messages.extend(tool_results)
                elif response_message.content:
                    # Fallback for textual tool calls
                    executed_any, fallback_results = self.parse_and_execute_textual_tool_calls(response_message.content)
                    if executed_any:
                        self.messages.extend(fallback_results)
                        continue # Re-query model to react to results
                    
                    if verbose:
                        print(f"\nAgent: {response_message.content}")
                    return response_message.content
                else:
                    return "Model returned empty response."

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                if verbose:
                    print(error_msg)
                return error_msg

import time

def main():
    agent = CodeAgent()
    if not agent.client:
        return

    # Check for command-line arguments
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"--- Running Command: {user_input} ---")
        agent.chat(user_input, verbose=True)
        return

    # Infinite Automatic Mode
    print("--- Groq Code Agent (INFINITE AUTO MODE) ---")
    print("Starting mission loop...")
    
    first_run = True
    while True:
        try:
            if first_run:
                print("\n[Loop Start] Initial Mission: Building 'James Game'...")
                agent.chat("Start your mission and build 'James Game' from scratch. Use web languages and textures.", verbose=True)
                first_run = False
            else:
                print("\n[Loop Tick] Checking for improvements or new tasks...")
                agent.chat("Review the current state of 'James Game'. If it can be improved (textures, features, polish), do so. Otherwise, look for ways to expand the app or build a companion app. Always use tools.", verbose=True)
            
            print("\nCycle complete. Waiting 10 seconds before next iteration...")
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nInfinite loop stopped by user.")
            break
        except Exception as e:
            print(f"\nError in loop: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main()
