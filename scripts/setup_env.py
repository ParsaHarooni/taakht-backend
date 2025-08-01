#!/usr/bin/env python3
"""
Environment setup script for Taakht Backend.
This script helps set up the environment configuration for different environments.
"""

import os
import shutil
from pathlib import Path


def create_env_file(environment: str = "development"):
    """Create .env file from template."""

    # Check if .env already exists
    if os.path.exists(".env"):
        print("⚠️  .env file already exists. Skipping creation.")
        return

    # Check if env.example exists
    if not os.path.exists("env.example"):
        print("❌ env.example file not found. Please create it first.")
        return

    # Copy env.example to .env
    shutil.copy("env.example", ".env")

    # Update environment in .env file
    with open(".env", "r") as f:
        content = f.read()

    # Replace ENVIRONMENT value
    content = content.replace("ENVIRONMENT=development", f"ENVIRONMENT={environment}")

    with open(".env", "w") as f:
        f.write(content)

    print(f"✅ Created .env file with {environment} environment")


def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "uploads",
        "uploads/items",
        "uploads/users",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def main():
    """Main setup function."""
    print("🚀 Setting up Taakht Backend environment...")

    # Get environment from user
    env = input(
        "Enter environment (development/production/test) [development]: "
    ).strip()
    if not env:
        env = "development"

    if env not in ["development", "production", "test"]:
        print("❌ Invalid environment. Using development.")
        env = "development"

    # Create .env file
    create_env_file(env)

    # Create directories
    create_directories()

    print(f"\n🎉 Environment setup complete for {env}!")
    print("\nNext steps:")
    print("1. Edit .env file with your specific configuration")
    print("2. Run: uv sync (to install dependencies)")
    print("3. Run: uv run python main.py (to start the server)")

    if env == "production":
        print("\n⚠️  Production setup:")
        print("- Update SECRET_KEY and JWT_SECRET_KEY in .env")
        print("- Configure DATABASE_URL for PostgreSQL")
        print("- Set up proper CORS_ORIGINS")
        print("- Configure SMTP settings for email functionality")


if __name__ == "__main__":
    main()
