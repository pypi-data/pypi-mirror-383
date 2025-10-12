"""
airobo/cli.py

CLI for the airobo tool.
"""
import argparse
from airobo.api import publish, version

commands = {
    "publish": publish,
    "version": version,
}


#---------------------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog='airobo')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Dynamically create subparsers for each command in the commands dictionary
    for command_name in commands.keys():
        subparsers.add_parser(command_name, help=f'Run {command_name} command')

    args = parser.parse_args()

    # Iterate through commands dictionary to find matching key and execute callback
    if args.command in commands:
        callback = commands[args.command]
        callback()
    else:
        parser.print_help()

#---------------------------------------

if __name__ == "__main__":
    main()