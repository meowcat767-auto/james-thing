import os
import sys
import subprocess
import json
from dotenv import load_dotenv
from groq import Groq
from duckduckgo_search import DDGS

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

def run_command(command):
    try:
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
                    "You are a powerful AI agent capable of building entire applications from scratch. "
                    "You have access to tools that allow you to write files, create directories, run commands, and search the web. "
                    "You may use any tools as you see fit, and any programming languages you see fit. "
                    "You also have support for Git. Git credentials (GIT_USERNAME and GIT_TOKEN) are available in the environment. "
                    "The target repository is: https://git.meowcat.site/james/thing.git "
                    "When using Git, you can push/pull using credentials in the URL: https://${GIT_USERNAME}:${GIT_TOKEN}@git.meowcat.site/james/thing.git "
                    "Your primary mission is to build a 3D shooter game called 'james game' using web languages (HTML/CSS/JS/Three.js) that can be easily deployed. "
                    "When asked to build an app or research a topic, think step-by-step. "
                    "1. If needed, use web_search to find the latest information or best practices. "
                    "2. Plan the structure. "
                    "3. Create the necessary directories. "
                    "4. Write the code files. "
                    "5. Initialize Git and commit if appropriate. "
                    "6. Provide instructions on how to run the app. "
                    "Always use the available tools to perform these actions."
                )
            }
        ]

    def process_tool_calls(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"\n[Tool Call] {function_name}({args})")
            
            if function_name == "write_file":
                result = write_file(args.get("path"), args.get("content"))
            elif function_name == "make_directory":
                result = make_directory(args.get("path"))
            elif function_name == "run_command":
                result = run_command(args.get("command"))
            elif function_name == "web_search":
                result = web_search(args.get("query"))
            else:
                result = "Unknown tool"
            
            print(f"[Result] {result}")
            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": result
            })
        return results

    def chat(self, user_input):
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
                    # Continue the loop to let the model react to tool results
                else:
                    return response_message.content

            except Exception as e:
                return f"An error occurred: {str(e)}"

def main():
    agent = CodeAgent()
    if not agent.client:
        return

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        response = agent.chat(user_input)
        print(f"\nAgent: {response}")
        return

    print("--- Groq Code Agent (App Builder) ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print("\nAgent is thinking...", end="", flush=True)
        response = agent.chat(user_input)
        print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()
