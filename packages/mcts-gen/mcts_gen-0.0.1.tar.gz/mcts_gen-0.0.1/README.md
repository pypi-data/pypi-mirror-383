# MCTS-Gen: A Generic MCTS Framework

This project provides a generic Monte Carlo Tree Search (MCTS) framework. Its core concept is the replacement of the Genetic Programming (GP) engine from `chess-ant` with a modern AI agent. While inspired by AlphaZero, it uses a simpler, decoupled approach: the standard UCT algorithm is augmented by an external AI agent that provides policy and value predictions.

## Features

-   **AI-Augmented UCT**: Utilizes the standard UCT algorithm. The AI agent enhances the search by providing value predictions and, most importantly, by performing **Policy Pruning**—narrowing the search space by supplying a pre-filtered list of promising moves.
-   **AI Agent Integration**: Exposes the MCTS engine as a set of tools, enabling seamless integration with AI agents like the Gemini CLI.
-   **Extensible Game Logic**: Easily add support for new games by creating a new game state module.
-   **Optional Dependencies**: Install support for specific games on demand (e.g., `pip install mcts-gen[shogi]`).

## Quickstart

### 1. Installation

#### Standard Installation

The core package can be installed directly using pip:
```bash
pip install mcts-gen
```

#### Installation with Game-Specific Dependencies

To include support for specific games, you can install optional dependencies. For example, to install with support for Shogi:

```bash
pip install mcts-gen[shogi]
```
This will automatically install the `python-shogi` library alongside the core package.

### 2. Server Setup for Gemini CLI

To allow the Gemini agent to use the MCTS-Gen tools, you must register the server in your `settings.json` file. This allows the Gemini CLI to automatically manage the server process and provide the necessary context files.

Create or update your `settings.json` file with the following configuration:

```json
{
  "context": {
    "fileName": [
      "AGENTS.md",
      "GEMINI.md"
    ]
  },
  "mcpServers": {
    "mcts_gen_simulator_server": {
      "command": "python",
      "args": [
        "-m",
        "mcts_gen.fastmcp_server"
      ]
    }
  }
}
```

**Note**: The `context` block tells the Gemini CLI to load `AGENTS.md` (and `GEMINI.md` if it exists), which is crucial for the agent to understand how to use the tools.

You can place this `settings.json` file in one of two locations:

1.  **Project-Specific**: `./.gemini/settings.json` (inside this project directory)
2.  **Global**: `~/.gemini/settings.json` (in your home directory)

For an alternative setup method using the `fastmcp` command-line tool, please see the official guide:
- [Gemini CLI 🤝 FastMCP](https://gofastmcp.com/integrations/gemini-cli)

## For Maintainers: How to Release a New Version

The package publication process is automated using GitHub Actions.

#### a) Releasing to TestPyPI (for testing)

To release a version to the TestPyPI repository for verification, create and push a git tag with a `-test` suffix.

```bash
# Example for version 0.1.0
git tag v0.1.0-test1
git push origin v0.1.0-test1
```

#### b) Releasing to PyPI (Official)

To perform an official release, create and push a git tag that follows the semantic versioning format (e.g., `vX.Y.Z`).

```bash
# Example for version 0.1.0
git tag v0.1.0
git push origin v0.1.0
```

## Development

### Testing

To run all tests:
```bash
pytest
```

## License

This project is licensed under the GPL-3.0-or-later license.