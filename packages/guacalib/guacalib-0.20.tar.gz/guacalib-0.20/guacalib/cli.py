#!/usr/bin/env python3

import argparse
import os
import sys
from guacalib import GuacamoleDB
from guacalib.cli_handle_usergroup import handle_usergroup_command
from guacalib.cli_handle_dump import handle_dump_command
from guacalib.cli_handle_user import handle_user_command
from guacalib.cli_handle_conn import handle_conn_command
from guacalib.cli_handle_conngroup import handle_conngroup_command

def positive_int(value):
    """Convert to integer and validate that it is positive"""
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue

def validate_selector(args, entity_type="connection"):
    """Validate exactly one of name or id is provided and validate ID format"""
    has_name = hasattr(args, 'name') and args.name is not None
    has_id = hasattr(args, 'id') and args.id is not None
    
    if not (has_name ^ has_id):
        print(f"Error: Exactly one of --name or --id must be provided for {entity_type}")
        sys.exit(1)
    
    # Validate ID format if ID is provided
    if has_id and args.id <= 0:
        print(f"Error: {entity_type.capitalize()} ID must be a positive integer greater than 0")
        sys.exit(1)

def setup_user_subcommands(subparsers):
    user_parser = subparsers.add_parser('user', help='Manage Guacamole users')
    user_subparsers = user_parser.add_subparsers(dest='user_command', help='User commands')

    # User new command
    new_user = user_subparsers.add_parser('new', help='Create a new user')
    new_user.add_argument('--name', required=True, help='Username for Guacamole')
    new_user.add_argument('--password', required=True, help='Password for Guacamole user')
    new_user.add_argument('--usergroup', help='Comma-separated list of user groups to add user to')

    # User list command
    user_subparsers.add_parser('list', help='List all users')

    # User exists command
    exists_user = user_subparsers.add_parser('exists', help='Check if a user exists')
    exists_user.add_argument('--name', required=True, help='Username to check')

    # User delete command
    del_user = user_subparsers.add_parser('del', help='Delete a user')
    del_user.add_argument('--name', required=True, help='Username to delete')
    
    # User modify command
    modify_user = user_subparsers.add_parser('modify', help='Modify user parameters')
    modify_user.add_argument('--name', help='Username to modify')
    modify_user.add_argument('--set', help='Parameter to set in format param=value')
    modify_user.add_argument('--password', help='New password for the user')

def setup_usergroup_subcommands(subparsers):
    group_parser = subparsers.add_parser('usergroup', help='Manage Guacamole usergroups')
    usergroup_subparsers = group_parser.add_subparsers(dest='usergroup_command', help='Usergroup commands')

    # Group new command
    new_group = usergroup_subparsers.add_parser('new', help='Create a new usergroup')
    new_group.add_argument('--name', required=True, help='Usergroup name')

    # Group list command
    usergroup_subparsers.add_parser('list', help='List all usergroups')

    # Group exists command
    exists_group = usergroup_subparsers.add_parser('exists', help='Check if a usergroup exists. Exactly one of --name or --id must be provided.')
    exists_group_group = exists_group.add_mutually_exclusive_group(required=True)
    exists_group_group.add_argument('--name', help='Usergroup name to check')
    exists_group_group.add_argument('--id', type=int, help='Usergroup ID to check')

    # Group delete command
    del_group = usergroup_subparsers.add_parser('del', help='Delete a usergroup. Exactly one of --name or --id must be provided.')
    del_group_group = del_group.add_mutually_exclusive_group(required=True)
    del_group_group.add_argument('--name', help='Usergroup name to delete')
    del_group_group.add_argument('--id', type=int, help='Usergroup ID to delete')

    # Group modify command
    modify_group = usergroup_subparsers.add_parser('modify', help='Modify usergroup membership. Exactly one of --name or --id must be provided.')
    modify_group_group = modify_group.add_mutually_exclusive_group(required=True)
    modify_group_group.add_argument('--name', help='Usergroup name to modify')
    modify_group_group.add_argument('--id', type=int, help='Usergroup ID to modify')
    modify_group.add_argument('--adduser', help='Username to add to usergroup')
    modify_group.add_argument('--rmuser', help='Username to remove from usergroup')

