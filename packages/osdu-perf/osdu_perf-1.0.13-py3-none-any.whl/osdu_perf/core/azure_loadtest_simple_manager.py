"""
Azure Load Test SDK Manager - Simplified Version

A minimal manager for Azure Load Testing using the official Python SDK.
Contains only the essential methods for creating resources, tests, uploading files, and running tests.

Author: OSDU Performance Testing Team
Date: October 2025
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Azure SDK imports
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.loadtesting import LoadTestMgmtClient
from azure.developer.loadtesting import LoadTestingClient


class AzureLoadTestManager:
    """
    Simplified Azure Load Test Manager using official Python SDK.
    
    Contains only essential methods:
    - create_load_test_resource: Creates Azure Load Test resource
    - create_test: Creates a test configuration
    - upload_files: Uploads test files
    - run_test: Runs a load test
    """
    
    def __init__(self, 
                 subscription_id: str,
                 resource_group_name: str,
                 load_test_name: str,
                 location: str = "eastus"):
        """
        Initialize the Azure Load Test Manager.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Resource group name
            load_test_name: Name for the load test resource
            location: Azure region (default: "eastus")
        """
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.load_test_name = load_test_name
        self.location = location
        
        # Initialize logger
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Initialize Azure credential and clients
        self._credential = AzureCliCredential()
        self.resource_client = ResourceManagementClient(
            credential=self._credential,
            subscription_id=self.subscription_id
        )
        self.loadtest_mgmt_client = LoadTestMgmtClient(
            credential=self._credential,
            subscription_id=self.subscription_id
        )
        self.loadtest_client = None
    
    def create_load_test_resource(self) -> Dict[str, Any]:
        """
        Create the Azure Load Test resource.
        
        Returns:
            Dict[str, Any]: The created load test resource information
        """
        # Create resource group if it doesn't exist
        try:
            self.resource_client.resource_groups.get(self.resource_group_name)
        except Exception:
            rg_params = {
                'location': self.location,
                'tags': {'Environment': 'Performance Testing', 'Service': 'OSDU'}
            }
            self.resource_client.resource_groups.create_or_update(
                self.resource_group_name, rg_params
            )
        
        # Check if load test resource already exists
        try:
            existing_resource = self.loadtest_mgmt_client.load_tests.get(
                resource_group_name=self.resource_group_name,
                load_test_name=self.load_test_name
            )
            # Initialize data plane client
            self.loadtest_client = LoadTestingClient(
                endpoint=existing_resource.data_plane_uri,
                credential=self._credential
            )
            return existing_resource.as_dict()
        except Exception:
            # Create new load test resource
            load_test_params = {
                'location': self.location,
                'tags': {'Environment': 'Performance Testing', 'Service': 'OSDU'},
                'identity': {'type': 'SystemAssigned'}
            }
            
            create_operation = self.loadtest_mgmt_client.load_tests.begin_create_or_update(
                resource_group_name=self.resource_group_name,
                load_test_name=self.load_test_name,
                load_test_resource=load_test_params
            )
            
            result = create_operation.result()
            
            # Initialize data plane client
            self.loadtest_client = LoadTestingClient(
                endpoint=result.data_plane_uri,
                credential=self._credential
            )
            
            return result.as_dict()
    
    def create_test(self, 
                   test_id: str,
                   display_name: str,
                   description: str,
                   engine_instances: int = 1,
                   environment_variables: Dict[str, str] = None) -> Dict[str, Any]:
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
        if not self.loadtest_client:
            raise ValueError("Load test resource not created. Call create_load_test_resource first.")
        
        test_config = {
            'displayName': display_name,
            'description': description,
            'loadTestConfiguration': {
                'engineInstances': engine_instances,
                'splitAllCSVs': False,
                'quickStartTest': False
            },
            'passFailCriteria': {'passFailMetrics': {}},
            'environmentVariables': environment_variables or {}
        }
        
        result = self.loadtest_client.administration.create_or_update_test(
            test_id=test_id,
            body=test_config
        )
        
        return result
    
    def upload_files(self, test_id: str, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Upload test files to a test.
        
        Args:
            test_id: Test identifier
            file_paths: List of file paths to upload
            
        Returns:
            List[Dict[str, Any]]: List of uploaded file information
        """
        if not self.loadtest_client:
            raise ValueError("Load test resource not created. Call create_load_test_resource first.")
        
        uploaded_files = []
        
        for file_path in file_paths:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                continue
            
            file_name = file_path_obj.name
            
            # Determine file type
            if file_name.lower() == 'locustfile.py':
                file_type = 'JMX_FILE'
            else:
                file_type = 'ADDITIONAL_ARTIFACTS'
            
            # Upload file
            with open(file_path, 'rb') as file_content:
                result = self.loadtest_client.administration.upload_test_file(
                    test_id=test_id,
                    file_name=file_name,
                    file_type=file_type,
                    body=file_content
                )
            
            uploaded_files.append({
                'fileName': file_name,
                'fileType': file_type,
                'result': result
            })
        
        return uploaded_files
    
    def run_test(self, 
                test_id: str,
                test_run_id: str,
                display_name: str,
                description: str) -> Dict[str, Any]:
        """
        Run a load test.
        
        Args:
            test_id: Test identifier
            test_run_id: Test run identifier
            display_name: Display name for the test run
            description: Test run description
            
        Returns:
            Dict[str, Any]: The test run information
        """
        if not self.loadtest_client:
            raise ValueError("Load test resource not created. Call create_load_test_resource first.")
        
        test_run_config = {
            'testId': test_id,
            'displayName': display_name,
            'description': description
        }
        
        result = self.loadtest_client.test_run.create_or_update_test_run(
            test_run_id=test_run_id,
            body=test_run_config
        )
        
        return result


def main():
    """
    Example usage of the simplified Azure Load Test Manager.
    """
    # Configuration
    subscription_id = "015ab1e4-bd82-4c0d-ada9-0f9e9c68e0c4"
    resource_group_name = "osdu_perf_dev"
    load_test_name = "osd_perf_new"
    
    # Initialize manager
    manager = AzureLoadTestManager(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        load_test_name=load_test_name
    )
    
    # Create load test resource
    resource_info = manager.create_load_test_resource()
    print(f"Resource created: {resource_info.get('name', 'Unknown')}")
    
    # Create a test
    test_info = manager.create_test(
        test_id="sample-test",
        display_name="Sample Load Test",
        description="Sample test",
        engine_instances=1,
        environment_variables={"LOCUST_USERS": "10", "LOCUST_SPAWN_RATE": "2"}
    )
    print(f"Test created: {test_info.get('testId', 'Unknown')}")
    
    # Upload files (example - requires actual files)
    # uploaded_files = manager.upload_files("sample-test", ["locustfile.py", "requirements.txt"])
    
    # Run test
    # run_result = manager.run_test("sample-test", "test-run-1", "Test Run", "Sample test run")
    
    print("Azure Load Test Manager example completed!")


if __name__ == "__main__":
    main()