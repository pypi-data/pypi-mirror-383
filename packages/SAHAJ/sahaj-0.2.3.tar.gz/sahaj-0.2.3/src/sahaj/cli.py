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
  SAHAJ --list          List all available open-source modules supported by SAHAJ
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

    # Run docker compose with live output
    print("Starting containers with Docker Compose...\n")
    try:
        process = subprocess.Popen(
            ["docker", "compose", "-f", compose_file_path, "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.strip())

        process.stdout.close()
        return_code = process.wait()
        if return_code == 0:
            print("\nContainers started successfully!")
        else:
            print("\nDocker Compose finished with errors.")
    except FileNotFoundError:
        print("Docker not found. Please ensure Docker is installed and in PATH.")

def list_modules():
    modules = [
        "Organization Management – Configure organizational hierarchy, departments, users, and access controls for compliance operations.",
        "Cookie Consent – Automatically scan websites and manage cookie consent to ensure DPDPA compliance.",
        "Data Principal Management – Maintain records and lifecycle of both legacy and new data principals for compliance tracking.",
        "Data Element – Identify, ingest, and classify PII data elements across systems for compliance monitoring.",
        "Purpose Management – Define, manage, and publish data processing purposes aligned with DPDPA consent requirements.",
        "Notice Orchestration – Create and manage Data Principal Notices for transparent data collection and consent communication.",
        "Collection Point – Configure and manage all data collection sources including web, mobile, and offline channels.",
        "Consent Governance – Monitor, search, and administer collected consents aligned with business and legal objectives.",
        "Consent Validation – Validate consent records, scope, and artifacts to ensure lawful and compliant data processing.",
        "Legacy Notice – Collect and regularize consents from existing data principals as mandated under Section 5(2).",
        "Grievance – Track, manage, and resolve data principal grievances in line with BRD-CMS compliance standards.",
        "Data Principal Rights – Handle and fulfill Data Principal access and rights requests efficiently.",
        "Breach Management – Log, assess, and report data breaches, ensuring timely notification to authorities and data principals.",
        "Assets/SKU – Maintain and manage organizational assets, SKUs, and their linkage to consent and cookie compliance activities.",
        "Customer Portal – Deploy a self-service Data Principal portal for managing consents and exercising privacy rights."
    ]

    # Display in table format
    print(f"{'No.':<4} {'Module':<25} Description")
    print("-" * 100)
    for i, module in enumerate(modules, start=1):
        if "–" in module:
            name, desc = module.split("–", 1)
        else:
            name, desc = module, ""
        print(f"{i:<4} {name.strip():<25} {desc.strip()}")

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
        "--list": list_modules,
        "--help": show_help,
        "-version": show_version,
        "-update": show_update,
        "-license": show_license,
        "-about": show_about,
        "-docs": show_docs,
        "-init": init_docker,
        "-list": list_modules,
        "-help": show_help
    }

    func = commands.get(cmd, show_help)
    func()

if __name__ == "__main__":
    main()
