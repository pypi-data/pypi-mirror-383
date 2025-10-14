"""
Azure Load Test SDK Manager

A comprehensive manager for Azure Load Testing using the official Python SDK.
Provides methods for creating resources, tests, uploading files, and running tests.

Author: OSDU Performance Testing Team
Date: October 2025
"""

import logging
import time
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# Azure SDK imports
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.loadtesting import LoadTestMgmtClient
from azure.developer.loadtesting import LoadTestAdministrationClient, LoadTestRunClient



class AzureLoadTestSDKManager:
    """
    Azure Load Test Manager using official Python SDK.
    
    Provides comprehensive Azure Load Testing management including:
    - Resource creation and management
    - Test creation and configuration
    - File upload and management
    - Test execution and monitoring
    """
    
    def __init__(self, 
                 subscription_id: str,
                 resource_group_name: str,
                 load_test_name: str,
                 location: str = "eastus"):
        """
        Initialize the Azure Load Test SDK Manager.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Resource group name
            load_test_name: Name for the load test resource
            location: Azure region (default: "eastus")
        """
        # Store configuration
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.load_test_name = load_test_name
        self.location = location
        
        # Initialize logger
        self._setup_logging()
        
        # Initialize Azure credential
        self._credential = AzureCliCredential()
        
        # Initialize Azure SDK clients
        self._init_clients()
        
        # Log initialization
        self.logger.info(f"Azure Load Test SDK Manager initialized")
        self.logger.info(f"Subscription: {self.subscription_id}")
        self.logger.info(f"Resource Group: {self.resource_group_name}")
        self.logger.info(f"Load Test Name: {self.load_test_name}")
        self.logger.info(f"Location: {self.location}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _init_clients(self) -> None:
        """Initialize Azure SDK clients."""
        try:
            # Resource Management Client for resource group operations
            self.resource_client = ResourceManagementClient(
                credential=self._credential,
                subscription_id=self.subscription_id
            )
            
            # Load Test Management Client for resource operations
            self.loadtest_mgmt_client = LoadTestMgmtClient(
                credential=self._credential,
                subscription_id=self.subscription_id
            )
            
            # Load Testing Clients will be initialized after resource creation
            self.loadtest_admin_client = None
            self.loadtest_run_client = None
            
            self.logger.info("✅ Azure SDK clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Azure SDK clients: {e}")
            raise
    
    def create_resource_group(self) -> bool:
        """
        Create the resource group if it doesn't exist.
        
        Returns:
            bool: True if resource group exists or was created successfully
        """
        try:
            self.logger.info(f"🔍 Checking if resource group '{self.resource_group_name}' exists...")
            
            # Check if resource group exists
            try:
                rg = self.resource_client.resource_groups.get(self.resource_group_name)
                self.logger.info(f"✅ Resource group '{self.resource_group_name}' already exists")
                return True
            except Exception:
                # Resource group doesn't exist, create it
                self.logger.info(f"📁 Creating resource group '{self.resource_group_name}'...")
                
                rg_params = {
                    'location': self.location,
                    'tags': {
                        'Environment': 'Performance Testing',
                        'Service': 'OSDU',
                        'CreatedBy': 'AzureLoadTestSDKManager'
                    }
                }
                
                result = self.resource_client.resource_groups.create_or_update(
                    self.resource_group_name,
                    rg_params
                )
                
                self.logger.info(f"✅ Resource group '{self.resource_group_name}' created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error creating resource group: {e}")
            raise
    
    def create_load_test_resource(self) -> Dict[str, Any]:
        """
        Create the Azure Load Test resource.
        
        Returns:
            Dict[str, Any]: The created load test resource information
        """
        try:
            self.logger.info(f"🏗️  Creating Azure Load Test resource '{self.load_test_name}'...")
            
            # Ensure resource group exists
            self.create_resource_group()
            
            # Check if load test resource already exists
            try:
                existing_resource = self.loadtest_mgmt_client.load_tests.get(
                    resource_group_name=self.resource_group_name,
                    load_test_name=self.load_test_name
                )
                self.logger.info(f"✅ Load test resource '{self.load_test_name}' already exists")
                
                # Initialize data plane client with existing resource
                self._init_data_plane_client()
                return existing_resource.as_dict()
                
            except Exception:
                # Resource doesn't exist, create it
                self.logger.info(f"Creating new load test resource...")
                
                # Define load test resource parameters
                load_test_params = {
                    'location': self.location,
                    'tags': {
                        'Environment': 'Performance Testing',
                        'Service': 'OSDU',
                        'CreatedBy': 'AzureLoadTestSDKManager'
                    },
                    'identity': {
                        'type': 'SystemAssigned'
                    }
                }
                
                # Create the load test resource
                create_operation = self.loadtest_mgmt_client.load_tests.begin_create_or_update(
                    resource_group_name=self.resource_group_name,
                    load_test_name=self.load_test_name,
                    load_test_resource=load_test_params
                )
                
                # Wait for creation to complete
                result = create_operation.result()
                
                self.logger.info(f"✅ Load test resource '{self.load_test_name}' created successfully")
                self.logger.info(f"   Resource ID: {result.id}")
                self.logger.info(f"   Data Plane URI: {result.data_plane_uri}")
                
                # Initialize data plane client
                self._init_data_plane_client()
                
                return result.as_dict()
                
        except Exception as e:
            self.logger.error(f"❌ Error creating load test resource: {e}")
            raise
    
    def _init_data_plane_client(self) -> None:
        """Initialize the data plane client after resource creation."""
        try:
            # Get the load test resource to obtain data plane URI
            resource = self.loadtest_mgmt_client.load_tests.get(
                resource_group_name=self.resource_group_name,
                load_test_name=self.load_test_name
            )
            
            if resource.data_plane_uri:
                # Initialize Load Testing Clients for data plane operations
                self.loadtest_admin_client = LoadTestAdministrationClient(
                    endpoint=resource.data_plane_uri,
                    credential=self._credential
                )
                
                self.loadtest_run_client = LoadTestRunClient(
                    endpoint=resource.data_plane_uri,
                    credential=self._credential
                )
                
                self.logger.info(f"✅ Data plane clients initialized: {resource.data_plane_uri}")
            else:
                raise ValueError("Data plane URI not available")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize data plane client: {e}")
            raise
    
    def create_test(self, 
                   test_id: str,
                   display_name: Optional[str] = None,
                   description: Optional[str] = None,
                   engine_instances: int = 1,
                   environment_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a test configuration.
        
        Args:
            test_id: Unique identifier for the test
            display_name: Display name for the test
            description: Test description
            engine_instances: Number of engine instances
            environment_variables: Environment variables for the test
            
        Returns:
            Dict[str, Any]: The created test information
        """
        try:
            if not self.loadtest_admin_client:
                raise ValueError("Data plane client not initialized. Create load test resource first.")
            
            self.logger.info(f"🧪 Creating test '{test_id}'...")
            
            '''
            # Prepare test configuration
            test_config = {
                'displayName': display_name or test_id,
                'description': description or f"Load test created by Azure Load Test SDK Manager",
                'kind': 'Locust',  # Set test type as Locust
                'loadTestConfiguration': {
                    'engineInstances': engine_instances,
                    'splitAllCSVs': False,
                    'quickStartTest': False
                },
                'passFailCriteria': {
                    'passFailMetrics': {}
                },
                'environmentVariables': environment_variables or {},
                'secrets': {},
                'certificate': None,
                'keyvaultReferenceIdentityType': 'SystemAssigned',  # Use system assigned identity
                'keyvaultReferenceIdentityId': None,
                "inputArtifacts": {
                    "testScriptFileInfo": {
                        "fileName": "locustfile.py"
                    }
                }
            }

            
            test_config = {
                "loadTestConfiguration": {
                    "engineInstances": 1
                },

                "inputArtifacts": {
                    "testScriptFileInfo": {
                        "fileName": "locustfile.py"
                    }
                }
            }
            '''
            test_config = {"testModel": {
                "testId": "locust-sample-test",
                'displayName': "Locust Sample Test",
                'description': "Load test created by Azure Load Test SDK Manager",
                "engineBuiltinIdentityType": "SystemAssigned"
            }}

            test_config={"testModel":{
                "testId": "sample-test",
                "Load testing framework ": "Locust",
                "engineInstances": 1,
                "engineBuiltinIdentityType": "SystemAssigned"
            }
            }

            # Create the test
            result = self.loadtest_admin_client.create_or_update_test(
                test_id=test_id,
                body=test_config
            )

            self.logger.info(f"✅ Test '{test_id}' created successfully, complete result to understand response body: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error creating test '{test_id}': {e}")
            raise
    
    def upload_test_files(self, 
                         test_id: str, 
                         file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Upload test files to a test.
        
        Args:
            test_id: Test identifier
            file_paths: List of file paths to upload
            
        Returns:
            List[Dict[str, Any]]: List of uploaded file information
        """
        try:
            if not self.loadtest_admin_client:
                raise ValueError("Data plane client not initialized. Create load test resource first.")
            
            self.logger.info(f"📁 Uploading {len(file_paths)} files to test '{test_id}'...")
            
            uploaded_files = []
            
            for file_path in file_paths:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.exists():
                    self.logger.warning(f"⚠️  File not found: {file_path}")
                    continue
                
                file_name = file_path_obj.name
                self.logger.info(f"   Uploading: {file_name}")
                
                # Determine file type
                if file_name.lower() == 'locustfile.py':
                    file_type = 'JMX_FILE'  # Main test script
                else:
                    file_type = 'ADDITIONAL_ARTIFACTS'  # Supporting files
                
                # Upload file
                with open(file_path, 'rb') as file_content:
                    result = self.loadtest_admin_client.begin_upload_test_file(
                        test_id=test_id,
                        file_name=file_name,
                        file_type=file_type,
                        body=file_content
                    ).result()  # Wait for upload to complete
                
                uploaded_files.append({
                    'fileName': file_name,
                    'fileType': file_type,
                    'result': result
                })
                
                self.logger.info(f"   ✅ Uploaded: {file_name}")
            
            self.logger.info(f"✅ Successfully uploaded {len(uploaded_files)} files")
            return uploaded_files
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading files to test '{test_id}': {e}")
            raise
    
    def run_test(self, 
                test_id: str,
                test_run_id: Optional[str] = None,
                display_name: Optional[str] = None,
                description: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a load test.
        
        Args:
            test_id: Test identifier
            test_run_id: Test run identifier (auto-generated if not provided)
            display_name: Display name for the test run
            description: Test run description
            
        Returns:
            Dict[str, Any]: The test run information
        """
        try:
            if not self.loadtest_run_client:
                raise ValueError("Data plane client not initialized. Create load test resource first.")
            
            # Generate test run ID if not provided
            if not test_run_id:
                import uuid
                test_run_id = f"{test_id}-run-{int(time.time())}"
            
            self.logger.info(f"🚀 Starting test run '{test_run_id}' for test '{test_id}'...")
            
            # Prepare test run configuration
            test_run_config = {
                'testId': test_id,
                'displayName': display_name or f"Test run for {test_id}",
                'description': description or f"Load test run created by Azure Load Test SDK Manager"
            }
            
            # Start the test run
            result = self.loadtest_run_client.begin_test_run(
                test_run_id=test_run_id,
                body=test_run_config
            ).result()  # Wait for test run to start
            
            self.logger.info(f"✅ Test run '{test_run_id}' started successfully")
            self.logger.info(f"   Status: {result.get('status', 'UNKNOWN')}")
            
        
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error running test '{test_id}': {e}")
  
def main():
    """
    Example usage of the Azure Load Test SDK Manager.
    """
    # Configuration
    subscription_id = "015ab1e4-bd82-4c0d-ada9-0f9e9c68e0c4"
    resource_group_name = "osdu_perf_dev"
    load_test_name = "osd_perf_new"
    location = "eastus"
    
    try:
        # Initialize the manager
        manager = AzureLoadTestSDKManager(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            load_test_name=load_test_name,
            location=location
        )
        
        # Create load test resource
        print("Creating Azure Load Test resource...")
        resource_info = manager.create_load_test_resource()
        print(f"Resource created: {resource_info.get('name', 'Unknown')}")
        
        # Create a test test_id = "sample-test"
        test_id = "sample-test"
        
        print("\nCreating a test...")
       
        test_info = manager.create_test(
            test_id=test_id,
            display_name="Sample Load Test",
            description="Sample test created by SDK manager",
            engine_instances=1,
            environment_variables={
                "LOCUST_USERS": "10",
                "LOCUST_SPAWN_RATE": "2",
                "LOCUST_RUN_TIME": "60"
            }
        )
        print(f"Test created: {test_info.get('testId', 'Unknown')}")
        return 
        # Create sample test files for upload
        print("\nCreating sample test files...")
        import tempfile
        import os
        
        # Create temporary directory for test files
        temp_dir = tempfile.mkdtemp()
        
        
        # Create a sample locustfile.py
        locustfile_content = '''"""
Sample Locust Test File for Azure Load Testing
"""

import os
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts."""
        self.host = os.environ.get("LOCUST_HOST", "https://httpbin.org")
    
    @task(3)
    def test_get_request(self):
        """Test GET request."""
        self.client.get("/get")
    
    @task(1)
    def test_post_request(self):
        """Test POST request."""
        self.client.post("/post", json={"test": "data"})
'''
        
        # Create requirements.txt
        requirements_content = '''locust>=2.0.0
requests>=2.25.0
'''
        
        # Write files
        locustfile_path = os.path.join(temp_dir, "locustfile.py")
        requirements_path = os.path.join(temp_dir, "requirements.txt")
        
        with open(locustfile_path, 'w') as f:
            f.write(locustfile_content)
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        print(f"Created test files in: {temp_dir}")
        
        # Upload test files
        print("\nUploading test files...")
        uploaded_files = manager.upload_test_files(
            test_id=test_id,
            file_paths=[locustfile_path, requirements_path]
        )
        print(f"Uploaded {len(uploaded_files)} files:")
        print(f"  Files: {uploaded_files}")
        for file_info in uploaded_files:
            print(f"  - {file_info['fileName']} ({file_info['fileType']})")
        
        
        

        # Run the test
        print("\nRunning the test...")
        import time
        test_run_id = f"{test_id}-run-{int(time.time())}"
        
        test_run_result = manager.run_test(
            test_id=test_id,
            test_run_id=test_run_id,
            display_name="Sample Test Run",
            description="Automated test run via SDK manager"
        )
        
        print(f"Test run started: {test_run_result.get('testRunId', 'Unknown')}")
        print(f"Status: {test_run_result.get('status', 'Unknown')}")
        
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary files")

        print("\nAzure Load Test SDK Manager example completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()