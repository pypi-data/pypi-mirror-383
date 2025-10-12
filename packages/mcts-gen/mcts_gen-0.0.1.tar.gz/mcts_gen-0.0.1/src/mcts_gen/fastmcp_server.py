from fastmcp import FastMCP
from mcts_gen.services.ai_gp_simulator import AiGpSimulator

# 1. Create the core FastMCP server instance
mcp = FastMCP(
    name="mcts_gen_simulator_server"
)

# 2. Create an instance of our stateful simulator class.
#    The simulator's __init__ method will register its own methods as tools.
simulator = AiGpSimulator(mcp)

# 3. Run the server
if __name__ == "__main__":
    mcp.run()