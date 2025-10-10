import gevent.monkey
gevent.monkey.patch_all()

import os
from pathlib import Path
import getpass
class InitManager:
    def __init__(self):
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            # Perform initialization tasks here
            print("Initializing...")
            self.initialized = True
        else:
            print("Already initialized.")

    def create_project_config(self, output_path: Path, service_name: str = None) -> None:
        """Creates a config.yaml file for the project."""
        username = getpass.getuser()
        test_run_id_prefix = f"{username}_{service_name}_test" if service_name else f"{username}_osdu_test"
        
        

        # Best practice: Load this template from a file in a 'templates' directory
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
        output_path.write_text(config_content, encoding='utf-8')
        print(f"[create_project_config] Created config.yaml at {output_path} generated prefix {test_run_id_prefix}")

    
    def create_service_test_file(self, output_path: Path, service_name: str):
        print(f"[create_service_test_file] Creating test file for service: {service_name} path {output_path}")

        output_path.write_text(f"# Test file for {service_name}\n", encoding='utf-8')
        print(f"✅ Created {output_path.name}")

    def create_requirements_file(self, output_path: Path):
        
        output_path.write_text(f"osdu_perf\n", encoding='utf-8')
        print(f"[create_requirements_file] Created {output_path.name}")

    def create_project_readme(self, output_path: Path, service_name: str):
        output_path.write_text(f"# README for {service_name} tests\n", encoding='utf-8')
        print(f"[create_project_readme] Created {output_path.name}")

    def create_locustfile_template(self, output_path: Path, service_name:str):
        output_path.write_text("# Main locustfile.py\n", encoding='utf-8')
        print(f"[create_locustfile_template] Created {output_path.name}")

    # required 
    
    def _should_create_file(self, filepath: str, choice: str) -> bool:
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

    def _create_file_if_needed(self, path: Path, creation_func, choice: str, *args) -> None:
        """A wrapper to create a file or skip it based on user choice."""
        if self._should_create_file(path, choice):
            # Unpack the list of args if it's passed as a single list
            creation_func(path, *args[0] if isinstance(args[0], list) else args)
        else:
            print(f"⏭️  Skipped existing: {path.name}")

    def init_project(self, service_name: str, force: bool = False) -> None:
        """
        Initialize a new performance testing project for a specific service.
        
        Args:
            service_name: Name of the service to test (e.g., 'storage', 'search', 'wellbore')
            force: If True, overwrite existing files without prompting
        """
        project_name = f"perf_tests"
        test_filename = f"perf_{service_name}_test.py"
        project_path = Path.cwd() / project_name
        
        print(f"[init_project] Initializing OSDU Performance Testing project for: {service_name}")
        
        # Check if project already exists
        if os.path.exists(project_name):
            print(f"[init_project]  Directory '{project_name}' already exists!")
            
            # Check if specific service test file exists
            test_file_path = os.path.join(project_name, test_filename)
            if os.path.exists(test_file_path):
                print(f"[init_project]  Test file '{test_filename}' already exists!")
                
                if force:
                    choice = 'o'  # Force overwrite
                    print("[init_project] Force mode: Overwriting existing files...")
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
                            #_backup_existing_files(project_name, service_name)
                            break
                        elif choice in ['c', 'cancel']:
                            print("❌ Initialization cancelled.")
                            return
                        else:
                            print("❌ Invalid choice. Please enter 'o', 's', 'b', or 'c'.")
            else:
                # Directory exists but no service test file
                choice = 's' if not force else 'o'  # Skip mode or force
                print(f"[init_project] Directory exists but '{test_filename}' not found. Creating missing files...")
        else:
            choice = 'o'  # New project
            print(f"[init_project] Creating new project directory: {project_name}")
            # Create project directory
            os.makedirs(project_name, exist_ok=True)
        
        files_to_create = [
            {"name": test_filename, "creator": self.create_service_test_file, "args": [service_name]},
            {"name": "requirements.txt", "creator": self.create_requirements_file, "args": []},
            {"name": "README.md", "creator": self.create_project_readme, "args": [service_name]},
            {"name": "locustfile.py", "creator": self.create_locustfile_template, "args": [service_name]},
            {"name": "config.yaml", "creator": self.create_project_config, "args": [service_name]},
        ]
        
        for file_meta in files_to_create:
            file_path = project_path / file_meta["name"]
            self._create_file_if_needed(file_path, file_meta["creator"], choice, file_meta["args"])

        
        print(f"\n[init_project] Project {'updated' if choice == 's' else 'initialized'} successfully in {project_name}/")
        if choice != 's':
            print(f"[init_project] Created test file: {test_filename}")
        print(f"\n[init_project] Next steps:")
        print(f"   1. cd {project_name}")
        print("   2. pip install -r requirements.txt")
        print(f"   3. Edit config.yaml to set your OSDU environment details (host, partition, app_id, token)")
        print(f"   4. Edit {test_filename} to implement your test scenarios")
        print(f"   5. Run local tests: osdu-perf run local --config config.yaml")
        print(f"   6. Run Azure Load Tests: osdu-perf run azure_load_test --config config.yaml --subscription-id <sub-id> --resource-group <rg> --location <location>")
        print(f"   7. Optional: Override config values with CLI arguments (e.g., --host, --partition, --token)")
        
