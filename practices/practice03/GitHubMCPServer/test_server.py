#!/usr/bin/env python3
"""
Simple test script to verify GitHub MCP Server functionality.
This script tests the core components without external dependencies.
"""

import sys
import os
import ast



def test_syntax():
    """Test that all Python files have valid syntax."""
    print("🧪 Testing file syntax...")
    
    python_files = [
        "src/github_mcp_server/utils/errors.py",
        "src/github_mcp_server/utils/api_client.py", 
        "src/github_mcp_server/utils/formatters.py",
        "src/github_mcp_server/tools/search_issues.py",
        "src/github_mcp_server/tools/list_pull_requests.py",
        "src/github_mcp_server/tools/get_file_content.py",
        "src/github_mcp_server/tools/list_repository_contents.py",
        "src/github_mcp_server/server.py"
    ]
    
    success_count = 0
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            ast.parse(source_code)
            print(f"✅ {file_path}")
            success_count += 1
        except SyntaxError as e:
            print(f"❌ {file_path}: Syntax error - {e}")
        except Exception as e:
            print(f"❌ {file_path}: Error reading - {e}")
    
    print(f"\n📊 Syntax test: {success_count}/{len(python_files)} files have valid syntax")
    return success_count == len(python_files)



def test_structure():
    """Test that files have expected structure."""
    print("\n🧪 Testing file structure...")
    
    # Test server.py structure
    try:
        with open("src/github_mcp_server/server.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Prepare checks
        run_method_ok = ("mcp.run_stdio(" in content) or ("mcp.run()" in content) or ("mcp.run(" in content)
        checks = [
            ("FastMCP import", "from fastmcp import FastMCP" in content),
            ("mcp instance", "mcp = FastMCP" in content),
            ("tool imports", "from .tools" in content),
            ("main guard", "if __name__ == \"__main__\":" in content),
            ("run method", run_method_ok)
        ]
        
        success_count = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
                success_count += 1
            else:
                print(f"❌ {check_name}")
        
        print(f"📊 Server structure: {success_count}/{len(checks)} checks passed")
        return success_count == len(checks)
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False



def test_config_files():
    """Test that configuration files exist."""
    print("\n🧪 Testing configuration files...")
    
    config_files = [
        "pyproject.toml",
        "requirements.txt", 
        ".env.example",
        "README.md"
    ]
    
    success_count = 0
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path} (missing)")
    
    print(f"📊 Config files: {success_count}/{len(config_files)} files exist")
    return success_count == len(config_files)



def main():
    """Run all tests."""
    print("🚀 Starting GitHub MCP Server structural tests")
    print("=" * 60)
    
    tests = [
        test_syntax,
        test_structure,
        test_config_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    
    success_count = sum(results)
    total_tests = len(results)
    
    if success_count == total_tests:
        print(f"🎉 All {total_tests} structural tests passed!")
        print("\n✅ Server structure is correct")
        print("\nNext steps:")
        print("1. Install dependencies: pip install fastmcp httpx pydantic python-dotenv aiofiles")
        print("2. Set GITHUB_TOKEN environment variable")
        print("3. Run: python -m github_mcp_server.server")
        print("4. Or use: fastmcp dev src/github_mcp_server/server.py")
        return True
    else:
        print(f"⚠️  {success_count}/{total_tests} tests passed")
        print("\n❌ Some structural tests failed. Please check the errors above.")
        return False



if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)