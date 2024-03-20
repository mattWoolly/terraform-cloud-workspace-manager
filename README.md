# Terraform Cloud Workspace Manager

This Python script is designed to manage Terraform Cloud workspace settings efficiently, offering command-line options to change workspace execution modes, update VCS branch settings, configure VCS trigger paths, and reset workspace settings to a predefined state.

## Features

-   **Set Execution Mode**: Switch between local and remote execution modes for your Terraform Cloud workspaces.
-   **Change VCS Branch**: Update the VCS branch that your Terraform Cloud workspace tracks.
-   **Set VCS Trigger Paths**: Specify paths within your repository that should trigger runs when changes are detected.
-   **Set VCS Trigger Paths**: Define paths within your repository to trigger runs when changes are detected.
-   **Reset Workspace Settings**: Apply a predefined set of settings to quickly reset or initialize a workspace configuration.

## Getting Started

### Prerequisites

-   Python 3.x installed on your machine.
-   `requests` and `colorama` Python packages installed.
-   A valid Terraform Cloud API token.

### Installation

1.  Ensure Python 3 and pip are installed on your system.
2.  Install the required Python packages 
`pip install -r requirements.txt` 

3.  Clone this repository or download the script to your local machine.
4.  Create a config.json file in the same directory as the script with your Terraform Cloud API token and base URL:
```
{
    "API_TOKEN": "<your_api_token_here>",
    "API_BASE_URL": "https://app.terraform.io/api/v2/"
}
```
Replace <your_api_token_here> with your actual Terraform Cloud API token.

### Usage

The script can be run from the command line with various arguments to perform actions on your Terraform Cloud workspace.

-   **Set Execution Mode**:
`./workspace_manager.py --local # Set workspace to local execution mode.
./workspace_manager.py --remote # Set workspace to remote execution mode.` 

-   **Change VCS Branch**:
`./workspace_manager.py --change-branch "new-branch-name"` 

-   **Set VCS Trigger Paths**:
`./workspace_manager.py --set-trigger-paths` 

-   **Reset workspace to default settings (remote, main branch, working directory, and trigger paths)**
`./workspace_manager.py --reset-workspace`

The script determines the repository root and sets trigger paths based on your current working directory.

### Setting up Aliases

1.  **Open Your Zsh Configuration File**:

Open your `~/.zshrc` file in your preferred text editor. This file is executed whenever you start a new zsh session.

2.  **Add Aliases**:

At the bottom of the file, add aliases for the script. Be sure to replace `(path to the script)` with the actual path to your `workspace_manager.py` script. For example:

```
alias tflocal='python3 /path/to/workspace_manager.py --local'
alias tfremote='python3 /path/to/workspace_manager.py --remote'
alias tfsetbranch='python3 /path/to/workspace_manager.py --change-branch main'
alias tfsettriggers='python3 /path/to/workspace_manager.py --set-trigger-paths'
alias tfreset='python3 /path/to/workspace_manager.py --reset-workspace'
```

These aliases allow you to execute the script's functionalities without typing the full command:

-   **tflocal**: Set workspace to local execution mode.
-   **tfremote**: Set workspace to remote execution mode.
-   **tfsetbranch**: Change the VCS branch of the workspace. Usage: `tfsetbranch new-branch-name`
-   **tfsettriggers**: Set VCS trigger paths based on the repo root.

3.  **Reload Your Configuration**:

For the changes to take effect, reload your `.zshrc` file by running:

`% source ~/.zshrc` 

or simply close and reopen your terminal.

### Usage

With aliases set up, you can now easily manage your Terraform Cloud workspace settings using short commands:

-   Switch to local execution mode:
```
% tflocal
```
-   Switch to remote execution mode
```
% tfremote
```

-   Change the VCS branch (replace `new-branch-name` with your target branch name):

`% tfsetbranch new-branch-name` 

-   Set the VCS trigger paths:
```
% tfsettriggers
```

### Adding New Features

To extend this script with new functionalities:

1.  **Understand Existing Classes**: Familiarize yourself with the `TerraformCloudAPI` and `TerraformWorkspaceManager` classes. New API functionalities can be added as methods to these classes.
    
2.  **Add New Method**: For a new feature, add a method in `TerraformWorkspaceManager`. Use `patch_workspace` method from `TerraformCloudAPI` for making API calls.
    
3.  **Update `main` Function**: Incorporate your new method into the `main` function with appropriate argument parsing.
    
4.  **Test Your Changes**: Always test new functionalities to ensure they work as expected before using them in production.
    

## Contributing

Contributions to enhance this script are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is open-sourced under the MIT License.