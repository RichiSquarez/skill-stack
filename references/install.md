# Install (only after explicit user OK)

## Skills
- skills.sh: `npx -y skills add <owner/repo@skill> -g -y`
- From GitHub manually (sparse, cheap):
  ```bash
  git clone --depth 1 --filter=blob:none --sparse https://github.com/<owner>/<repo> /tmp/sk && \
  git -C /tmp/sk sparse-checkout set <path/to/skill> && \
  cp -r /tmp/sk/<path/to/skill> ~/.agents/skills/ && rm -rf /tmp/sk
  ```
  Also link for Claude/Codex if needed: `ln -s ~/.agents/skills/<name> ~/.claude/skills/<name>`
- Then: `python3 <skill-stack>/scripts/build_index.py --force`

## MCP — Claude Code
- stdio: `claude mcp add <name> -- npx -y <package>`
- with env: `claude mcp add <name> -e KEY=value -- npx -y <package>`
- remote: `claude mcp add --transport http <name> <url>`

## MCP — Codex (`~/.codex/config.toml`)
```toml
[mcp_servers.<name>]
command = "npx"
args = ["-y", "<package>"]
# env = { KEY = "value" }
```
Or: `codex mcp add <name> -- npx -y <package>`

Never write API keys into files without asking; tell the user which keys are needed.
