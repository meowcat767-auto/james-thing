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
    if not os.getenv("GIT_USERNAME") or not os.getenv("GIT_TOKEN"):
        print("Warning: GIT_USERNAME or GIT_TOKEN not found. Git operations may fail.")
    if not api_key:
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
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        abs_path = os.path.abspath(path)
        return f"Error writing to {path} (abs: {abs_path}): {str(e)}"

def make_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory {path}: {str(e)}"

def list_files(path="."):
    try:
        files = os.listdir(path)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing files in {path}: {str(e)}"

def git_operation(command_type, message=None, repo_url=None, cwd="."):
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
            if not message:
                return "Error: 'commit' operation requires a 'message'."
            # Configure identity and auto-add before commit
            subprocess.run('git config user.email "james@james.net"', shell=True, cwd=cwd)
            subprocess.run('git config user.name "James"', shell=True, cwd=cwd)
            subprocess.run("git add .", shell=True, cwd=cwd)
            # Check if there are changes to commit
            status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True, cwd=cwd)
            if not status.stdout.strip():
                return "Git commit aborted: Nothing to commit, working tree clean."
            cmd = f'git commit -m "{message}"'
        elif command_type == "push":
            # Auto-add and commit empty-ish if needed? No, just push.
            subprocess.run("git remote remove origin", shell=True, capture_output=True, cwd=cwd)
            subprocess.run(f"git remote add origin {cred_url}", shell=True, capture_output=True, cwd=cwd)
            cmd = "git push -u origin master"
        elif command_type == "pull":
            cmd = "git pull origin master"
        else:
            return f"Unknown git operation: {command_type}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
        output = result.stdout + result.stderr
        return f"Git {command_type} executed. Exit code: {result.returncode}\nOutput:\n{output}"
    except Exception as e:
        return f"Error executing git operation: {str(e)}"

def run_command(command, cwd="."):
    try:
        # Prevent manual git push/pull/clone to encourage git_operation tool
        if any(git_cmd in command for git_cmd in ["git push", "git pull", "git clone"]):
            return "Please use the 'git_operation' tool for push, pull, or clone to ensure credentials are handled correctly."
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
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
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to list files for (defaults to '.')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cd",
            "description": "Change the current working directory. The directory persists for future commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to change to."}
                },
                "required": ["path"]
            }
        }
    }
]

