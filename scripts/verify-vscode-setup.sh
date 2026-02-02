#!/bin/bash

# VS Code fyp_env Configuration Verification Script
# This script verifies that VS Code is properly configured to use fyp_env

echo "🔍 Verifying VS Code fyp_env Configuration..."
echo ""

# Check if .vscode directory exists
if [ -d ".vscode" ]; then
    echo "✅ .vscode directory exists"
else
    echo "❌ .vscode directory NOT found"
    exit 1
fi

# Check settings.json
if [ -f ".vscode/settings.json" ]; then
    echo "✅ .vscode/settings.json exists"

    # Check Python interpreter path
    if grep -q "fyp_env" ".vscode/settings.json"; then
        echo "✅ Python interpreter configured for fyp_env"
    else
        echo "⚠️  fyp_env not found in settings.json"
    fi

    # Check terminal auto-activation
    if grep -q "terminal.integrated.shellArgs" ".vscode/settings.json"; then
        echo "✅ Terminal auto-activation configured"
    else
        echo "⚠️  Terminal auto-activation not configured"
    fi
else
    echo "❌ .vscode/settings.json NOT found"
fi

# Check fyp_env exists
echo ""
echo "🔍 Checking fyp_env environment..."
if command -v mamba &> /dev/null; then
    echo "✅ Mamba installed"

    if mamba env list | grep -q "fyp_env"; then
        echo "✅ fyp_env environment exists"

        # Get fyp_env path
        FYP_ENV_PATH=$(mamba env list | grep fyp_env | awk '{print $NF}')
        echo "   Path: $FYP_ENV_PATH"

        # Check Python exists in fyp_env
        if [ -f "$FYP_ENV_PATH/bin/python" ]; then
            echo "✅ Python exists in fyp_env"
            PYTHON_VERSION=$("$FYP_ENV_PATH/bin/python" --version 2>&1)
            echo "   Version: $PYTHON_VERSION"
        else
            echo "❌ Python NOT found in fyp_env"
        fi
    else
        echo "❌ fyp_env environment NOT found"
        echo "   Create it with: mamba create -n fyp_env python=3.10"
    fi
else
    echo "❌ Mamba NOT installed"
fi

# Check if currently in fyp_env
echo ""
echo "🔍 Current environment status..."
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "   Active environment: $CONDA_DEFAULT_ENV"

    if [ "$CONDA_DEFAULT_ENV" = "fyp_env" ]; then
        echo "✅ Currently in fyp_env"
    else
        echo "⚠️  Not in fyp_env (this is OK outside VS Code terminals)"
    fi
else
    echo "⚠️  No conda environment active (this is OK outside VS Code)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "VS Code Configuration Status:"
echo "  • Settings: $([ -f .vscode/settings.json ] && echo '✅' || echo '❌')"
echo "  • Tasks: $([ -f .vscode/tasks.json ] && echo '✅' || echo '❌')"
echo "  • Launch configs: $([ -f .vscode/launch.json ] && echo '✅' || echo '❌')"
echo "  • Extensions: $([ -f .vscode/extensions.json ] && echo '✅' || echo '❌')"
echo ""
echo "Environment Status:"
echo "  • Mamba: $(command -v mamba &> /dev/null && echo '✅' || echo '❌')"
echo "  • fyp_env: $(mamba env list 2>/dev/null | grep -q fyp_env && echo '✅' || echo '❌')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "  1. Reload VS Code window: Ctrl+Shift+P → 'Developer: Reload Window'"
echo "  2. Open new terminal: Ctrl+\` (should show fyp_env)"
echo "  3. Install extensions: Ctrl+Shift+P → 'Extensions: Show Recommended'"
echo "  4. Start coding - fyp_env will be active automatically! 🎉"
echo ""
