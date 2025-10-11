import sys

def is_terminal():
    """Check if stdout is a terminal (not piped)"""
    return sys.stdout.isatty()

# Initialize colors based on terminal
if is_terminal():
    VAR_COLOR = '\033[1;36m'  # Bright cyan
    RESET = '\033[0m'         # Reset color
else:
    VAR_COLOR = ''
    RESET = ''

def handle_conn_command(args, guacdb):
    command_handlers = {
        'new': handle_conn_new,
        'list': handle_conn_list,
        'del': handle_conn_delete,
        'exists': handle_conn_exists,
        'modify': handle_conn_modify,
    }
    
    handler = command_handlers.get(args.conn_command)
    if handler:
        handler(args, guacdb)
    else:
        print(f"Unknown connection command: {args.conn_command}")
        sys.exit(1)

"""
def handle_conn_list(args, guacdb):
    # Get connections with both groups and parent group info
    connections = guacdb.list_connections_with_conngroups_and_parents()
    print("connections:")
    for conn in connections:
        name, protocol, host, port, groups, parent = conn
        print(f"  {name}:")
        print(f"    type: {protocol}")
        print(f"    hostname: {host}")
        print(f"    port: {port}")
        if parent:
            print(f"    parent: {parent}")
        print("    groups:")
        for group in (groups.split(',') if groups else []):
            print(f"      - {group}")
"""

def handle_conn_list(args, guacdb):
    # Check if specific ID is requested
    if hasattr(args, 'id') and args.id:
        # Get specific connection by ID
        connection = guacdb.get_connection_by_id(args.id)
        if not connection:
            print(f"Connection with ID {args.id} not found")
            sys.exit(1)
        connections = [connection]
    else:
        # Get all connections
        connections = guacdb.list_connections_with_conngroups_and_parents()
    
    print("connections:")
    for conn in connections:
        # Unpack connection info (now includes connection_id)
        conn_id, name, protocol, host, port, groups, parent, user_permissions = conn
            
        print(f"  {name}:")
        print(f"    id: {conn_id}")
        print(f"    type: {protocol}")
        print(f"    hostname: {host}")
        print(f"    port: {port}")
        if parent:
            print(f"    parent: {parent}")
        print("    groups:")
        for group in (groups.split(',') if groups else []):
            if group:  # Skip empty group names
                print(f"      - {group}")
        
        # Add this section to show individual user permissions
        if user_permissions:
            print("    permissions:")
            for user in user_permissions:
                print(f"      - {user}")

def handle_conn_new(args, guacdb):
    try:
        connection_id = None
        
        connection_id = guacdb.create_connection(
            args.type,
            args.name,
            args.hostname,
            args.port,
            args.password
        )
        guacdb.debug_print(f"Successfully created connection '{args.name}'")
            
        if connection_id and args.usergroup:
            groups = [g.strip() for g in args.usergroup.split(',')]
            success = True
            
            for group in groups:
                try:
                    guacdb.grant_connection_permission(
                        group,  # Direct group name
                        'USER_GROUP', 
                        connection_id,
                        group_path=None  # No path nesting
                    )
                    guacdb.debug_print(f"Granted access to group '{group}'")
                except Exception as e:
                    print(f"[-] Failed to grant access to group '{group}': {e}")
                    success = False
            
            if not success:
                raise RuntimeError("Failed to grant access to one or more groups")
        
    except Exception as e:
        print(f"Error creating connection: {e}")
        sys.exit(1)

