![image](https://github.com/user-attachments/assets/939a7ad6-f572-4abf-a3db-12030d670ef0)

# LWAgents: A Library for Graph-Driven AI Agents with Tool Integration

**LWAgents** is a flexible and extensible Python library designed for building graph-driven workflows powered by AI agents. It provides a robust framework for creating, managing, and executing workflows where nodes represent states or tasks, edges represent transitions, and AI agents or deterministic logic decide the next steps.

Whether you're designing task-oriented AI systems, probabilistic workflows, or integrating external tools into your decision-making processes, **LWAgents** offers the structure and flexibility to get started quickly.

---

## Key Features

- **Graph-Based Workflow Execution**:
  - Represent workflows as graphs with nodes (tasks) and edges (transitions).
  - Seamlessly execute workflows step-by-step.

- **AI Agent Integration**:
  - Integrate language models (like OpenAI's GPT) as decision-making agents.
  - Use agents for routing, decision-making, or task execution.

- **Tooling Support**:
  - Extend functionality by defining custom tools and decorators.
  - Easily integrate tools for calculations, API calls, or other tasks.

- **Dynamic Transitions**:
  - Support for conditional transitions via edge logic.
  - Direct traversal capabilities allow agents or nodes to dynamically decide the next step.

- **State Management**:
  - Built-in support for maintaining and updating both local graph state and global agent state during execution.
  - Global agent state allows tracking all agent actions across the entire workflow.
  - Record detailed histories of execution for debugging and analysis.

- **Extensibility**:
  - Modular architecture enables easy customization and scaling.
  - Add new nodes, tools, or agents with minimal setup.

---

## Installation

### Using pip
To install the library, run:

```
pip install lwagents
```
From Source
To install the library from source:

Clone the repository:
```
git clone https://github.com/HenningGC/lwagents.git
```
Navigate to the project directory:
```
cd lwagents
```
Install the package in editable mode:
```
pip install -e .
```
### Basic Usage
Define a Simple Workflow
Define Nodes and Edges: Nodes represent tasks, and edges define transitions between them.

```
from lwagents import Graph, Node, Edge

def print_task(val):
    print(val)
    return

start_node = Node(node_name="start", kind="START", command=print_task, parameters={"val": "Starting..."})
task_node = Node(node_name="task", kind="STATE", command=print_task, parameters={"val": "Performing a task..."})
end_node = Node(node_name="end", kind="TERMINAL")

edge1 = Edge(edge_name="to_task")
edge2 = Edge(edge_name="to_end")
```
Create a Graph: Connect nodes with edges to define transitions.
```
with Graph(state=YourGlobalState) as graph:
    start_node.connect(to_node=task_node, edge=edge1)
    task_node.connect(to_node=end_node, edge=edge1)


```
Run the Workflow: Execute the graph starting from the START node.
```
graph.run(start_node=start_node, streaming=True)
```

### Advanced Features
AI Agents for Decision-Making
Integrate AI agents (like OpenAI's GPT) to dynamically route or execute tasks:

```
from lwagents import LLMAgent, LLMFactory

# Initialize an LLM model
factory = LLMFactory()
llm_model = factory.create_model("gpt", openai_api_key="your_openai_api_key")
agent = LLMAgent(name="my_agent", llm_model=llm_model)

# Use the agent in a node
decision_node = Node(
    node_name="decision",
    kind="STATE",
    command=lambda prompt: agent.action(prompt=prompt),
    parameters={"prompt": [{"role": "user", "content": "Which task should I perform next?"}]}
)
```

Global Agent State Management
Access and manage global agent state across your workflow:

```
from lwagents.state import get_global_agent_state, reset_global_agent_state

# Reset global state at the beginning (optional, good for testing)
reset_global_agent_state()

# Access global state to see all agent activities
global_state = get_global_agent_state()
print(f"Total agent actions performed: {len(global_state.history)}")

# Print the global agent state history
global_state.print_history()
```

Tools for Task Execution
Define custom tools for your agents to use:

```
from lwagents import Tool

@Tool
def calculate_sum(a, b):
    return a + b

# Use the tool in a node
agent = LLMAgent(name="tool_agent", llm_model=llm_model, tools=[calculate_sum])

```

Node Routing
Explicitly define router nodes that use global agent state.

```
@node_router
def test_router(agent):
    global_state = get_global_agent_state()
    prompt =[{"role": "system", "content": "You are an agent router and your task is to decide which node to travel to next based on the task and results thus far. Your next answer must only return the node name."},
     {"role": "user", "content": f"You have the following nodes at your disposal: get_division, search_internet, get_sum, end. You have to decide in which order you will visit each node based on this objective: get sum, then divide and search on the internet. These are the results thus far: {global_state.history}"}]
    result = agent.action(prompt = prompt)

    return result.content
```
## Project Structure

```
lwagents/
├── lwagents/               # Library code
│   ├── __init__.py         # Initialize the package
│   ├── graph.py            # Graph-related functionality
│   ├── state.py            # State management
│   ├── agent.py            # Agent implementation
│   ├── tools.py            # Tooling and decorators
│   ├── models.py           # Model-related code
│   ├── messages.py         # Message classes for agent communication
│   ├── logs.py             # Logging utilities
├── tests/                  # Test cases
├── examples/               # Example scripts
├── README.md               # Project documentation
├── pyproject.toml          # Build system requirements
├── requirements.txt        # Dependencies for the library
└── LICENSE                 # License for the library
```
Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch for your feature or bug fix.
Submit a pull request.

## License
This project is licensed under the MIT License.

Author
HenningGC https://github.com/HenningGC
