#!/bin/bash

# Git Hooks for GitFlow Workflow
# This script sets up all necessary git hooks for the project

set -e

HOOKS_DIR=".githooks"

echo "🔧 Setting up GitFlow Git Hooks..."

# Check if fyp_env is activated
if [[ "$CONDA_DEFAULT_ENV" != "fyp_env" ]]; then
    echo "⚠️  Warning: fyp_env environment is not activated!"
    echo "   Please run: mamba activate fyp_env"
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Using fyp_env environment"

# Create .githooks directory if it doesn't exist
mkdir -p $HOOKS_DIR

# Configure git to use our custom hooks directory
git config core.hooksPath $HOOKS_DIR

echo "✅ Git hooks path configured to: $HOOKS_DIR"

# Create pre-commit hook
cat > $HOOKS_DIR/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 Running pre-commit checks..."

# Ensure fyp_env is activated
if [[ "$CONDA_DEFAULT_ENV" != "fyp_env" ]]; then
    echo "⚠️  fyp_env not activated. Attempting to activate..."
    # Try to activate fyp_env
    if command -v mamba &> /dev/null; then
        eval "$(conda shell.bash hook)"
        mamba activate fyp_env 2>/dev/null || {
            echo "❌ Failed to activate fyp_env. Please run: mamba activate fyp_env"
            exit 1
        }
    else
        echo "❌ Mamba not found. Please activate fyp_env manually."
        exit 1
    fi
fi

# Stash unstaged changes
git stash -q --keep-index

# Run Black
echo "  → Checking code formatting with Black..."
black --check . || {
    echo "❌ Black formatting check failed. Run: black ."
    git stash pop -q
    exit 1
}

# Run isort
echo "  → Checking import sorting with isort..."
isort --check-only . || {
    echo "❌ isort check failed. Run: isort ."
    git stash pop -q
    exit 1
}

# Run Flake8
echo "  → Running Flake8 linter..."
flake8 . || {
    echo "❌ Flake8 linting failed."
    git stash pop -q
    exit 1
}

# Run Bandit security check
echo "  → Running Bandit security scan..."
bandit -r . -ll || {
    echo "⚠️  Bandit found security issues (continuing...)"
}

# Pop stashed changes
git stash pop -q

echo "✅ All pre-commit checks passed!"
exit 0
EOF

# Create commit-msg hook for conventional commits
cat > $HOOKS_DIR/commit-msg << 'EOF'
#!/bin/bash

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Conventional commit pattern
pattern="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .{1,100}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Commit message must follow Conventional Commits:"
    echo "  <type>[optional scope]: <description>"
    echo ""
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo ""
    echo "Examples:"
    echo "  feat: add user authentication"
    echo "  fix(api): resolve caching issue"
    echo "  docs: update README with deployment guide"
    exit 1
fi

echo "✅ Commit message format is valid"
exit 0
EOF

# Create pre-push hook
cat > $HOOKS_DIR/pre-push << 'EOF'
#!/bin/bash

echo "🚀 Running pre-push checks..."

# Get current branch
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

# Prevent direct push to master or main
if [ "$current_branch" = "master" ] || [ "$current_branch" = "main" ]; then
    echo "❌ Direct push to $current_branch is not allowed!"
    echo "Please use GitFlow workflow:"
    echo "  1. Create a release branch: git flow release start x.y.z"
    echo "  2. Or use hotfix: git flow hotfix start x.y.z"
    exit 1
fi

# Prevent direct push to develop without tests passing
if [ "$current_branch" = "develop" ]; then
    echo "  → Running tests before pushing to develop..."
    if command -v pytest &> /dev/null; then
        pytest --maxfail=1 --disable-warnings -q || {
            echo "❌ Tests failed! Fix tests before pushing to develop."
            exit 1
        }
    else
        echo "⚠️  pytest not found, skipping tests"
    fi
fi

echo "✅ Pre-push checks passed!"
exit 0
EOF

# Create post-checkout hook
cat > $HOOKS_DIR/post-checkout << 'EOF'
#!/bin/bash

# Check if dependencies need to be updated
if [ -f requirements.txt ]; then
    # Compare requirements.txt hash
    if [ -f .requirements.hash ]; then
        current_hash=$(md5sum requirements.txt 2>/dev/null | awk '{print $1}' || echo "")
        old_hash=$(cat .requirements.hash 2>/dev/null || echo "")
        
        if [ "$current_hash" != "$old_hash" ] && [ -n "$current_hash" ]; then
            echo "📦 Dependencies have changed. Consider running:"
            echo "   pip install -r requirements.txt"
        fi
    fi
    
    # Save current hash
    md5sum requirements.txt 2>/dev/null | awk '{print $1}' > .requirements.hash || true
fi
EOF

# Create post-merge hook
cat > $HOOKS_DIR/post-merge << 'EOF'
#!/bin/bash

echo "🔄 Post-merge actions..."

# Check if dependencies changed
if [ -f requirements.txt ]; then
    echo "  → Checking for dependency updates..."
    if git diff --name-only HEAD@{1} HEAD | grep -q "requirements.txt"; then
        echo "⚠️  requirements.txt has changed!"
        echo "   Run: pip install -r requirements.txt"
    fi
fi

# Check if migrations changed
if git diff --name-only HEAD@{1} HEAD | grep -q "migrations"; then
    echo "⚠️  Database migrations have changed!"
    echo "   Run: python manage.py migrate"
fi
EOF

# Make all hooks executable
chmod +x $HOOKS_DIR/pre-commit
chmod +x $HOOKS_DIR/commit-msg
chmod +x $HOOKS_DIR/pre-push
chmod +x $HOOKS_DIR/post-checkout
chmod +x $HOOKS_DIR/post-merge

echo ""
echo "✅ GitFlow hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  ✓ pre-commit    - Code quality checks"
echo "  ✓ commit-msg    - Enforce conventional commits"
echo "  ✓ pre-push      - Protect master/develop branches"
echo "  ✓ post-checkout - Dependency update warnings"
echo "  ✓ post-merge    - Migration & dependency warnings"
echo ""
echo "🌊 GitFlow Quick Reference:"
echo "  Start feature:  git flow feature start <name>"
echo "  Finish feature: git flow feature finish <name>"
echo "  Start release:  git flow release start <version>"
echo "  Finish release: git flow release finish <version>"
echo "  Start hotfix:   git flow hotfix start <version>"
echo "  Finish hotfix:  git flow hotfix finish <version>"
echo ""