def handle_conn_delete(args, guacdb):
    # Validate exactly one selector provided
    from .cli import validate_selector
    validate_selector(args, "connection")
    
    try:
        if hasattr(args, 'id') and args.id is not None:
            # Delete by ID using resolver
            guacdb.delete_existing_connection(connection_id=args.id)
        else:
            # Delete by name using resolver
            guacdb.delete_existing_connection(connection_name=args.name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error deleting connection: {e}")
        sys.exit(1)

def handle_conn_exists(args, guacdb):
    # Validate exactly one selector provided
    from .cli import validate_selector
    validate_selector(args, "connection")
    
    try:
        if hasattr(args, 'id') and args.id is not None:
            # Check existence by ID using resolver
            if guacdb.connection_exists(connection_id=args.id):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # Check existence by name using resolver
            if guacdb.connection_exists(connection_name=args.name):
                sys.exit(0)
            else:
                sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error checking connection existence: {e}")
        sys.exit(1)
        
def handle_conn_modify(args, guacdb):
    """Handle the connection modify command"""
    # Check if no modification options provided - show help
    if (not args.set and args.parent is None and not args.permit and not args.deny):
        # Print help information about modifiable parameters
        print("Usage: guacaman conn modify {--name <connection_name> | --id <connection_id>} [--set <param=value> ...] [--parent CONNGROUP] [--permit USERNAME] [--deny USERNAME]")
        print("\nModification options:")
        print(f"  {VAR_COLOR}--set{RESET}: Modify connection parameters")
        print(f"  {VAR_COLOR}--parent{RESET}: Set parent connection group (use empty string to remove group)")
        print("\nModifiable connection parameters:")
        for param, info in sorted(guacdb.CONNECTION_PARAMETERS.items()):
            if info['table'] == 'connection':
                desc = f"  {VAR_COLOR}{param}{RESET}: {info['description']} (type: {info['type']}, default: {info['default']})"
                if 'ref' in info:
                    if is_terminal():
                        desc += f"\n    Reference: \033[4m{info['ref']}\033[0m"
                    else:
                        desc += f"\n    Reference: {info['ref']}"
                print(desc)
        
        print("\nParameters in guacamole_connection_parameter table:")
        for param, info in sorted(guacdb.CONNECTION_PARAMETERS.items()):
            if info['table'] == 'parameter':
                desc = f"  {VAR_COLOR}{param}{RESET}: {info['description']} (type: {info['type']}, default: {info['default']})"
                if 'ref' in info:
                    if is_terminal():
                        desc += f"\n    Reference: \033[4m{info['ref']}\033[0m"
                    else:
                        desc += f"\n    Reference: {info['ref']}"
                print(desc)
        
        sys.exit(1)
    
    # Validate exactly one selector provided
    from .cli import validate_selector
    validate_selector(args, "connection")
    
    try:
        # Get connection name for display purposes (resolvers handle the actual lookup)
        if hasattr(args, 'id') and args.id is not None:
            # For ID-based operations, get name for display
            connection_name = guacdb.get_connection_name_by_id(args.id)
            if not connection_name:
                print(f"Error: Connection with ID {args.id} not found")
                sys.exit(1)
        else:
            connection_name = args.name
        
        guacdb.debug_connection_permissions(connection_name)
        
        # Handle permission modifications (these methods expect connection_name)
        if args.permit:
            guacdb.grant_connection_permission_to_user(args.permit, connection_name)
            print(f"Successfully granted permission to user '{args.permit}' for connection '{connection_name}'")
            guacdb.debug_connection_permissions(connection_name)
            
        if args.deny:
            guacdb.revoke_connection_permission_from_user(args.deny, connection_name)
            print(f"Successfully revoked permission from user '{args.deny}' for connection '{connection_name}'")

        # Handle parent group modification using resolver
        if args.parent is not None:
            try:
                # Convert empty string to None to unset parent group
                parent_group = args.parent if args.parent != "" else None
                if hasattr(args, 'id') and args.id is not None:
                    guacdb.modify_connection_parent_group(connection_id=args.id, group_name=parent_group)
                else:
                    guacdb.modify_connection_parent_group(connection_name=args.name, group_name=parent_group)
                print(f"Successfully set parent group to '{args.parent}' for connection '{connection_name}'")
            except Exception as e:
                print(f"Error setting parent group: {e}")
                sys.exit(1)
                
        # Process each --set argument (if any) using resolver
        for param_value in args.set or []:
            if '=' not in param_value:
                print(f"Error: Invalid format for --set. Must be param=value, got: {param_value}")
                sys.exit(1)
                
            param, value = param_value.split('=', 1)
            guacdb.debug_print(f"Modifying connection '{connection_name}': setting {param}={value}")
            
            try:
                if hasattr(args, 'id') and args.id is not None:
                    guacdb.modify_connection(connection_id=args.id, param_name=param, param_value=value)
                else:
                    guacdb.modify_connection(connection_name=args.name, param_name=param, param_value=value)
                print(f"Successfully updated {param} for connection '{connection_name}'")
            except ValueError as e:
                print(f"Error: {str(e)}")
                sys.exit(1)
                
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error modifying connection: {e}")
        sys.exit(1)
