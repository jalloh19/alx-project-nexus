# VS Code Configuration

This directory contains VS Code workspace settings for automatic `fyp_env` activation and Python development.

## Auto-activation Features

### ✅ Automatic Environment Activation
- **fyp_env** is automatically activated in every new integrated terminal
- No need to run `mamba activate fyp_env` manually
- Python interpreter is pre-configured to use fyp_env

### ✅ Python Development
- **Default Interpreter**: `/home/jalloh/miniconda3/envs/fyp_env/bin/python`
- **Linting**: Flake8, Pylint, Bandit, mypy enabled
- **Formatting**: Black with 100-character line length
- **Import Sorting**: isort with Black profile
- **Format on Save**: Enabled

### ✅ Testing
- **Framework**: pytest
- **Coverage**: Enabled with HTML reports
- **Test Discovery**: Automatic in `tests/` directory

### ✅ Quick Tasks
Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type "Tasks: Run Task":
- Django: Run Server
- Django: Migrate
- Django: Make Migrations
- Django: Create Superuser
- Tests: Run All
- Tests: Run with Coverage
- Code Quality: Format All
- Docker: Up/Down/Logs
- Git: Setup Hooks

### ✅ Debug Configurations
Press `F5` or use Debug panel:
- **Python: Django** - Run Django development server
- **Python: Pytest** - Run tests with debugger
- **Python: Django Shell** - Interactive Django shell
- **Python: Current File** - Debug current Python file

## Files

- **settings.json** - Workspace settings (Python interpreter, linting, formatting)
- **extensions.json** - Recommended VS Code extensions
- **launch.json** - Debug configurations
- **tasks.json** - Quick tasks for common operations

## Recommended Extensions

The workspace will prompt you to install recommended extensions:
- **Python** - Python language support
- **Pylance** - Fast Python language server
- **Black Formatter** - Code formatting
- **Docker** - Docker container support
- **Kubernetes** - K8s manifest support
- **Terraform** - Infrastructure as Code
- **GitLens** - Enhanced Git capabilities

## Verifying Setup

### Check Python Interpreter
1. Open any `.py` file
2. Look at bottom-left status bar
3. Should show: `Python 3.10.x ('fyp_env': conda)`

### Check Terminal Auto-activation
1. Open new terminal: `Ctrl+` ` (backtick)
2. Should automatically show: `(fyp_env) user@host:~/path$`
3. Verify: `echo $CONDA_DEFAULT_ENV` → Should output `fyp_env`

### Check Linting
1. Write some intentionally bad Python code
2. Should see red squiggles and problems in Problems panel

## Troubleshooting

### Terminal doesn't activate fyp_env
```bash
# Reload VS Code window
Ctrl+Shift+P → "Developer: Reload Window"
```

### Python interpreter not found
```bash
# Update settings.json with correct path
# Check fyp_env location: mamba env list
```

### Linters not working
```bash
# Ensure fyp_env is activated
mamba activate fyp_env

# Install linting tools
pip install -r requirements-dev.txt
```

## Manual Override (if needed)

If auto-activation doesn't work, you can still manually activate:
```bash
mamba activate fyp_env
```

But with these settings, **it should happen automatically!** 🎉
