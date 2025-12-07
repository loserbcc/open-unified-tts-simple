#!/bin/bash
# Install the MCP server using uv

set -e

cd "$(dirname "$0")"

echo "Installing unified-tts-simple MCP server..."
uv pip install -e .

echo ""
echo "Done! Add to Claude with:"
echo ""
echo "  claude mcp add unified-tts-simple uv run --directory $(pwd) python server.py"
echo ""
echo "Or manually add to ~/.claude/claude_desktop_config.json:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "unified-tts-simple": {
      "command": "uv",
      "args": ["run", "--directory", "PATH_TO_MCP_SERVER", "python", "server.py"],
      "env": {
        "TTS_API_URL": "http://localhost:8766",
        "TTS_OUTPUT_DIR": "~/tts-output"
      }
    }
  }
}
EOF
