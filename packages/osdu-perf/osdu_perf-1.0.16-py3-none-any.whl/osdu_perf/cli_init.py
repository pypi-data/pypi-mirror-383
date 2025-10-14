"""
CLI Initialization Functions for the OSDU Performance Testing Framework.

This module contains all the initialization, project creation, and file generation
functions used by the main CLI interface.
"""

import getpass
import os
import shutil
import json
import base64
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

# Version information
__version__ = "1.0.12"


def create_sample_jwt_token(
    issuer: str = "https://sample-issuer.com",
    audience: str = "sample-audience",
    subject: str = "sample-user@example.com",
    app_id: str = "sample-app-id",
    tenant_id: str = "sample-tenant-id",
    expiry_hours: int = 24,
    include_osdu_claims: bool = True
) -> str:
    """
    Create a sample JWT token for testing purposes.
    
    Note: This creates an UNSIGNED token for testing purposes only.
    DO NOT use this for actual authentication.
    
    Args:
        issuer: Token issuer (iss claim)
        audience: Token audience (aud claim)
        subject: Token subject (sub claim)
        app_id: Azure Application ID (appid claim)
        tenant_id: Azure Tenant ID (tid claim)
        expiry_hours: Token expiry time in hours from now
        include_osdu_claims: Whether to include OSDU-specific claims
        
    Returns:
        str: Sample JWT token (unsigned)
    """
    # Header for JWT (unsigned)
    header = {
        "alg": "none",  # No signature for sample token
        "typ": "JWT"
    }
    
    # Current time and expiry
    now = int(time.time())
    exp = now + (expiry_hours * 3600)
    
    # Payload with standard and Azure AD claims
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "appid": app_id,
        "tid": tenant_id,
        "iat": now,
        "exp": exp,
        "nbf": now,
        "ver": "2.0",
        "name": "Sample User",
        "preferred_username": subject,
        "email": subject,
        "roles": ["user"],
        "scp": "user.read openid profile"
    }
    
    # Add OSDU-specific claims if requested
    if include_osdu_claims:
        payload.update({
            "groups": [
                "users.datalake.viewers", 
                "users.datalake.editors",
                "users.datalake.admins"
            ],
            "entitlements": [
                {
                    "group": "data.default.viewers",
                    "classification": "restricted"
                },
                {
                    "group": "data.default.editors", 
                    "classification": "restricted"
                }
            ]
        })
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()
    
    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()
    
    # Create unsigned JWT (no signature part)
    token = f"{header_encoded}.{payload_encoded}."
    
    return token


def create_sample_jwt_tokens_file(output_path: str) -> None:
    """
    Create a sample JWT tokens file with various token examples.
    
    Args:
        output_path: Path where to create the tokens file
    """
    # Generate multiple sample tokens
    tokens = {
        "basic_token": create_sample_jwt_token(),
        "admin_token": create_sample_jwt_token(
            subject="admin@example.com",
            include_osdu_claims=True
        ),
        "viewer_token": create_sample_jwt_token(
            subject="viewer@example.com",
            include_osdu_claims=True
        ),
        "long_lived_token": create_sample_jwt_token(
            expiry_hours=168  # 7 days
        )
    }
    
    content = f'''# Sample JWT Tokens for OSDU Performance Testing
# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#
# WARNING: These are UNSIGNED tokens for testing purposes only!
# DO NOT use these for actual authentication in production!

import json

# Sample JWT tokens for different scenarios
SAMPLE_TOKENS = {{
'''
    
    for token_name, token_value in tokens.items():
        content += f'    "{token_name}": "{token_value}",\n'
    
    content += '''}

def get_sample_token(token_type: str = "basic_token") -> str:
    """
    Get a sample JWT token by type.
    
    Args:
        token_type: Type of token to retrieve
        
    Returns:
        str: Sample JWT token
    """
    return SAMPLE_TOKENS.get(token_type, SAMPLE_TOKENS["basic_token"])


def decode_token_payload(token: str) -> dict:
    """
    Decode and return the payload of a JWT token (for inspection).
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded payload
    """
    import base64
    import json
    
    try:
        # Split token and get payload
        parts = token.split('.')
        if len(parts) < 2:
            raise ValueError("Invalid token format")
            
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
            
        decoded_bytes = base64.urlsafe_b64decode(payload)
        return json.loads(decoded_bytes.decode())
        
    except Exception as e:
        return {"error": f"Failed to decode token: {e}"}


# Example usage:
if __name__ == "__main__":
    # Print sample token
    token = get_sample_token("basic_token")
    print("Sample JWT Token:")
    print(token)
    print("\\nDecoded Payload:")
    print(json.dumps(decode_token_payload(token), indent=2))
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created sample JWT tokens file at {output_path}")
    print("⚠️  WARNING: These are unsigned tokens for testing purposes only!")
    print("   Do not use in production environments.")


def create_auth_utils_file(output_path: str) -> None:
    """
    Create a utility file for authentication helpers.
    
    Args:
        output_path: Path where to create the auth utils file
    """
    content = '''"""
Authentication utilities for OSDU Performance Testing
"""

