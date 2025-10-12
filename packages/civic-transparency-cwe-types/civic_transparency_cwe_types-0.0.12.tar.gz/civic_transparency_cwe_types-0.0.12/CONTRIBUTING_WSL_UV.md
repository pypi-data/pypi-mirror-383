# Install uv on WSL

1. Fetch and run the uv install.
2. Add to path.
3. Reload shell config.
4. Verify.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc # Or ~/.zshrc

source ~/.bashrc # Or ~/.zshrc

uv -V
```
