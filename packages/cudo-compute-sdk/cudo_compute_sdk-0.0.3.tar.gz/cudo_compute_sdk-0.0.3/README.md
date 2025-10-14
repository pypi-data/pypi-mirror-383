<div align="center">

<a href="https://www.vantagecompute.ai/">

  <img src="https://vantage-compute-public-assets.s3.us-east-1.amazonaws.com/branding/vantage-logo-text-black-horz.png" alt="Vantage Compute Logo" width="100" style="margin-bottom: 0.5em;"/>

</a>
</div>

<div align="center">

# Cudo Compute SDK

A Python SDK for the Cudo Compute Platform API.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/cudo-compute-sdk.svg)](https://pypi.org/project/cudo-compute-sdk/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

![GitHub Issues](https://img.shields.io/github/issues/vantagecompute/cudo-comptue-sdk?label=issues&logo=github&style=plastic)
![Pull Requests](https://img.shields.io/github/issues-pr/vantagecompute/cudo-compute-sdk?label=pull-requests&logo=github&style=plastic)
![GitHub Contributors](https://img.shields.io/github/contributors/vantagecompute/cudo-compute-sdk?logo=github&style=plastic)

</br>

</div>

A Python SDK for interacting with the [Cudo Compute](https://www.cudocompute.com/) REST API. Manage virtual machines, storage, networks, and other cloud resources programmatically.

## Features

- **Async/Await Support** - Built on `httpx` for efficient async operations
- **Type Safe** - Comprehensive type hints with Pydantic models
- **Full API Coverage** - Complete support for VMs, storage, networking, and more
- **Well Tested** - 112 tests with 78% code coverage
- **Great Documentation** - Detailed docs with examples

## Installation

### Using pip

```bash
pip install cudo-compute-sdk
```

### Using uv (recommended)

```bash
uv add cudo-compute-sdk
```

## Quick Start

### Basic Usage

```python
import asyncio
from cudo_compute_sdk import CudoComputeSDK

async def main():
    # Initialize the SDK with your API key
    sdk = CudoComputeSDK(api_key="your-api-key-here")
    
    try:
        # List all projects
        projects = await sdk.list_projects()
        print(f"Found {len(projects)} projects")
        
        # List VMs in a project
        vms = await sdk.list_vms(project_id="my-project")
        for vm in vms:
            print(f"VM: {vm.id} - State: {vm.state}")
    
    finally:
        # Clean up
        await sdk.close()

asyncio.run(main())
```

### Creating a Virtual Machine

```python
async def create_vm_example():
    sdk = CudoComputeSDK(api_key="your-api-key")
    
    try:
        vm = await sdk.create_vm(
            project_id="my-project",
            vm_id="my-vm-001",
            data_center_id="gb-bournemouth-1",
            machine_type="standard",
            boot_disk_image_id="ubuntu-2204-lts",
            vcpus=2,
            memory_gib=4,
            gpus=0,
            ssh_key_source="SSH_KEY_SOURCE_USER"
        )
        print(f"Created VM: {vm.id}")
        print(f"IP Address: {vm.external_ip_address}")
    
    finally:
        await sdk.close()
```

### Managing Storage

```python
async def storage_example():
    sdk = CudoComputeSDK(api_key="your-api-key")
    
    try:
        # Create a disk
        disk = await sdk.create_disk(
            project_id="my-project",
            disk_id="data-disk-001",
            data_center_id="gb-bournemouth-1",
            size_gib=100
        )
        
        # Attach to VM
        await sdk.attach_disk(
            project_id="my-project",
            disk_id="data-disk-001",
            vm_id="my-vm-001"
        )
        
        print(f"Created and attached disk: {disk.id}")
    
    finally:
        await sdk.close()
```

## API Key Setup

1. Log in to [Cudo Compute](https://www.cudocompute.com/)
2. Navigate to your account settings
3. Generate an API key
4. Set it as an environment variable:

```bash
export CUDO_API_KEY="your-api-key-here"
```

Then use it in your code:

```python
import os
from cudo_compute_sdk import CudoComputeSDK

sdk = CudoComputeSDK(api_key=os.getenv("CUDO_API_KEY"))
```

## Documentation

Visit the full project documentation: [Cudo Compute SDK Docs](https://vantagecompute.github.io/cudo-compute-sdk)

### Key Sections

- **[Installation Guide](https://vantagecompute.github.io/cudo-compute-sdk/installation)** - Detailed setup instructions
- **[Usage Examples](https://vantagecompute.github.io/cudo-compute-sdk/usage)** - Common use cases and examples
- **[API Reference](https://vantagecompute.github.io/cudo-compute-sdk/api-reference)** - Complete API documentation
- **[Architecture](https://vantagecompute.github.io/cudo-compute-sdk/architecture)** - SDK design and patterns
- **[Troubleshooting](https://vantagecompute.github.io/cudo-compute-sdk/troubleshooting)** - Common issues and solutions

## Supported Operations

### Virtual Machines
- Create, start, stop, reboot, terminate VMs
- Resize VMs (CPU, memory)
- List and get VM details
- Connect via web console
- Monitor VM metrics

### Data Centers & Machine Types
- List available data centers
- Get machine type specifications
- Query pricing information

### Storage
- Create and manage disks
- Attach/detach disks to VMs
- Create and manage NFS volumes
- Manage VM images (public and private)

### Networking
- Create and manage virtual networks
- Configure security groups and rules
- Manage SSH keys

### Projects & Billing
- List and manage projects
- View billing account information

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/vantagecompute/cudo-compute-sdk.git
cd cudo-compute-sdk

# Install dependencies
uv sync --extra dev

# Run tests
just unit

# Run type checking
just typecheck

# Format code
just fmt

# Run linter
just lint
```

### Running Tests

```bash
# Run all unit tests with coverage
just unit

# Run tests with verbose output
uv run pytest tests/unit -v

# Run specific test file
uv run pytest tests/unit/test_sdk.py -v
```

### Project Structure

```
cudo-compute-sdk/
├── cudo_compute_sdk/
│   ├── __init__.py          # Main SDK implementation
│   └── schema.py            # Pydantic models for API data
├── tests/
│   └── unit/
│       ├── test_sdk.py      # SDK method tests
│       └── test_schema.py   # Schema model tests
├── docusaurus/              # Documentation site
├── justfile                 # Development task runner
├── pyproject.toml           # Project configuration
└── README.md
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/cudo-compute-sdk.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write tests for new functionality
   - Ensure all tests pass: `just unit`
   - Run type checking: `just typecheck`
   - Format code: `just fmt`

4. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Coding Standards

- **Python 3.12+** required
- **Type hints** on all public methods
- **Docstrings** for all public methods (Google style)
- **Tests** for all new functionality
- **80%+ test coverage** for new code

### Development Commands

```bash
just unit          # Run unit tests with coverage
just typecheck     # Run static type checking
just fmt           # Format code with ruff
just lint          # Run linters (codespell + ruff)
just docs-dev      # Start documentation dev server
just docs-build    # Build documentation
```

## Requirements

- Python 3.12 or higher
- Dependencies:
  - `httpx` >= 0.28.1 (async HTTP client)
  - `pydantic` >= 2.0.0 (data validation)

## License

This project is licensed under the Apache License 2.0.

See the [LICENSE](LICENSE) file for details.

### Key Points

- ✅ Free to use, modify, and distribute
- ✅ Commercial use permitted
- ✅ Patent rights granted
- ✅ Must include license and copyright notice
- ✅ Changes must be documented

## Support

- 📖 **Documentation**: [https://vantagecompute.github.io/cudo-compute-sdk](https://vantagecompute.github.io/cudo-compute-sdk)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/vantagecompute/cudo-compute-sdk/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/vantagecompute/cudo-compute-sdk/discussions)
- 📧 **Email**: support@vantagecompute.ai

## Acknowledgments

Built with:
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [pytest](https://pytest.org/) - Testing framework
- [Docusaurus](https://docusaurus.io/) - Documentation

## Copyright

Copyright 2025 Vantage Compute Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

Made with ❤️ by [Vantage Compute](https://vantagecompute.ai)
