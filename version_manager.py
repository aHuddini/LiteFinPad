"""
LiteFinPad Version Manager
Handles version reading, incrementing, and validation
"""
import os
import re
from typing import Tuple, Optional

VERSION_FILE = "version.txt"
BACKUP_VERSION_FILE = "version.txt.backup"
README_FILE = "README.txt"


def read_version() -> str:
    """Read current version from version.txt"""
    if not os.path.exists(VERSION_FILE):
        # Create default version file
        write_version("3.0")
        return "3.0"
    
    try:
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            version = f.read().strip()
            if not version:
                return "3.0"
            return version
    except Exception as e:
        print(f"[ERROR] Failed to read version: {e}")
        return "3.0"


def update_readme_version(version: str) -> bool:
    """Update version number in README.txt file"""
    if not os.path.exists(README_FILE):
        # README.txt doesn't exist, skip update
        return True
    
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update version line (matches "Version: X.Y.Z" or "Version: X.Y")
        # Pattern matches: Version: followed by version number
        pattern = r'(Version:\s*)(\d+\.\d+(?:\.\d+)?)'
        replacement = r'\1' + version
        
        updated_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if updated_content != content:
            with open(README_FILE, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        else:
            # Version not found or already correct
            return True
    except Exception as e:
        print(f"[WARNING] Failed to update README.txt version: {e}")
        # Don't fail the build if README update fails
        return True


def write_version(version: str) -> bool:
    """Write version to version.txt with backup and update README.txt"""
    try:
        # Create backup if file exists
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                old_version = f.read().strip()
            with open(BACKUP_VERSION_FILE, 'w', encoding='utf-8') as f:
                f.write(old_version)
        
        # Write new version
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            f.write(version)
        
        # Update README.txt version
        update_readme_version(version)
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write version: {e}")
        return False


def parse_version(version: str) -> Tuple[int, int]:
    """
    Parse version string into major and minor components
    Supports: "3.0", "3.1", "3.0.1" (treats as 3.0)
    Returns: (major, minor)
    """
    try:
        # Remove any whitespace
        version = version.strip()
        
        # Match version pattern (e.g., "3.0" or "3.1")
        match = re.match(r'^(\d+)\.(\d+)', version)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            return (major, minor)
        
        # If just a single number (e.g., "3"), treat as "3.0"
        if version.isdigit():
            return (int(version), 0)
        
        print(f"[WARNING] Invalid version format: {version}")
        return (3, 0)
    except Exception as e:
        print(f"[ERROR] Failed to parse version: {e}")
        return (3, 0)


def increment_version(version: str, increment_type: str = "minor") -> str:
    """
    Increment version number
    
    Args:
        version: Current version (e.g., "3.0")
        increment_type: "major" or "minor" (default: "minor")
    
    Returns:
        New version string (e.g., "3.1" or "4.0")
    """
    major, minor = parse_version(version)
    
    if increment_type == "major":
        # Increment major, reset minor
        major += 1
        minor = 0
    else:  # minor
        # Increment minor
        minor += 1
    
    return f"{major}.{minor}"


def validate_version(version: str) -> bool:
    """Validate version string format"""
    try:
        major, minor = parse_version(version)
        # Check if parsing succeeded and values are reasonable
        return major >= 0 and minor >= 0 and major < 100 and minor < 100
    except:
        return False


def get_next_dev_version(base_version: str) -> str:
    """
    Get next development version
    For development builds, we increment the minor version
    Example: 3.0 -> 3.1, 3.1 -> 3.2
    """
    return increment_version(base_version, "minor")


def get_next_release_version(base_version: str) -> str:
    """
    Get next release version
    For releases, we increment the major version
    Example: 3.0 -> 4.0, 3.5 -> 4.0
    """
    return increment_version(base_version, "major")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python version_manager.py read              - Read current version")
        print("  python version_manager.py increment [type]  - Increment version (type: minor/major)")
        print("  python version_manager.py set <version>     - Set specific version")
        print("  python version_manager.py validate <version> - Validate version format")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "read":
        version = read_version()
        print(version)
    
    elif command == "increment":
        increment_type = sys.argv[2] if len(sys.argv) > 2 else "minor"
        current = read_version()
        new_version = increment_version(current, increment_type)
        if write_version(new_version):
            print(new_version)
        else:
            print(f"[ERROR] Failed to increment version")
            sys.exit(1)
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("[ERROR] Version number required")
            sys.exit(1)
        new_version = sys.argv[2]
        if not validate_version(new_version):
            print(f"[ERROR] Invalid version format: {new_version}")
            sys.exit(1)
        if write_version(new_version):
            print(f"[SUCCESS] Version set to {new_version}")
        else:
            print(f"[ERROR] Failed to set version")
            sys.exit(1)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("[ERROR] Version number required")
            sys.exit(1)
        version = sys.argv[2]
        if validate_version(version):
            print(f"[VALID] {version}")
        else:
            print(f"[INVALID] {version}")
            sys.exit(1)
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)

