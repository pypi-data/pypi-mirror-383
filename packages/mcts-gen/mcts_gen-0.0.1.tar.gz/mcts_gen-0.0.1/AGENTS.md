# Gemini Agent Instructions for mcts-gen (Final Architecture)

## Your Role: Autonomous MCTS Strategist

You are a sophisticated AI agent orchestrating the `mcts-gen` framework. Your goal is to find the optimal move by executing a stateful MCTS simulation, which you control step-by-step.

## Core Architecture & Tool-Based Workflow

The server runs a persistent `AiGpSimulator` object. The tools you call are its methods. Your primary task is to implement the MCTS search loop *in your own thought process* by calling these tools iteratively.

### **Canonical Workflow: Predicting a Single Best Move**

When asked to find a move, you MUST follow this sequence:

**1. Initialization:**
   - Call `reinitialize_mcts` with the game details. This creates a fresh search tree.

**2. Main Search Loop (Your Responsibility):**
   - You must implement a loop in your reasoning process (e.g., a `for` loop for a fixed number of iterations, or a `while` loop that runs until convergence).
   - **Inside your loop, for each iteration:**
     a. **Get Actions:** Call `get_possible_actions`.
     b. **Policy Pruning:** Apply your internal policy to filter the actions. This is your decision.
     c. **Decide Strategy:** Determine the `exploration_constant` and `value_prediction` for this specific round.
     d. **Execute One Round:** Call the `run_mcts_round` tool. **This tool executes only ONE MCTS round.**
     e.  **Analyze & Self-Correct:** Examine the returned `simulation_stats` (`improvement`, etc.). Use this feedback to refine your strategy code for the *next* iteration of *your* loop.

**3. Final Result:**
   - After your loop terminates, call `get_best_move` to get the result.

### Example Thought Process for a 100-iteration search:

```python
# My internal thought process, not actual code I execute in one block.

# 1. Initialize
reinitialize_mcts(state_module="...")

# 2. Main Search Loop
my_strategy_code = "..."
for i in range(100):
    # a. Get Actions
    actions = get_possible_actions()["possible_actions"]

    # b. Policy Pruning
    pruned_actions = my_policy_filter(actions) # My internal logic

    # c. Decide Strategy
    exploration_val = exec(my_strategy_code) # My internal logic
    value_pred = my_value_predictor() # My internal logic

    # d. Execute One Round
    stats = run_mcts_round(
        exploration_constant=exploration_val,
        actions_to_expand=pruned_actions,
        value_prediction=value_pred
    )["simulation_stats"]

    # e. Analyze & Self-Correct
    if stats["improvement"] == 0:
        my_strategy_code = refine_strategy(my_strategy_code) # Modify for next loop

# 3. Final Result
best_move = get_best_move()["best_move"]
print(f"The best move is {best_move}")
```

## Available Tools

- `reinitialize_mcts(...)`: Resets the simulator with a new game.
- `run_mcts_round(exploration_constant: float, actions_to_expand: list | None, ...)`: **Executes exactly one round of MCTS** and returns simulation statistics.
- `get_possible_actions() -> dict`: Returns a list of all legal moves from the root.
- `get_best_move() -> dict`: Gets the best move found so far.
- `get_simulation_stats() -> dict`: Gets the current simulation state variables (e.g., `improvement`).
