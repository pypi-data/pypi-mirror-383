#!/bin/bash
# Quick test script to validate the production package

set -e

echo "🚀 Testing Production-Grade Databricks Claude Package"
echo "================================================="

# Test 1: Package structure
echo "📁 Checking package structure..."
required_files=(
    "pyproject.toml"
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "Dockerfile"
    ".pre-commit-config.yaml"
    ".github/workflows/ci.yml"
    "src/databricks_claude/__init__.py"
    "src/databricks_claude/__about__.py"
    "src/databricks_claude/core.py"
    "src/databricks_claude/cli.py"
    "src/databricks_claude/exceptions.py"
    "tests/conftest.py"
    "tests/test_core.py"
    "tests/test_cli.py"
    "tests/test_integration.py"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        exit 1
    fi
done

# Test 2: Python package structure
echo ""
echo "📦 Testing Python package installation..."
python -m pip install -e . > /dev/null 2>&1
echo "  ✅ Package installed successfully"

# Test 3: Import tests
echo ""
echo "🐍 Testing Python imports..."
python -c "import databricks_claude; print(f'  ✅ Package version: {databricks_claude.__version__}')"

python -c "from databricks_claude.core import DatabricksClaudeCore; print('  ✅ Core module imports')"

python -c "from databricks_claude.cli import cli; print('  ✅ CLI module imports')"

python -c "from databricks_claude.exceptions import DatabricksClaudeError; print('  ✅ Exceptions module imports')"

# Test 4: CLI functionality
echo ""
echo "🖥️  Testing CLI functionality..."
databricks-claude --version | grep -q "databricks-claude 1.0.0" && echo "  ✅ CLI version command works"

databricks-claude --help > /dev/null && echo "  ✅ CLI help command works"

# Test 5: Run unit tests
echo ""
echo "🧪 Running unit tests..."
python -m pytest tests/ -v --tb=short --disable-warnings

# Test 6: Code quality checks
echo ""
echo "🔍 Running code quality checks..."

echo "  📝 Checking format with black..."
python -m black --check src tests --quiet && echo "    ✅ Code formatting OK"

echo "  📊 Checking imports with isort..."
python -m isort --check-only src tests --quiet && echo "    ✅ Import sorting OK"

echo "  🔧 Checking lint with flake8..."
python -m flake8 src tests --quiet && echo "    ✅ Linting OK"

echo "  🔒 Checking security with bandit..."
python -m bandit -r src --quiet --format json > /dev/null && echo "    ✅ Security check OK"

# Test 7: Build package
echo ""
echo "📦 Testing package build..."
python -m build --quiet > /dev/null 2>&1 && echo "  ✅ Package builds successfully"

ls dist/*.whl > /dev/null 2>&1 && echo "  ✅ Wheel file created"
ls dist/*.tar.gz > /dev/null 2>&1 && echo "  ✅ Source distribution created"

# Test 8: Package validation
echo ""
echo "✅ Testing package validation..."
python -m twine check dist/* --quiet && echo "  ✅ Package passes twine validation"

echo ""
echo "🎉 All tests passed! Production package is ready!"
echo ""
echo "📊 Package Statistics:"
echo "  - Lines of Code: $(find src -name '*.py' -exec wc -l {} + | tail -n1 | awk '{print $1}')"
echo "  - Test Files: $(find tests -name 'test_*.py' | wc -l)"
echo "  - Dependencies: $(grep -c '^[a-zA-Z]' pyproject.toml | head -1)" 
echo "  - Package Size: $(du -sh dist/*.whl | cut -f1)"

echo ""
echo "🚀 Ready for deployment!"
echo "  - PyPI: twine upload dist/*"
echo "  - Docker: docker build -t databricks-claude ."
echo "  - CI/CD: Push to trigger GitHub Actions"

