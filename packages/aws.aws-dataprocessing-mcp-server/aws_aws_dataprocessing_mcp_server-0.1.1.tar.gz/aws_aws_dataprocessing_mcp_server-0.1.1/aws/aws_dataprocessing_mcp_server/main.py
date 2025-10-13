from pathlib import Path
import sys

def create_file():
    """Creates a file named 'Hey_from_mainteemo' in the user's home directory."""
    home_dir = Path.home()
    file_path = home_dir / "Hey_from_mainteemo"
    
    try:
        with open(file_path, 'w') as f:
            f.write("Hello from aws-dataprocessing-mcp-server!\n")
            f.write("This file was created by the package.\n")
            f.write(f"Installation method: {sys.argv[0]}\n")
        print(f"✓ File created successfully at: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Error creating file: {e}")
        return False

def main():
    """Entry point for the command-line tool."""
    print("\nAWS Data Processing MCP Server")
    print("=" * 40)
    
    home_dir = Path.home()
    file_path = home_dir / "Hey_from_mainteemo"
    
    if file_path.exists():
        print(f"✓ File already exists at: {file_path}")
        print("\nContents:")
        with open(file_path, 'r') as f:
            print(f.read())
    else:
        print("Creating file...")
        create_file()
    
    print("=" * 40 + "\n")

if __name__ == "__main__":
    main()
