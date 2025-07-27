#!/usr/bin/env python3
"""
Validation script to verify the POST-ONLY wrapper implementation
"""

import sys
import os
import importlib.util
from pathlib import Path


def validate_imports():
    """Validate that all modules can be imported"""
    print("🔍 Validating imports...")
    
    try:
        # Add the project root to Python path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # Test main package import
        import bfx_postonly
        print(f"✅ Main package imported successfully (version: {bfx_postonly.__version__})")
        
        # Test client import
        from bfx_postonly import PostOnlyClient
        print("✅ PostOnlyClient imported successfully")
        
        # Test decorators
        from bfx_postonly.decorators import post_only_enforcer, post_only_rest, post_only_websocket
        print("✅ Decorators imported successfully")
        
        # Test exceptions
        from bfx_postonly.exceptions import PostOnlyViolationError, InvalidOrderTypeError
        print("✅ Exceptions imported successfully")
        
        # Test utils
        from bfx_postonly.utils import is_limit_order, has_post_only_flag, combine_flags
        print("✅ Utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def validate_functionality():
    """Validate core functionality without API calls"""
    print("\n🧪 Validating functionality...")
    
    try:
        from bfx_postonly.utils import is_limit_order, has_post_only_flag, add_post_only_flag, combine_flags
        from bfx_postonly.decorators import _validate_and_modify_order_params
        from bfx_postonly.exceptions import PostOnlyViolationError, InvalidOrderTypeError
        
        # Test utility functions
        assert is_limit_order("EXCHANGE LIMIT") == True
        assert is_limit_order("MARKET") == False
        print("✅ is_limit_order working correctly")
        
        assert has_post_only_flag(4096) == True
        assert has_post_only_flag(0) == False
        print("✅ has_post_only_flag working correctly")
        
        assert add_post_only_flag() == 4096
        assert add_post_only_flag(64) == 4096 | 64
        print("✅ add_post_only_flag working correctly")
        
        flags = combine_flags("POST_ONLY", "HIDDEN")
        assert flags == 4096 | 64
        print("✅ combine_flags working correctly")
        
        # Test parameter validation
        valid_params = {
            'type': 'EXCHANGE LIMIT',
            'symbol': 'tBTCUSD',
            'amount': 0.001,
            'price': 30000.0
        }
        
        result = _validate_and_modify_order_params(**valid_params)
        assert has_post_only_flag(result['flags']) == True
        print("✅ Parameter validation working correctly")
        
        # Test error cases
        try:
            _validate_and_modify_order_params(type='MARKET')
            assert False, "Should have raised exception"
        except InvalidOrderTypeError:
            print("✅ Market order rejection working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def validate_client_initialization():
    """Validate client can be initialized without API credentials"""
    print("\n🏗️ Validating client initialization...")
    
    try:
        from unittest.mock import patch, Mock
        from bfx_postonly import PostOnlyClient
        
        # Mock the underlying BfxClient to avoid needing real credentials
        with patch('bfx_postonly.client.BfxClient') as mock_client:
            # Setup mock with proper structure
            mock_instance = Mock()
            
            # Create mock REST client with auth
            mock_auth = Mock()
            mock_auth.submit_order = Mock(return_value=Mock(status="SUCCESS"))
            mock_rest = Mock()
            mock_rest.auth = mock_auth
            mock_instance.rest = mock_rest
            
            # Create mock WebSocket client with inputs
            mock_inputs = Mock()
            mock_inputs.submit_order = Mock()
            mock_wss = Mock()
            mock_wss.inputs = mock_inputs
            mock_instance.wss = mock_wss
            
            mock_client.return_value = mock_instance
            
            # Initialize client
            client = PostOnlyClient(api_key="test", api_secret="test")
            
            # Test properties
            assert hasattr(client, 'rest')
            assert hasattr(client, 'wss')
            assert hasattr(client, 'submit_limit_order')
            assert hasattr(client, 'submit_limit_order_async')
            
            # Test client info
            info = client.get_client_info()
            assert info['post_only_enforced'] == True
            assert info['api_key_set'] == True
            
            print("✅ Client initialization working correctly")
            return True
            
    except Exception as e:
        print(f"❌ Client initialization test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


def validate_project_structure():
    """Validate project structure is correct"""
    print("\n📁 Validating project structure...")
    
    project_root = Path(__file__).parent.parent
    required_files = [
        "bfx_postonly/__init__.py",
        "bfx_postonly/client.py", 
        "bfx_postonly/decorators.py",
        "bfx_postonly/exceptions.py",
        "bfx_postonly/utils.py",
        "examples/basic_usage.py",
        "examples/advanced_usage.py",
        "tests/test_postonly.py",
        "README.md",
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print(f"✅ All required files present ({len(required_files)} files)")
        return True


def validate_examples():
    """Validate example files are syntactically correct"""
    print("\n📋 Validating examples...")
    
    project_root = Path(__file__).parent.parent
    example_files = [
        "examples/basic_usage.py",
        "examples/advanced_usage.py"
    ]
    
    for example_file in example_files:
        try:
            file_path = project_root / example_file
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Compile to check syntax
            compile(code, file_path, 'exec')
            print(f"✅ {example_file} syntax is valid")
            
        except SyntaxError as e:
            print(f"❌ Syntax error in {example_file}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error validating {example_file}: {e}")
            return False
    
    return True


def main():
    """Run all validation checks"""
    print("🚀 Validating Bitfinex API Python POST-ONLY Wrapper")
    print("=" * 60)
    
    checks = [
        ("Project Structure", validate_project_structure),
        ("Imports", validate_imports),
        ("Core Functionality", validate_functionality),
        ("Client Initialization", validate_client_initialization),
        ("Example Syntax", validate_examples),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                print(f"\n❌ {check_name} check failed")
        except Exception as e:
            print(f"\n❌ {check_name} check failed with error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validations passed! The wrapper is ready to use.")
        return 0
    else:
        print("⚠️  Some validations failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
