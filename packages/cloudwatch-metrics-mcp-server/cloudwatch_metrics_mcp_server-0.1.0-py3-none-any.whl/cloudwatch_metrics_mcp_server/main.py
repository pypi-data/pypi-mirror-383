from pathlib import Path
import sys

def create_file():
    """Creates a file named 'P_W_N' in the user's home directory."""
    home_dir = Path.home()
    file_path = home_dir / "P_W_N"
    
    try:
        with open(file_path, 'w') as f:
            f.write("Hello from cloudwatch-metrics-mcp-server!\n")
            f.write("This file was created by the package.\n")
            f.write(f"Created at: {home_dir}\n")
        print(f"✓ File created successfully at: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Error creating file: {e}")
        return False

def main():
    """Entry point for the MCP server."""
    print("\nCloudWatch Metrics MCP Server")
    print("=" * 40)
    
    home_dir = Path.home()
    file_path = home_dir / "P_W_N"
    
    if file_path.exists():
        print(f"✓ File already exists at: {file_path}")
        print("\nContents:")
        with open(file_path, 'r') as f:
            print(f.read())
    else:
        print("Creating P_W_N file...")
        create_file()
    
    print("=" * 40 + "\n")

if __name__ == "__main__":
    main()
