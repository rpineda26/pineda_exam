"""Main entry point for the Task Manager CLI application."""

from app.controller.task_cli import TaskCLI


def main():
    """Main function to start the Task Manager CLI."""
    cli = TaskCLI()
    cli.start()


if __name__ == "__main__":
    main()