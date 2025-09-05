<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements - Python Nornir network automation script for reading MAC addresses from Cisco devices
	<!-- Ask for project type, language, and frameworks if not specified. Skip if already provided. -->

- [x] Scaffold the Project - Created Python project structure with Nornir configuration
	<!--
	Ensure that the previous step has been marked as completed.
	Call project setup tool with projectType parameter.
	Run scaffolding command to create project files and folders.
	Use '.' as the working directory.
	If no appropriate projectType is available, search documentation using available tools.
	Otherwise, create the project structure manually using available file creation tools.
	-->

- [x] Customize the Project - Added connectivity test script and comprehensive documentation
	<!--
	Verify that all previous steps have been completed successfully and you have marked the step as completed.
	Develop a plan to modify codebase according to user requirements.
	Apply modifications using appropriate tools and user-provided references.
	Skip this step for "Hello World" projects.
	-->

- [x] Install Required Extensions - No extensions needed for Python project
	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->

- [x] Compile the Project - Dependencies installed and scripts tested successfully
	<!--
	Verify that all previous steps have been completed.
	Install any missing dependencies.
	Run diagnostics and resolve any issues.
	Check for markdown files in project folder for relevant instructions on how to do this.
	-->

- [x] Create and Run Task - No tasks needed for Python script project
	<!--
	Verify that all previous steps have been completed.
	Check https://code.visualstudio.com/docs/debugtest/tasks to determine if the project needs a task. If so, use the create_and_run_task to create and launch a task based on package.json, README.md, and project structure.
	Skip this step otherwise.
	 -->

- [x] Launch the Project - Python scripts are ready for execution
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [x] Ensure Documentation is Complete - README.md and copilot-instructions.md are complete

## Project Summary

This is a Python network automation project using Nornir to scan MAC addresses from Cisco devices.

### Key Files:
- `get_mac_addresses.py` - Main MAC address scanner script
- `test_connectivity.py` - Connectivity testing utility
- `config.yaml` - Nornir configuration
- `inventory/` - Device inventory (hosts, groups, defaults)
- `requirements.txt` - Python dependencies

### Usage:
1. Test connectivity: `python3 test_connectivity.py`
2. Scan MAC addresses: `python3 get_mac_addresses.py`

### Device Configuration:
- Username: admin
- Password: cisco  
- Supports Cisco IOS and NX-OS platforms

### Prerequisites:
- Python 3.7+
- SSH access to network devices
- Dependencies installed via `pip install -r requirements.txt`
