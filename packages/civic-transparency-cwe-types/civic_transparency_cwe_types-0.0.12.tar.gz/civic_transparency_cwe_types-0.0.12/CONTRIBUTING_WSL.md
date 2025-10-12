# GitHub Access from VS Code + WSL (Contributor Guide)

This guide explains how to **set up GitHub authentication inside WSL** so you can clone, commit, and push directly from VS Code connected to WSL.
You **do not need your GitHub password** - you'll use SSH keys instead.

---

## 1. Check if Git works in WSL
In your WSL terminal:

```bash
git --version
git config --list
```

If those work, you're good to continue.
If not, install Git on WSL and configure with your user.name and user.email.

---

## 2. Generate a new SSH key (inside WSL)
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

- Press **Enter** for defaults.
- Optionally add a passphrase (recommended for personal machines).
- This creates:
  - `~/.ssh/id_ed25519` (private key)
  - `~/.ssh/id_ed25519.pub` (public key)

---

## 3. Add the key to your SSH agent
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

## 4. Add the key to your GitHub account
Copy the public key and paste it into
**GitHub / Settings / SSH and GPG keys / New SSH key**.

```bash
cat ~/.ssh/id_ed25519.pub
```

Name it something like **WSL-Ubuntu**.

---

## 5. Test your connection
```bash
ssh -T git@github.com
```

Expected message:
```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```
That's good - it means you're connected.

---

## 6. Set your Git identity (one time)
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

---

## 7. Verify your remote
In your repo folder:
```bash
git remote -v
```

If it shows `https://github.com/...`, switch to SSH:
```bash
git remote set-url origin git@github.com:<org>/<repo>.git
```

---

## 8. Add, commit, and push normally
```bash
git add .
git commit -m "Describe your changes"
git push -u origin main
```

For new branches:
```bash
git switch -c feat/some-change
git push -u origin feat/some-change
```

---

## 9. (Optional) Keep SSH agent alive between sessions
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
if ! pgrep -u "$USER" ssh-agent >/dev/null; then
  eval "$(ssh-agent -s)"
fi
ssh-add -l >/dev/null 2>&1 || ssh-add ~/.ssh/id_ed25519
```

---

## 10. Open in VS Code (connected to WSL)

In your WSL Terminal, cd to the repo folder, and open the folder with VS Code.
For example:

```bash
cd ~/projects/ct/civic-transparency-py-cwe-types
code .
```
- Bottom-left should say **WSL: Ubuntu**.
- You can now use the **Source Control** panel to commit/push directly.

---

## 11. Troubleshooting

| Symptom | Fix |
|----------|-----|
| “Permission denied (publickey)” | Check `ssh-add -l` shows your key; if not, run `ssh-add ~/.ssh/id_ed25519`. |
| “Too open permissions” | Run `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_ed25519 && chmod 644 ~/.ssh/id_ed25519.pub`. |
| VS Code keeps asking for login | Ensure your remote uses `git@github.com:` not HTTPS. |
| SSH key reused from Windows | Copy `C:\Users\<You>\.ssh\id_ed25519*` into `~/.ssh/` and `chmod` as above. |

---

### Congratulations
From now on, commits and pushes in VS Code (WSL) will just work, with no GitHub password prompts, no extra setup.