import base64
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def create_test_jwt_token(
    claims: Optional[Dict[str, Any]] = None,
    expiry_hours: int = 24
) -> str:
    """
    Create a test JWT token with custom claims.
    
    WARNING: This creates an UNSIGNED token for testing only!
    
    Args:
        claims: Custom claims to include in the token
        expiry_hours: Token expiry in hours
        
    Returns:
        str: Unsigned JWT token
    """
    if claims is None:
        claims = {}
    
    # Default header
    header = {"alg": "none", "typ": "JWT"}
    
    # Default payload with timing
    now = int(time.time())
    default_payload = {
        "iss": "test-issuer",
        "aud": "test-audience", 
        "sub": "test-user",
        "iat": now,
        "exp": now + (expiry_hours * 3600),
        "nbf": now
    }
    
    # Merge with custom claims
    payload = {**default_payload, **claims}
    
    # Encode parts
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()
    
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()
    
    return f"{header_b64}.{payload_b64}."


def extract_token_claims(token: str) -> Dict[str, Any]:
    """
    Extract and decode claims from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded claims
    """
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {"error": "Invalid token format"}
        
        # Decode payload
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
            
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded.decode())
        
    except Exception as e:
        return {"error": str(e)}


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if expired, False otherwise
    """
    claims = extract_token_claims(token)
    
    if "error" in claims:
        return True
        
    exp = claims.get("exp")
    if not exp:
        return True
        
    return int(time.time()) >= exp


def get_token_expiry_info(token: str) -> Dict[str, Any]:
    """
    Get expiry information for a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Expiry information
    """
    claims = extract_token_claims(token)
    
    if "error" in claims:
        return claims
    
    exp = claims.get("exp")
    if not exp:
        return {"error": "No expiry claim found"}
    
    exp_datetime = datetime.fromtimestamp(exp)
    now = datetime.now()
    
    return {
        "expires_at": exp_datetime.isoformat(),
        "expires_in_seconds": max(0, int((exp_datetime - now).total_seconds())),
        "is_expired": exp_datetime <= now,
        "time_until_expiry": str(max(timedelta(0), exp_datetime - now))
    }


# Common OSDU claims for testing
OSDU_TEST_CLAIMS = {
    "groups": [
        "users.datalake.viewers",
        "users.datalake.editors", 
        "users.datalake.admins"
    ],
    "entitlements": [
        {
            "group": "data.default.viewers",
            "classification": "restricted"
        },
        {
            "group": "data.default.editors",
            "classification": "restricted"
        }
    ]
}


def create_osdu_test_token(
    partition: str = "opendes",
    user_email: str = "test@example.com",
    app_id: str = "test-app-id",
    tenant_id: str = "test-tenant-id"
) -> str:
    """
    Create a test token with OSDU-specific claims.
    
    Args:
        partition: OSDU data partition
        user_email: User email
        app_id: Application ID
        tenant_id: Tenant ID
        
    Returns:
        str: Test JWT token with OSDU claims
    """
    claims = {
        "sub": user_email,
        "email": user_email,
        "appid": app_id,
        "tid": tenant_id,
        "preferred_username": user_email,
        "name": "Test User",
        **OSDU_TEST_CLAIMS
    }
    
    return create_test_jwt_token(claims)
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created authentication utilities at {output_path}")


def _backup_existing_files(project_name: str, service_name: str) -> None:
    """
    Create backup of existing project files.
    
    Args:
        project_name: Name of the project directory
        service_name: Name of the service
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{project_name}_backup_{timestamp}"
    
    try:
        shutil.copytree(project_name, backup_dir)
        print(f"✅ Backup created at: {backup_dir}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        raise


def _should_create_file(filepath: str, choice: str) -> bool:
    """
    Determine if a file should be created based on user choice and file existence.
    
    Args:
        filepath: Path to the file
        choice: User choice ('o', 's', 'b')
        
    Returns:
        True if file should be created, False otherwise
    """
    if choice == 'o':  # Overwrite
        return True
    elif choice == 's':  # Skip existing
        return not os.path.exists(filepath)
    elif choice == 'b':  # Backup (already done, now create new)
        return True
    return False


def init_project(service_name: str, force: bool = False) -> None:
    """
    Initialize a new performance testing project for a specific service.
    
    Args:
        service_name: Name of the service to test (e.g., 'storage', 'search', 'wellbore')
        force: If True, overwrite existing files without prompting
    """
    project_name = f"perf_tests"
    test_filename = f"perf_{service_name}_test.py"
    
    print(f"🚀 Initializing OSDU Performance Testing project for: {service_name}")
    
    # Check if project already exists
    if os.path.exists(project_name):
        print(f"⚠️  Directory '{project_name}' already exists!")
        
        # Check if specific service test file exists
        test_file_path = os.path.join(project_name, test_filename)
        if os.path.exists(test_file_path):
            print(f"⚠️  Test file '{test_filename}' already exists!")
            
            if force:
                choice = 'o'  # Force overwrite
                print("🔄 Force mode: Overwriting existing files...")
            else:
                # Ask user what to do
                while True:
                    choice = input(f"Do you want to:\n"
                                 f"  [o] Overwrite existing files\n"
                                 f"  [s] Skip existing files and create missing ones\n" 
                                 f"  [b] Backup existing files and create new ones\n"
                                 f"  [c] Cancel initialization\n"
                                 f"Enter your choice [o/s/b/c]: ").lower().strip()
                    
                    if choice in ['o', 'overwrite']:
                        print("🔄 Overwriting existing files...")
                        break
                    elif choice in ['s', 'skip']:
                        print("⏭️  Skipping existing files, creating missing ones...")
                        break
                    elif choice in ['b', 'backup']:
                        print("💾 Creating backup of existing files...")
                        _backup_existing_files(project_name, service_name)
                        break
                    elif choice in ['c', 'cancel']:
                        print("❌ Initialization cancelled.")
                        return
                    else:
                        print("❌ Invalid choice. Please enter 'o', 's', 'b', or 'c'.")
        else:
            # Directory exists but no service test file
            choice = 's' if not force else 'o'  # Skip mode or force
            print(f"📁 Directory exists but '{test_filename}' not found. Creating missing files...")
    else:
        choice = 'o'  # New project
    
    # Create project directory
    os.makedirs(project_name, exist_ok=True)
    
    # Create sample test file
    test_file_path = os.path.join(project_name, test_filename)
    if _should_create_file(test_file_path, choice):
        create_service_test_file(service_name, test_file_path)
    else:
        print(f"⏭️  Skipped existing: {test_filename}")

    # Create requirements.txt
    requirements_path = os.path.join(project_name, "requirements.txt")
    if _should_create_file(requirements_path, choice):
        create_requirements_file(requirements_path)
    else:
        print(f"⏭️  Skipped existing: requirements.txt")

    # Create comprehensive README.md
    readme_path = os.path.join(project_name, "README.md")
    if _should_create_file(readme_path, choice):
        create_project_readme(service_name, readme_path)
    else:
        print(f"⏭️  Skipped existing: README.md")
    
    # Create locustfile.py for direct Locust testing
    locustfile_path = os.path.join(project_name, "locustfile.py")
    if _should_create_file(locustfile_path, choice):
        create_locustfile_template(locustfile_path, [service_name])
    else:
        print(f"⏭️  Skipped existing: locustfile.py")
    
    # Create config.yaml for project configuration
    config_path = os.path.join(project_name, "config.yaml")
    if _should_create_file(config_path, choice):
        create_project_config(config_path, service_name)
    else:
        print(f"⏭️  Skipped existing: config.yaml")
    
    print(f"\n✅ Project {'updated' if choice == 's' else 'initialized'} successfully in {project_name}/")
    if choice != 's':
        print(f"✅ Created test file: {test_filename}")
    print(f"\n📝 Next steps:")
    print(f"   1. cd {project_name}")
    print("   2. pip install -r requirements.txt")
    print(f"   3. Edit config.yaml to set your OSDU environment details (host, partition, app_id, token)")
    print(f"   4. Edit {test_filename} to implement your test scenarios")
    print(f"   5. Run local tests: osdu-perf run local --config config.yaml")
    print(f"   6. Run Azure Load Tests: osdu-perf run azure_load_test --config config.yaml --subscription-id <sub-id> --resource-group <rg> --location <location>")
    print(f"   7. Optional: Override config values with CLI arguments (e.g., --host, --partition, --token)")


def create_project_config(output_path: str, service_name: str = None) -> None:
    """
    Create a config.yaml file for the performance testing project.
    
    Args:
        output_path: Path where to create the config.yaml file
        service_name: Name of the service being tested (used for test_run_id_prefix)
    """
    # Get current username from environment
    username = getpass.getuser()
    
    # Generate test_run_id_prefix based on username and service name
    if service_name:
        test_run_id_prefix = f"{username}_{service_name}_test"
    else:
        test_run_id_prefix = f"{username}_osdu_test"
    
    config_content = f"""# OSDU Performance Testing Configuration
# This file contains configuration settings for the OSDU performance testing framework

# OSDU Environment Configuration
osdu_environment:
  # OSDU instance details (required for run local command)
  host: "https://your-osdu-host.com"
  partition: "your-partition-id"
  app_id: "your-azure-app-id"
  
  # Authentication (optional - uses automatic token generation if not provided)
  auth:
    # Manual token override (optional)
    token: ""

# Metrics Collection Configuration  
metrics_collector:
  # Kusto (Azure Data Explorer) Configuration
  kusto:
    cluster: ""
    database: ""
    ingest_uri: ""

# Test Configuration (Optional)
test_settings:
  default_wait_time: 
    min: 1
    max: 3
  default_users: 10
  default_spawn_rate: 2
  default_run_time: "60s"
  test_run_id_prefix: "{test_run_id_prefix}"
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Created config.yaml at {output_path}")
    print(f"   📋 Generated test_run_id_prefix: {test_run_id_prefix}")


def create_service_test_file(service_name: str, output_path: str) -> None:
    """
    Create a service-specific test file following the perf_*_test.py pattern.
    
    Args:
        service_name: Name of the service
        output_path: Path where to create the test file
    """
    try:
        # Try to use the templates module
        from .templates.service_test_template import get_service_test_template
        formatted_template = get_service_test_template(service_name)
    except ImportError:
        # Fallback to embedded template if external file is not found
        service_name_clean = service_name.title()
        service_name_lower = service_name.lower()
        
        formatted_template = f'''import os
"""
Performance tests for {service_name_clean} Service
Generated by OSDU Performance Testing Framework
"""

from osdu_perf.core.base_service import BaseService


class {service_name_clean}PerformanceTest(BaseService):
    """
    Performance test class for {service_name_clean} Service
    
    This class will be automatically discovered and executed by the framework.
    """
    
    def __init__(self, client=None):
        super().__init__(client)
        self.name = "{service_name_lower}"
    
    def execute(self, headers=None, partition=None, base_url=None):
        """
        Execute {service_name_lower} performance tests
        
        Args:
            headers: HTTP headers including authentication
            partition: Data partition ID  
            base_url: Base URL for the service
        """
        print(f"🔥 Executing {{self.name}} performance tests...")
        
        # Example 1: Health check endpoint
        try:
            self._test_health_check(headers, base_url)
        except Exception as e:
            print(f"❌ Health check failed: {{e}}")
        
        # Example 2: Service-specific API calls
        try:
            self._test_service_apis(headers, partition, base_url)
        except Exception as e:
            print(f"❌ Service API tests failed: {{e}}")
        
        print(f"✅ Completed {{self.name}} performance tests")
    
    def provide_explicit_token(self) -> str:
        """
        Provide an explicit token for service execution.
        
        Returns the bearer token from environment variable set by localdev.py
        
        Returns:
            str: Authentication token for API requests
        """
        token = os.environ.get('ADME_BEARER_TOKEN', '')
        return token
  
    
    def prehook(self, headers=None, partition=None, base_url=None):
        """
        Pre-hook tasks before service execution.
        
        Use this method to set up test data, configurations, or prerequisites.
        
        Args:
            headers: HTTP headers including authentication
            partition: Data partition ID  
            base_url: Base URL for the service
        """
        print(f"🔧 Setting up prerequisites for {{self.name}} tests...")
        # TODO: Implement setup logic (e.g., create test data, configure environment)
        # Example: Create test records, validate partition access, etc.
        pass
    
    def posthook(self, headers=None, partition=None, base_url=None):
        """
        Post-hook tasks after service execution.
        
        Use this method for cleanup, reporting, or post-test validations.
        
        Args:
            headers: HTTP headers including authentication
            partition: Data partition ID  
            base_url: Base URL for the service
        """
        print(f"🧹 Cleaning up after {{self.name}} tests...")
        # TODO: Implement cleanup logic (e.g., delete test data, reset state)
        # Example: Remove test records, generate reports, validate cleanup
        pass
    
    def _test_health_check(self, headers, base_url):
        """Test health check endpoint"""
        try:
            response = self.client.get(
                f"{{base_url}}/api/{service_name_lower}/v1/health",
                headers=headers,
                name="{service_name_lower}_health_check"
            )
            print(f"Health check status: {{response.status_code}}")
        except Exception as e:
            print(f"Health check failed: {{e}}")
    
    def _test_service_apis(self, headers, partition, base_url):
        """
        Implement your service-specific test scenarios here
        
        Examples:
        - GET /api/{service_name_lower}/v1/records
        - POST /api/{service_name_lower}/v1/records
        - PUT /api/{service_name_lower}/v1/records/{{id}}
        - DELETE /api/{service_name_lower}/v1/records/{{id}}
        """
        
        # TODO: Replace with actual {service_name_lower} API endpoints
        
        # Example GET request
        try:
            response = self.client.get(
                f"{{base_url}}/api/{service_name_lower}/v1/info",
                headers=headers,
                name="{service_name_lower}_get_info"
            )
            print(f"Get info status: {{response.status_code}}")
        except Exception as e:
            print(f"Get info failed: {{e}}")


# Additional test methods can be added here
# Each method should follow the pattern: def test_scenario_name(self, headers, partition, base_url):
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_template)

    print(f"✅ Created {service_name} test file at {output_path}")


def create_requirements_file(output_path: str) -> None:
    """
    Create a requirements.txt file with osdu_perf and its dependencies.
    
    Args:
        output_path: Path where to create the requirements.txt file
    """
    requirements_content = f"""# Performance Testing Requirements
# Install with: pip install -r requirements.txt

# OSDU Performance Testing Framework
osdu_perf=={__version__}

# Additional dependencies (if needed)
# locust>=2.0.0  # Already included with osdu_perf
# azure-identity>=1.12.0  # Already included with osdu_perf
# requests>=2.28.0  # Already included with osdu_perf
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print(f"✅ Created requirements.txt at {output_path}")


def create_project_readme(service_name: str, output_path: str) -> None:
    """
    Create a comprehensive README for the performance testing project.
    
    Args:
        service_name: Name of the service being tested
        output_path: Path where to create the README
    """
    readme_content = f'''# {service_name.title()} Service Performance Tests

This project contains performance tests for the OSDU {service_name.title()} Service using the OSDU Performance Testing Framework.

## 📁 Project Structure

```
perf_tests/
├── config.yaml               # Framework configuration (metrics, test settings)
├── locustfile.py              # Main Locust configuration
├── perf_{service_name}_test.py        # {service_name.title()} service tests
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Framework Settings
Edit `config.yaml` and update:
- Kusto metrics collection settings
- Test defaults (users, spawn rate, wait time)

### 3. Configure Your Test Environment
Edit `perf_{service_name}_test.py` and update:
- API endpoints for {service_name} service
- Test data and scenarios
- Authentication requirements

### 3. Run Performance Tests
```bash
# Basic run with 10 users
locust -f locustfile.py --host https://your-api-host.com --partition your-partition --appid your-app-id

# Run with specific user count and spawn rate
locust -f locustfile.py --host https://your-api-host.com --partition your-partition --appid your-app-id -u 50 -r 5

# Run headless mode for CI/CD
locust -f locustfile.py --host https://your-api-host.com --partition your-partition --appid your-app-id --headless -u 10 -r 2 -t 60s
```

## 📝 Writing Performance Tests

### Test File Structure
Your test file `perf_{service_name}_test.py` follows this pattern:

```python
from osdu_perf.core.base_service import BaseService

class {service_name.title()}PerformanceTest(BaseService):
    def __init__(self, client=None):
        super().__init__(client)
        self.name = "{service_name}"
    
    def execute(self, headers=None, partition=None, base_url=None):
        # Your test scenarios go here
        self._test_health_check(headers, base_url)
        self._test_your_scenario(headers, partition, base_url)
```

### Key Points:
1. **Class Name**: Must end with `PerformanceTest` and inherit from `BaseService`
2. **File Name**: Must follow `perf_*_test.py` naming pattern for auto-discovery
3. **execute() Method**: Entry point for all your test scenarios
4. **HTTP Client**: Use `self.client` for making requests (pre-configured with Locust)

### Adding Test Scenarios

Create methods for each test scenario:

```python
def _test_create_record(self, headers, partition, base_url):
    \"\"\"Test record creation\"\"\"
    test_data = {{
        "kind": f"osdu:wks:{{partition}}:{service_name}:1.0.0",
        "data": {{"test": "data"}}
    }}
    
    response = self.client.post(
        f"{{base_url}}/api/{service_name}/v1/records",
        json=test_data,
        headers=headers,
        name="{service_name}_create_record"  # This appears in Locust UI
    )
    
    # Add assertions or validations
    assert response.status_code == 201, f"Expected 201, got {{response.status_code}}"
```

### HTTP Request Examples

```python
# GET request
response = self.client.get(
    f"{{base_url}}/api/{service_name}/v1/records/{{record_id}}",
    headers=headers,
    name="{service_name}_get_record"
)

# POST request with JSON
response = self.client.post(
    f"{{base_url}}/api/{service_name}/v1/records",
    json=data,
    headers=headers,
    name="{service_name}_create"
)

# PUT request
response = self.client.put(
    f"{{base_url}}/api/{service_name}/v1/records/{{record_id}}",
    json=updated_data,
    headers=headers,
    name="{service_name}_update"
)

# DELETE request
response = self.client.delete(
    f"{{base_url}}/api/{service_name}/v1/records/{{record_id}}",
    headers=headers,
    name="{service_name}_delete"
)
```

## 🔧 Configuration

### Framework Configuration (config.yaml)
The `config.yaml` file contains framework-wide settings:

```yaml
# Metrics Collection Configuration
metrics_collector:
  kusto:
    cluster: "https://your-kusto.eastus.kusto.windows.net"
    database: "your-database"
    ingest_uri: "https://ingest-your-kusto.eastus.kusto.windows.net"

# Test Configuration
test_settings:
  default_wait_time: 
    min: 1
    max: 3
  default_users: 10
  default_spawn_rate: 2
  default_run_time: "60s"
```

### Required CLI Arguments
- `--host`: Base URL of your OSDU instance
- `--partition`: Data partition ID
- `--appid`: Azure AD Application ID

### Optional Arguments
- `-u, --users`: Number of concurrent users (default: 1)
- `-r, --spawn-rate`: User spawn rate per second (default: 1)
- `-t, --run-time`: Test duration (e.g., 60s, 5m, 1h)
- `--headless`: Run without web UI (for CI/CD)

### Authentication
The framework automatically handles Azure authentication using:
- Azure CLI credentials (for local development)
- Managed Identity (for cloud environments)
- Service Principal (with environment variables)

## 📊 Monitoring and Results

### Locust Web UI
- Open http://localhost:8089 after starting Locust
- Monitor real-time performance metrics
- View request statistics and response times
- Download results as CSV

### Key Metrics to Monitor
- **Requests per second (RPS)**
- **Average response time**  
- **95th percentile response time**
- **Error rate**
- **Failure count by endpoint**

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Solution: Ensure Azure CLI is logged in or proper credentials are configured
   ```

2. **Import Errors**
   ```
   Solution: Run `pip install -r requirements.txt`
   ```

3. **Service Discovery Issues**
   ```
   Solution: Ensure test file follows perf_*_test.py naming pattern
   ```

4. **SSL/TLS Errors**
   ```
   Solution: Add --skip-tls-verify flag if using self-signed certificates
   ```

## 📚 Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [OSDU Performance Framework GitHub](https://github.com/janraj/osdu-perf)
- [Azure Authentication Guide](https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate)

## 🤝 Contributing

1. Follow the existing code patterns
2. Add comprehensive test scenarios
3. Update this README with new features
4. Test thoroughly before submitting changes

---

**Generated by OSDU Performance Testing Framework v{__version__}**
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ Created comprehensive README at {output_path}")


def create_locustfile_template(output_path: str, service_names: Optional[List[str]] = None) -> None:
    """
    Create a locustfile.py template with the framework.
    
    Args:
        output_path: Path where to create the locustfile.py
        service_names: Optional list of service names to include in template
    """
    from .core.local_test_runner import LocalTestRunner
    
    # Use the LocalTestRunner to create the template
    runner = LocalTestRunner()
    runner.create_locustfile_template(output_path, service_names)


def create_service_template(service_name: str, output_dir: str) -> None:
    """
    Create a service template file (legacy - kept for backward compatibility).
    
    Args:
        service_name: Name of the service
        output_dir: Directory where to create the service file
    """
    template = f'''"""
{service_name} Service for Performance Testing
"""

from osdu_perf.core.base_service import BaseService


class {service_name.capitalize()}Service(BaseService):
    """
    Performance test service for {service_name}
    """
    
    def __init__(self, client=None):
        super().__init__(client)
        self.name = "{service_name}"
    
    def execute(self, headers=None, partition=None, base_url=None):
        """
        Execute {service_name} service tests
        
        Args:
            headers: HTTP headers including authentication
            partition: Data partition ID
            base_url: Base URL for the service
        """
        # TODO: Implement your service-specific test logic here
        
        # Example API call:
        # response = self.client.get(
        #     f"{{base_url}}/api/{service_name}/health",
        #     headers=headers,
        #     name="{service_name}_health_check"
        # )
        
        print(f"Executing {service_name} service tests...")
        pass
'''
    
    os.makedirs(output_dir, exist_ok=True)
    service_file = os.path.join(output_dir, f"{service_name}_service.py")
    
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"✅ Created {service_name} service template at {service_file}")


def create_localdev_file(output_path: str) -> None:
    """
    Create a localdev.py file for running Locust tests locally with ADME authentication.
    
    Args:
        output_path: Path where to create the localdev.py file
    """
    # Get the template from the separate file
    template_path = Path(__file__).parent / 'localdev_template.py'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            localdev_content = template_file.read()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(localdev_content)
        
        print(f"✅ Created localdev.py at {output_path}")
        
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        print("Falling back to embedded template...")
        
        # Fallback to embedded template if separate file is missing
        localdev_content = '''#!/usr/bin/env python3
"""
Local Development CLI for OSDU Performance Testing Framework.
Runs Locust tests locally with ADME bearer token authentication.

Usage:
    python localdev.py --token "your_token" --partition "mypartition" --host "https://example.com"
"""

import argparse
import sys
import os
import subprocess
import glob

'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(localdev_content)
        
        print(f"✅ Created localdev.py at {output_path} (using fallback template)")


def create_azureloadtest_file(output_path: str, service_name: str = None) -> None:
    """
    Create an azureloadtest.py file for running Azure Load Testing with automatic file upload.
    
    Args:
        output_path: Path where to create the azureloadtest.py file
        service_name: Name of the service (used for default load test naming)
    """
    azureloadtest_content = '''#!/usr/bin/env python3
"""
Azure Load Testing CLI for OSDU Performance Testing Framework.
Creates and executes Azure Load Tests with automatic test file upload.

Prerequisites:
    pip install azure-cli azure-identity azure-mgmt-loadtesting azure-mgmt-resource

Usage:
    python azureloadtest.py --subscription-id "your_subscription" --resource-group "your_rg" --location "eastus" --token "your_token" --partition "mypartition"
"""

import argparse
import sys
import os
from datetime import datetime

try:
    from osdu_perf.azure_loadtest_template import AzureLoadTestManager
except ImportError:
    print("❌ OSDU Performance Testing Framework not found.")
    print("Install with: pip install osdu_perf")
    sys.exit(1)


def validate_inputs(args) -> bool:
    \"\"\"Validate required inputs for Azure Load Testing.\"\"\"
    errors = []
    
    # Azure-specific validations
    if not args.subscription_id or not args.subscription_id.strip():
        errors.append("Azure subscription ID is required")
    
    if not args.resource_group or not args.resource_group.strip():
        errors.append("Resource group is required")
    
    if not args.location or not args.location.strip():
        errors.append("Azure location is required")
    
    # ADME-specific validations
    if not args.token or not args.token.strip():
        errors.append("Bearer token is required")
    
    if not args.partition or not args.partition.strip():
        errors.append("Partition is required")
    
    if errors:
        print("❌ Validation errors:")
        for error in errors:
            print(f"   • {error}")
        return False
    
    return True


'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(azureloadtest_content)
    
    print(f"✅ Created azureloadtest.py at {output_path}")