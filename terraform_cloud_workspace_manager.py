#!/usr/bin/env python3

import requests
import re
import argparse
import os
from pathlib import Path
from urllib.parse import urljoin
from colorama import Fore, init

# Initialize Colorama for colored output in the terminal
init(autoreset=True)

# Constants and Configuration
API_BASE_URL = "https://app.terraform.io/api/v2/"
API_TOKEN = "API_TOKEN"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/vnd.api+json",
}

class TerraformCloudAPI:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = HEADERS

    def patch_workspace(self, organization_name, workspace_name, data):
        url = urljoin(self.base_url, f"organizations/{organization_name}/workspaces/{workspace_name}")
        return requests.patch(url, json=data, headers=self.headers)

class WorkspaceManager:
    def __init__(self, api_client):
        self.api_client = api_client

    @staticmethod
    def find_workspace_and_org(filename="terraform.tf"):
        try:
            with open(filename, "r") as file:
                content = file.read()
            workspace_name = WorkspaceManager._extract_value(content, 'workspaces {[^}]*name = "(.*?)"')
            organization_name = WorkspaceManager._extract_value(content, 'organization = "(.*?)"')
            return workspace_name, organization_name
        except FileNotFoundError:
            print(Fore.RED + f"{filename} file not found in the current directory.\n")
            return None, None

    def update_workspace_settings(self, organization_name, workspace_name, **kwargs):
        data = {"data": {"attributes": kwargs, "type": "workspaces"}}
        response = self.api_client.patch_workspace(organization_name, workspace_name, data)
        WorkspaceManager._log_response(response, kwargs)

    @staticmethod
    def _extract_value(content, pattern):
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None

    @staticmethod
    def _log_response(response, settings):
        if response.status_code == 200:
            if "working-directory" in settings:
                print(Fore.GREEN + f"    ✓ Successfully updated working directory to: {settings['working-directory']}")
            if "execution-mode" in settings:
                print(Fore.GREEN + f"    ✓ Successfully updated workspace execution mode to: {settings['execution-mode']}")
            if "trigger-patterns" in settings:
                print(Fore.GREEN + f"    ✓ Successfully updated workspace trigger patterns to: {settings['trigger-patterns']}")
        else:
            print(Fore.RED + f"    ✖ Failed to update workspace settings. Status code: {response.status_code}, Message: {response.text}\n")

    @staticmethod
    def find_repo_root(current_path):
        path = Path(current_path)
        for parent in [path] + list(path.parents):
            if any((parent / '.git').exists() for child in parent.iterdir()):
                return parent
        return path

    @staticmethod
    def get_working_directory():
        repo_root = WorkspaceManager.find_repo_root(os.getcwd())
        return os.path.relpath(os.getcwd(), start=repo_root)

def main():
    parser = argparse.ArgumentParser(description='Manage Terraform Cloud workspace settings.')
    parser.add_argument('--local', action='store_true', help='Set workspace to local execution mode.')
    parser.add_argument('--remote', action='store_true', help='Set workspace to remote execution mode.')
    parser.add_argument('--change-branch', type=str, help='Change the VCS branch of the workspace.')
    parser.add_argument('--set-working-directory', action='store_true', help='Update the working directory based on the current directory relative to the repo root.')
    parser.add_argument('--set-trigger-paths', action='store_true', help='Set VCS trigger paths based on the current directory relative to the repo root.')

    args = parser.parse_args()

    api_client = TerraformCloudAPI()
    manager = WorkspaceManager(api_client)

    workspace_name, organization_name = manager.find_workspace_and_org()

    if workspace_name and organization_name:
        print(Fore.GREEN + f"Workspace '{workspace_name}' found in organization '{organization_name}'.")

        settings = {}
        if args.local:
            settings["execution-mode"] = "local"
        elif args.remote:
            settings["execution-mode"] = "remote"
        if args.change_branch:
            settings["vcs-repo"] = {"branch": args.change_branch}
        if args.set_working_directory:
            settings["working-directory"] = WorkspaceManager.get_working_directory()
        if args.set_trigger_paths:
            repo_root = WorkspaceManager.find_repo_root(os.getcwd())
            relative_path = os.path.relpath(os.getcwd(), start=repo_root)
            trigger_paths = [f"{relative_path}/**/*", f"{relative_path}/common/**/*"]
            settings["trigger-patterns"] = trigger_paths

        # Update the workspace with the collected settings
        if settings:
            manager.update_workspace_settings(organization_name, workspace_name, **settings)

if __name__ == "__main__":
    main()
