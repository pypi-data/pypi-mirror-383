from . import greet, get_author, get_project_name, get_version

def main():
    print("=== Project Info ===")
    print(f"Project Name: {get_project_name()}")
    print(f"Version: {get_version()}")
    print(f"Author: {get_author()}")
    print("\n=== Greet Example ===")
    print(greet("Victor"))

if __name__ == "__main__":
    main()
