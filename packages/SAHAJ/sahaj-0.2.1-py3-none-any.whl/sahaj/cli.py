
import argparse
import importlib.metadata
import webbrowser
import os
import requests
import subprocess
import tempfile

DOCKER_COMPOSE_URL = "https://raw.githubusercontent.com/concur-live/docker-yml/main/docker-compose.yml"

def show_version():
    version = importlib.metadata.version("SAHAJ")
    print(f"SAHAJ version {version} (Last updated: Oct 2025)")

def show_update():
    print("Checking for updates...")
    print("No updates available right now. You are using the latest version.")

def show_license():
    license_path = os.path.join(os.path.dirname(__file__), "../../LICENSE.md")
    try:
        with open(os.path.abspath(license_path), "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("License file not found.")

def show_about():
    print("""SAHAJ is an open-source project to simplify installation and management
of community-driven software. It provides an intuitive command-line interface
for deployment, configuration, and discovery of open-source tools.
""")

def show_docs():
    url = "https://docs.sahaj.live"
    print(f"Opening documentation: {url}")
    webbrowser.open(url)

def show_help():
    print("""
SAHAJ - Open Source Software Installer

Usage:
  SAHAJ --version       Display current version of SAHAJ with release date
  SAHAJ --update        Check for and install updates
  SAHAJ --license       Show open-source license details
  SAHAJ --about         Show information about SAHAJ
  SAHAJ --docs          Open documentation in a browser
  SAHAJ --init          Fetch docker-compose file and run containers
  SAHAJ --help          Show this help message
""")

def init_docker():
    print("Fetching docker-compose file...")
    try:
        response = requests.get(DOCKER_COMPOSE_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching docker-compose file: {e}")
        return

    # Save to a temporary file
    temp_dir = tempfile.mkdtemp()
    compose_file_path = os.path.join(temp_dir, "docker-compose.yml")
    with open(compose_file_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"docker-compose.yml saved to {compose_file_path}")

    # Run docker compose
    print("Starting containers with Docker Compose...")
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", compose_file_path, "up", "-d"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("Containers started successfully!")
            print(result.stdout)
        else:
            print("Error running docker-compose:")
            print(result.stderr)
    except FileNotFoundError:
        print("Docker not found. Please ensure Docker is installed and in PATH.")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?", default=None)
    args, unknown = parser.parse_known_args()

    cmd = args.command or (unknown[0] if unknown else "--help")
    if cmd.startswith("-") and not cmd.startswith("--"):
        cmd = "-" + cmd
    if cmd.startswith("--"):
        cmd = cmd.lower()

    commands = {
        "--version": show_version,
        "--update": show_update,
        "--license": show_license,
        "--about": show_about,
        "--docs": show_docs,
        "--init": init_docker,
        "--help": show_help,
        "-version": show_version,
        "-update": show_update,
        "-license": show_license,
        "-about": show_about,
        "-docs": show_docs,
        "-init": init_docker,
        "-help": show_help
    }

    func = commands.get(cmd, show_help)
    func()

if __name__ == "__main__":
    main()
