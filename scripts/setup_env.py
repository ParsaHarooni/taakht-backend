#!/usr/bin/env python3
"""Environment setup script for Taakht backend.

This script helps users set up their environment by creating necessary
directories and copying environment configuration files.
"""

import shutil
from pathlib import Path


def create_env_file():
    """Create .env file from env.example if it doesn't exist."""
    env_example = Path("env.example")
    env_file = Path(".env")

    if not env_example.exists():
        print("❌ env.example file not found!")
        return False

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    try:
        shutil.copy2(env_example, env_file)
        print("✅ Created .env file from env.example")
        print("📝 Please edit .env file with your configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories for the application."""
    directories = ["logs", "uploads", "uploads/images", "uploads/temp"]

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
        else:
            print(f"✅ Directory already exists: {directory}")


def main():
    """Main setup function."""
    print("🚀 Setting up Taakht Backend environment...")
    print()

    # Create .env file
    create_env_file()
    print()

    # Create directories
    create_directories()
    print()

    print("🎉 Environment setup complete!")
    print("📋 Next steps:")
    print("   1. Edit .env file with your configuration")
    print("   2. Install dependencies: uv sync")
    print("   3. Run the application: uv run python main.py")


if __name__ == "__main__":
    main()
