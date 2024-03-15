#!/usr/bin/env python3

import requests
import re
import argparse
import os
from pathlib import Path
from urllib.parse import urljoin
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Constants and Configuration
API_BASE_URL = "https://app.terraform.io/api/v2/"
API_TOKEN = "API_TOKEN"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/vnd.api+json",
}


class TerraformCloudAPI:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def patch_workspace(self, organization_name, workspace_name, data):
        url = urljoin(
            self.base_url,
            f"organizations/{organization_name}/workspaces/{workspace_name}",
        )
        response = requests.patch(url, json=data, headers=self.headers)
        return response


class TerraformWorkspaceManager:
    def __init__(self, api_client):
        self.api_client = api_client

    def find_workspace_and_org(self, filename="terraform.tf"):
        try:
            with open(filename, "r") as file:
                content = file.read()
            workspace_name = self._extract_value(
                content, 'workspaces {[^}]*name = "(.*?)"'
            )
            organization_name = self._extract_value(content, 'organization = "(.*?)"')
            return workspace_name, organization_name
        except FileNotFoundError:
            print(Fore.RED + f"{filename} file not found in the current directory.\n")
            return None, None

    def update_workspace_settings(
        self, organization_name, workspace_name, mode=None, branch=None
    ):
        data = {"data": {"attributes": {}, "type": "workspaces"}}
        if mode is not None:
            data["data"]["attributes"]["execution-mode"] = (
                "remote" if mode == "remote" else "local"
            )
        if branch is not None:
            data["data"]["attributes"]["vcs-repo"] = {"branch": branch}
        response = self.api_client.patch_workspace(
            organization_name, workspace_name, data
        )
        operation = (
            f"changed execution mode to {mode}"
            if mode
            else f"changed the VCS branch to {branch}"
        )
        self._log_response(response, operation + "\n")

    def set_vcs_trigger_paths(self, organization_name, workspace_name, trigger_paths):
        data = {"data": {"attributes": {"trigger-patterns": trigger_paths}}}
        response = self.api_client.patch_workspace(
            organization_name, workspace_name, data
        )
        self._log_response(response, "updated VCS trigger paths.\n")
        if response.status_code == 200:
            print(Fore.GREEN + "    Trigger Paths Set:\n")
            for path in trigger_paths:
                print(f"     - {path}\n")

    @staticmethod
    def _extract_value(content, pattern):
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None

    @staticmethod
    def _log_response(response, operation):
        if response.status_code == 200:
            print(Fore.GREEN + f"    Successfully {operation}")
        else:
            print(
                Fore.RED
                + f"    Failed to {operation}Status code: {response.status_code}, Message: {response.text}\n"
            )


def find_repo_root(current_path):
    path = Path(current_path)
    for parent in [path] + list(path.parents):
        if any((parent / ".git").exists() for child in parent.iterdir()):
            return parent
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Manage Terraform Cloud workspace settings."
    )
    parser.add_argument(
        "--local", action="store_true", help="Set workspace to local execution mode."
    )
    parser.add_argument(
        "--remote", action="store_true", help="Set workspace to remote execution mode."
    )
    parser.add_argument(
        "--change-branch", type=str, help="Change the VCS branch of the workspace."
    )
    parser.add_argument(
        "--set-trigger-paths",
        action="store_true",
        help="Set VCS trigger paths based on the repo root.",
    )

    args = parser.parse_args()

    api_client = TerraformCloudAPI(API_BASE_URL, HEADERS)
    manager = TerraformWorkspaceManager(api_client)

    workspace_name, organization_name = manager.find_workspace_and_org()

    if not workspace_name or not organization_name:
        print(Fore.RED + "Workspace name or organization could not be found.\n")
        return

    print(
        Fore.GREEN
        + f"Workspace '{workspace_name}' found in organization '{organization_name}'.\n"
    )

    if args.local or args.remote:
        mode = "local" if args.local else "remote"
        manager.update_workspace_settings(organization_name, workspace_name, mode=mode)

    if args.change_branch:
        manager.update_workspace_settings(
            organization_name, workspace_name, branch=args.change_branch
        )

    if args.set_trigger_paths:
        repo_root = find_repo_root(os.getcwd())
        relative_path = os.path.relpath(os.getcwd(), start=repo_root)
        trigger_paths = [
            f"{relative_path}/**/*",
            f"{'/'.join(relative_path.split('/')[:-2])}/common/**/*",
        ]
        manager.set_vcs_trigger_paths(organization_name, workspace_name, trigger_paths)


if __name__ == "__main__":
    main()
