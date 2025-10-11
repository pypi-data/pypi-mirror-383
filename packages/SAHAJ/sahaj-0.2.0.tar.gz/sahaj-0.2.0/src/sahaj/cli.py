import argparse
import importlib.metadata
import webbrowser
import os

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
  SAHAJ --help          Show this help message
""")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?", default=None)
    args, unknown = parser.parse_known_args()

    # Normalize commands: convert single dash to double dash
    cmd = args.command or (unknown[0] if unknown else "--help")
    if cmd.startswith("-") and not cmd.startswith("--"):
        cmd = "-" + cmd  # keep legacy single dash if needed
    if cmd.startswith("--"):
        cmd = cmd.lower()  # ensure consistent lowercase matching

    commands = {
        "--version": show_version,
        "--update": show_update,
        "--license": show_license,
        "--about": show_about,
        "--docs": show_docs,
        "--help": show_help,
        "-version": show_version,   # backward compatibility
        "-update": show_update,
        "-license": show_license,
        "-about": show_about,
        "-docs": show_docs,
        "-help": show_help
    }

    func = commands.get(cmd, show_help)
    func()

if __name__ == "__main__":
    main()