def setup_conngroup_subcommands(subparsers):
    conngroup_parser = subparsers.add_parser('conngroup', help='Manage connection groups')
    conngroup_subparsers = conngroup_parser.add_subparsers(dest='conngroup_command', help='Connection group commands')

    # Conngroup new command
    new_conngroup = conngroup_subparsers.add_parser('new', help='Create a new connection group')
    new_conngroup.add_argument('--name', required=True, help='Connection group name')
    new_conngroup.add_argument('--parent', help='Parent connection group name (optional)')

    # Conngroup list command
    list_conngroup = conngroup_subparsers.add_parser('list', help='List all connection groups')
    list_conngroup.add_argument('--id', type=positive_int, help='Show connection group by specific ID')

    # Conngroup exists command
    exists_conngroup = conngroup_subparsers.add_parser('exists', help='Check if a connection group exists. Exactly one of --name or --id must be provided.')
    exists_conngroup_group = exists_conngroup.add_mutually_exclusive_group(required=True)
    exists_conngroup_group.add_argument('--name', help='Connection group name to check')
    exists_conngroup_group.add_argument('--id', type=int, help='Connection group ID to check')

    # Conngroup delete command
    del_conngroup = conngroup_subparsers.add_parser('del', help='Delete a connection group. Exactly one of --name or --id must be provided.')
    del_conngroup_group = del_conngroup.add_mutually_exclusive_group(required=True)
    del_conngroup_group.add_argument('--name', help='Connection group name to delete')
    del_conngroup_group.add_argument('--id', type=int, help='Connection group ID to delete')

    # Conngroup modify command
    modify_conngroup = conngroup_subparsers.add_parser('modify', help='Modify connection group. Exactly one of --name or --id must be provided.')
    modify_conngroup_group = modify_conngroup.add_mutually_exclusive_group(required=True)
    modify_conngroup_group.add_argument('--name', help='Connection group name to modify')
    modify_conngroup_group.add_argument('--id', type=int, help='Connection group ID to modify')

    # Add connection arguments (mutually exclusive with remove arguments)
    conn_modify_group = modify_conngroup.add_mutually_exclusive_group()
    conn_modify_group.add_argument('--addconn-by-name',
                                  help='Add connection by name to the target group')
    conn_modify_group.add_argument('--addconn-by-id', type=int,
                                  help='Add connection by ID to the target group')
    conn_modify_group.add_argument('--rmconn-by-name',
                                  help='Remove connection by name from the target group')
    conn_modify_group.add_argument('--rmconn-by-id', type=int,
                                  help='Remove connection by ID from the target group')

    modify_conngroup.add_argument('--parent',
                               help='Set parent connection group name (use empty string to unset parent group)')
    modify_conngroup.add_argument('--permit', metavar='USERNAME', action='append', nargs='?',
                               help='Grant permission to use connection group to specified user')
    modify_conngroup.add_argument('--deny', metavar='USERNAME', action='append', nargs='?',
                               help='Revoke permission to use connection group from specified user')

def setup_dump_subcommand(subparsers):
    subparsers.add_parser('dump', help='Dump all groups, users and connections in YAML format')

def setup_version_subcommand(subparsers):
    subparsers.add_parser('version', help='Show version information')