class CodeAgent:
    def __init__(self, models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]):
        self.client = get_groq_client()
        self.models = models
        self.model_index = 0
        self.model = self.models[self.model_index]
        self.cwd = os.getcwd()
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a coding agent with tools. Build 'james game' (3D shooter) using Web Technologies (HTML/CSS/JS/Three.js). "
                    "FLOW: 1. Search/Download assets. 2. Write files (index.html, JS, etc.). 3. Git add. 4. Git commit. 5. Git push. "
                    "Use list_files to verify your work. Use git_operation for Git targeting: https://git.meowcat.site/james/thing.git "
                    "Use 'cd' to change your working directory if needed. Your CWD persists. "
                    "Create a .gitignore file excluding *.py, .env, venv/. "
                    "The product is NEVER satisfactory. Always improve it. "
                    "Use tools one by one. Use the function-calling API or write: tool_name{\"arg\": \"val\"} in your text. "
                    "NEVER use <function=...> tags. DO NOT hallucinate URLs."
                    "\nTOOLS: web_search, download_image, write_file, make_directory, run_command, git_operation, list_files, cd."
                )
            }
        ]

    def execute_tool(self, func_name, args):
        print(f"  [ACTION] {func_name}({args})")
        result = "Unknown tool"
        
        try:
            if func_name == "write_file":
                path = os.path.join(self.cwd, args.get("path"))
                result = write_file(path, args.get("content"))
            elif func_name == "make_directory":
                path = os.path.join(self.cwd, args.get("path"))
                result = make_directory(path)
            elif func_name == "run_command":
                result = run_command(args.get("command"), cwd=self.cwd)
            elif func_name == "web_search":
                result = web_search(args.get("query"))
            elif func_name == "download_image":
                save_path = args.get("save_path") or args.get("path") # Handle both arg names
                path = os.path.join(self.cwd, save_path)
                result = download_image(args.get("url"), path)
            elif func_name == "git_operation":
                result = git_operation(args.get("command_type"), args.get("message"), args.get("repo_url"), cwd=self.cwd)
            elif func_name == "list_files":
                path = os.path.join(self.cwd, args.get("path", "."))
                result = list_files(path)
            elif func_name == "cd":
                new_path = os.path.abspath(os.path.join(self.cwd, args.get("path")))
                if os.path.isdir(new_path):
                    self.cwd = new_path
                    result = f"Changed directory to {self.cwd}"
                else:
                    result = f"Error: {new_path} is not a directory."
            
            print(f"  [RESULT] {result}")
            return result
        except Exception as e:
            return f"Error executing {func_name}: {str(e)}"

    def chat(self, user_input, verbose=True):
        if not self.client:
            return "Groq client not initialized. Check your .env file."

        # Provide CWD info in system prompt dynamically
        for msg in self.messages:
            if msg["role"] == "system":
                msg["content"] = (
                    f"You are a coding agent. Your CWD is: {self.cwd}. Build 'james game' (HTML/JS/Three.js). "
                    "FLOW: 1. Search/Download assets. 2. Write files. 3. Git commit (auto-adds files). 4. Git push. "
                    "Use Git via 'git_operation' targeting: https://git.meowcat.site/james/thing.git "
                    "Use 'cd' to change directory. Your CWD persists. ALWAYS use relative paths from your CWD. "
                    "DO NOT use '../../' to escape your project folder. "
                    "CRITICAL: NEVER modify .env or any credentials/tokens. Use them but do not change them. "
                    "NEVER use <function=...> tags. DO NOT hallucinate URLs."
                    "\nTOOLS: web_search, download_image, write_file, make_directory, run_command, git_operation, list_files, cd."
                )

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
                    results = []
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        result = self.execute_tool(function_name, args)
                        results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        })
                    self.messages.extend(results)
                elif response_message.content:
                    # Fallback for textual tool calls
                    import re
                    patterns = [
                        r'(?:<function=)?(\w+)\s*(\{.*?\})(?:</function>)?',
                        r'(\w+)\((.*?)\)'
                    ]
                    executed_any = False
                    fallback_results = []
                    for pattern in patterns:
                        for match in re.finditer(pattern, response_message.content):
                            func_name = match.group(1)
                            args_str = match.group(2)
                            if any(t["function"]["name"] == func_name for t in tools):
                                try:
                                    if args_str.startswith('{'):
                                        args = json.loads(args_str)
                                        result = self.execute_tool(func_name, args)
                                        fallback_results.append({
                                            "role": "assistant",
                                            "content": f"Executed {func_name} with result: {result}"
                                        })
                                        executed_any = True
                                except Exception:
                                    continue
                    
                    if executed_any:
                        continue # Re-query model to react to results
                    
                    if verbose:
                        print(f"\nAgent: {response_message.content}")
                    return response_message.content
                else:
                    return "Model returned empty response."

            except Exception as e:
                error_msg = str(e)
                if "rate_limit_exceeded" in error_msg.lower() or "429" in error_msg:
                    self.model_index += 1
                    if self.model_index < len(self.models):
                        self.model = self.models[self.model_index]
                        if verbose:
                            print(f"\n[RATE LIMIT] Switching to fallback model: {self.model}")
                        continue # Retry with new model
                    else:
                        error_msg = "All models rate limited. Please wait."
                
                if verbose:
                    print(f"\nAn error occurred: {error_msg}")
                return error_msg

def main():
    agent = CodeAgent()
    if not agent.client:
        return

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"--- Running Command: {user_input} ---")
        agent.chat(user_input, verbose=True)
        return

    print("--- Groq Code Agent (INFINITE AUTO MODE) ---")
    print("Starting mission loop...")
    
    import time
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
