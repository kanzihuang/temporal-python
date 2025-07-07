# Temporal Python Project

A Python project following coding standards and best practices.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kanzihuang/temporal-python.git
   cd temporal-python
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Temporal Workflow for VMware VM Creation

This project implements a Temporal workflow to automate VMware virtual machine creation.

### Architecture
- **Workflows**: Orchestrates the VM creation process (`vm_workflows.py`)
- **Activities**: Contains the business logic for VM creation (`vm_activities.py`)
- **VMware Service**: Handles VMware API interactions (`vmware_service.py`)
- **Configuration**: VMware connection details stored in `config.yaml`
- **Worker**: Processes workflow tasks (`vm_worker.py`)
- **Client**: Submits VM creation requests (`start_vm_workflow.py`)

### Prerequisites
- Temporal Server running locally (see [Temporal docs](https://docs.temporal.io/cli#start-a-dev-server))
- VMware vCenter Server access
- Python 3.8+ and dependencies installed

### Configuration
1. Edit `config.yaml` with your VMware vCenter details:
   ```yaml
   vmware:
     host: "vc01.example.com"
     port: 443
     username: "administrator@vsphere.local"
     password: "your-secure-password"
     datacenter: "Datacenter01"
     cluster: "Cluster01"
     datastore: "Datastore01"
     network: "VM Network"
     folder: "/Datacenter01/vm/Workloads"
   ```

### Running the Workflow

1. **Start Temporal Server**:
   ```bash
   temporal server start-dev
   ```

2. **Start the Temporal Worker**:
   ```bash
   python -m temporal_python.workers.vm_worker
   ```

3. **Submit a VM Creation Request**:
   ```bash
   python -m temporal_python.clients.start_vm_workflow \
     --vm-name "test-vm-01" \
     --guest-id "ubuntu64Guest" \
     --num-cpus 2 \
     --memory-gb 4 \
     --disk-size-gb 40 \
     --notes "Created via Temporal workflow" \
     --task-queue vmware
   ```

## Coding Standards

This project follows PEP 8 style guide and uses the following tools to ensure code quality:
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking

### Running Checks

To run all checks manually:
```bash
pre-commit run --all-files
```

To run tests:
```bash
pytest
```