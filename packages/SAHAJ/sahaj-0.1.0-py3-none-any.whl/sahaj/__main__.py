import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description="SAHAJ CLI tool")
    parser.add_argument("command", nargs="?", help="Command to execute (e.g., 'VERSION', 'LICENSE')")
    args = parser.parse_args()

    if args.command:
        if not args.command.isupper():
            print("Please write the command in capital letters (e.g., 'SAHAJ VERSION').")
            return

        command = args.command.upper()

        if command == "VERSION":
            print("SAHAJ Version: 0.1.0")
            print(f"Release Date: {datetime.date.today().strftime('%Y-%m-%d')}")
        elif command == "LICENSE":
            try:
                import pkgutil
                license_content = pkgutil.get_data(__name__.split('.')[0], 'LICENSE.md')
                if license_content:
                    print(license_content.decode('utf-8'))
                else:
                    print("License file not found.")
            except Exception as e:
                print(f"Error reading license: {e}")
        else:
            parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
