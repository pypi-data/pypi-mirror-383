# Copyright 2025 Siby Jose
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from enum import Enum
from botocore.exceptions import BotoCoreError, ClientError

from .inventory import (
    make_boto3_session,
    list_running_instances,
    list_rds_instances,
    filter_instances_by_keywords
)
from .gateway import (
    validate_key_permissions,
    start_ssm_session,
    start_ssh_session,
    start_port_forwarding_to_rds
)

CONFIG_DIR = Path.home() / ".ssm-connect"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_ssh_defaults() -> Optional[dict]:
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('ssh')
    except Exception:
        return None


def save_ssh_defaults(key_path: str, username: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {'ssh': {'key_path': key_path, 'username': username}}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    if os.name != 'nt':
        os.chmod(CONFIG_FILE, 0o600)


def reset_ssh_defaults():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("✓ SSH config reset.")
    else:
        print("No saved SSH config found.")

class TargetType(Enum):
    EC2 = "ec2"
    RDS = "rds"


class ConnectionType(Enum):
    SSM = "ssm"
    SSH = "ssh"

def choose_target_type() -> Optional[TargetType]:
    print("\nWhat do you want to connect to?")
    print("[1] EC2")
    print("[2] RDS")
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            return TargetType.EC2
        elif choice == "2":
            return TargetType.RDS
        else:
            return None
    except (ValueError, KeyboardInterrupt):
        return None


def choose_ec2_connection_type() -> Optional[ConnectionType]:
    print("\nSelect Connection Type:")
    print("[1] SSM")
    print("[2] SSH over SSM")
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            return ConnectionType.SSM
        elif choice == "2":
            return ConnectionType.SSH
        else:
            return None
    except (ValueError, KeyboardInterrupt):
        return None


def prompt_for_keywords() -> Optional[List[str]]:
    raw = input("\n(Optional) Enter keywords to filter instances (or press ENTER to list all): ").strip()
    if not raw:
        return None
    return [s.lower() for s in raw.replace(',', ' ').split() if s.strip()]


def choose_instance(instances: List[Dict[str, str]], purpose: str = "connect to") -> Optional[str]:
    if not instances:
        return None
    print(f"\nSelect an EC2 Instance to {purpose}:")
    for idx, inst in enumerate(instances, start=1):
        print(f"[{idx}] {inst['Name']} ({inst['InstanceId']})")
    print("[0] Exit / Refine Search")
    try:
        raw_choice = input("\nEnter the number of the instance: ").strip()
        if raw_choice == "0":
            return "RETRY"
        choice_idx = int(raw_choice) - 1
        if 0 <= choice_idx < len(instances):
            return instances[choice_idx]["InstanceId"]
    except (ValueError, IndexError):
        return None
    return None


def choose_rds_instance(instances: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    if not instances:
        print("No available RDS instances found.")
        return None
    print("\n=== Step 2: Select target RDS instance ===")
    for idx, db in enumerate(instances, start=1):
        print(f"[{idx}] {db['DBInstanceIdentifier']} ({db['Engine']})")
    print("[0] Exit")
    try:
        choice = input("\nEnter the number of the RDS instance: ").strip()
        if choice == "0":
            return None
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(instances):
            return instances[choice_idx]
    except (ValueError, IndexError):
        return None
    return None


def prompt_for_ssh_details() -> Optional[Tuple[str, Path]]:
    saved = load_ssh_defaults()
    if saved:
        key_path_str = saved['key_path']
        username = saved['username']
        key_path = Path(key_path_str).expanduser()
        if key_path.is_file():
            print("\nUse saved SSH settings?")
            print(f"  Key: {key_path_str}")
            print(f"  User: {username}")
            use_saved = input("[Y/n]: ").strip().lower()
            if use_saved in ('', 'y', 'yes'):
                return username, key_path
            print("\nEnter new SSH details:")
        else:
            print(f"\nWarning: Saved key not found at {key_path_str}. Please enter new SSH details:")

    key_path_str = input("\nEnter the path to your private key file: ").strip()
    if not key_path_str:
        print("Error: Private key path cannot be empty.", file=sys.stderr)
        return None

    key_path = Path(key_path_str.strip('"\'').strip()).expanduser()
    if not key_path.is_file():
        print(f"Error: Private key file not found at '{key_path}'", file=sys.stderr)
        return None

    if not validate_key_permissions(key_path):
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return None

    username = input("Enter SSH username (e.g., ec2-user, ubuntu): ").strip()
    if not username:
        print("Error: Username cannot be empty.", file=sys.stderr)
        return None

    save = input("\nSave these settings for next time? [Y/n]: ").strip().lower()
    if save not in ('n', 'no'):
        try:
            save_ssh_defaults(str(key_path), username)
            print("✓ Settings saved")
        except Exception as e:
            print(f"Warning: Could not save settings: {e}", file=sys.stderr)

    return username, key_path


def select_ec2_instance(all_instances: List[Dict[str, str]], purpose: str = "connect to") -> Optional[str]:
    instance_id = None
    
    while not instance_id:
        keywords = prompt_for_keywords()
        filtered_instances = filter_instances_by_keywords(all_instances, keywords)
        
        if not filtered_instances:
            print("No instances found matching your keywords. Please try again.")
            continue
        
        selection = choose_instance(filtered_instances, purpose)
        if selection is None:
            print("Invalid selection. Please try again.", file=sys.stderr)
            continue
        elif selection == "RETRY":
            continue
        else:
            instance_id = selection
    
    return instance_id


def ask_continue_or_exit():
    choice = input("\nWould you like to open another session? [Y/n]: ").strip().lower()
    return choice != 'n' and choice != 'no'

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--reset-config":
        reset_ssh_defaults()
        sys.exit(0)
    
    try:
        session = make_boto3_session()
        all_instances = list_running_instances(session)
    except (BotoCoreError, ClientError) as e:
        print(f"AWS API Error: Failed to list instances: {e}", file=sys.stderr)
        print("\nTip: Ensure your AWS credentials are configured correctly.", file=sys.stderr)
        sys.exit(1)
    
    if not all_instances:
        print(f"No running EC2 instances found in region '{session.region_name}'.")
        sys.exit(0)
    
    print(f"Found {len(all_instances)} running EC2 instances in region '{session.region_name}'.")
    
    while True:
        target_type = choose_target_type()
        if not target_type:
            print("Invalid selection. Exiting.", file=sys.stderr)
            sys.exit(1)
        
        if target_type == TargetType.EC2:
            connection_type = choose_ec2_connection_type()
            if not connection_type:
                print("Invalid connection type.")
                continue
            
            if connection_type == ConnectionType.SSM:
                instance_id = select_ec2_instance(all_instances, "connect to")
                if instance_id:
                    start_ssm_session(instance_id, session)
            
            elif connection_type == ConnectionType.SSH:
                instance_id = select_ec2_instance(all_instances, "connect to")
                if not instance_id:
                    print("No instance selected.")
                    continue
                
                ssh_details = prompt_for_ssh_details()
                if not ssh_details:
                    print("Failed to get SSH details.")
                    continue
                username, key_path = ssh_details
                
                start_ssh_session(instance_id, username, key_path, session)
        
        elif target_type == TargetType.RDS:
            print("\n=== Step 1: Select the EC2 instance acting as a bastion ===")
            bastion_id = select_ec2_instance(all_instances, "use as bastion")
            if not bastion_id:
                print("No bastion instance selected.")
                continue
            
            try:
                rds_instances = list_rds_instances(session)
                if not rds_instances:
                    print("No available RDS instances found in this region.")
                    continue
                
                selected_rds = choose_rds_instance(rds_instances)
                if not selected_rds:
                    print("No RDS instance selected.")
                    continue
                
                start_port_forwarding_to_rds(bastion_id, selected_rds, session)
            except Exception as e:
                print(f"Error setting up RDS port forwarding: {e}", file=sys.stderr)
                continue
        
        if not ask_continue_or_exit():
            break
    
    print("Goodbye!")


if __name__ == "__main__":
    main()