def setup_conn_subcommands(subparsers):
    conn_parser = subparsers.add_parser('conn', help='Manage connections')
    conn_subparsers = conn_parser.add_subparsers(dest='conn_command', help='Connection commands')

    # Connection new command
    new_conn = conn_subparsers.add_parser('new', help='Create a new connection')
    new_conn.add_argument('--name', required=True, help='Connection name')
    new_conn.add_argument('--type', choices=['vnc', 'rdp', 'ssh'], required=True, 
                         help='Type of connection (vnc, rdp, ssh)')
    new_conn.add_argument('--hostname', required=True, help='Server hostname/IP')
    new_conn.add_argument('--port', required=True, help='Server port')
    new_conn.add_argument('--password', help='Connection password')
    new_conn.add_argument('--usergroup', help='Comma-separated list of user groups to grant access to')

    # Connection list command
    list_conn = conn_subparsers.add_parser('list', help='List all connections')
    list_conn.add_argument('--id', type=positive_int, help='Show connection by specific ID')

    # Connection exists command
    exists_conn = conn_subparsers.add_parser('exists', help='Check if a connection exists. Exactly one of --name or --id must be provided.')
    exists_group = exists_conn.add_mutually_exclusive_group(required=True)
    exists_group.add_argument('--name', help='Connection name to check')
    exists_group.add_argument('--id', type=int, help='Connection ID to check')

    # Connection delete command
    del_conn = conn_subparsers.add_parser('del', help='Delete a connection. Exactly one of --name or --id must be provided.')
    del_group = del_conn.add_mutually_exclusive_group(required=True)
    del_group.add_argument('--name', help='Connection name to delete')
    del_group.add_argument('--id', type=int, help='Connection ID to delete')
    
    # Connection modify command
    modify_conn = conn_subparsers.add_parser('modify', help='Modify connection parameters. Exactly one of --name or --id must be provided.')
    modify_group = modify_conn.add_mutually_exclusive_group(required=True)
    modify_group.add_argument('--name', help='Connection name to modify')
    modify_group.add_argument('--id', type=int, help='Connection ID to modify')
    modify_conn.add_argument('--set', action='append', help='Parameter to set in format param=value (can be used multiple times)')
    modify_conn.add_argument('--parent', 
                           help='Set parent connection group name (use empty string to unset group)')
    modify_conn.add_argument('--permit',
                           help='Grant permission to use connection to specified user')
    modify_conn.add_argument('--deny',
                           help='Revoke permission to use connection from specified user')

def main():
    parser = argparse.ArgumentParser(description='Manage Guacamole users, groups, and connections')
    parser.add_argument('--config', 
                       default=os.path.expanduser('~/.guacaman.ini'), 
                       help='Path to database config file (default: ~/.guacaman.ini)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    setup_user_subcommands(subparsers)
    setup_usergroup_subcommands(subparsers)
    setup_conn_subcommands(subparsers)
    setup_dump_subcommand(subparsers)
    setup_version_subcommand(subparsers)
    setup_conngroup_subcommands(subparsers)

    args = parser.parse_args()

    def check_config_permissions(config_path):
        """Check config file has secure permissions"""
        if not os.path.exists(config_path):
            return  # Will be handled later by GuacamoleDB
            
        mode = os.stat(config_path).st_mode
        if mode & 0o077:  # Check if group/others have any permissions
            print(f"ERROR: Config file {config_path} has insecure permissions!")
            print("Required permissions: -rw------- (600)")
            print("Fix with: chmod 600", config_path)
            sys.exit(2)

    # Check permissions before doing anything
    check_config_permissions(args.config)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'user' and not args.user_command:
        subparsers.choices['user'].print_help()
        sys.exit(1)

    if args.command == 'usergroup' and not args.usergroup_command:
        subparsers.choices['usergroup'].print_help()
        sys.exit(1)
    if args.command == 'conn' and not args.conn_command:
        subparsers.choices['conn'].print_help()
        sys.exit(1)

    try:
        with GuacamoleDB(args.config, debug=args.debug) as guacdb:
            if args.command == 'user':
                handle_user_command(args, guacdb)

            elif args.command == 'usergroup':
                handle_usergroup_command(args, guacdb)

            elif args.command == 'dump':
                handle_dump_command(guacdb)

            elif args.command == 'version':
                from guacalib import VERSION
                print(f"guacaman version {VERSION}")
                
            elif args.command == 'conn':
                handle_conn_command(args, guacdb)
                
            elif args.command == 'conngroup':
                if not args.conngroup_command:
                    subparsers.choices['conngroup'].print_help()
                    sys.exit(1)
                handle_conngroup_command(args, guacdb)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
