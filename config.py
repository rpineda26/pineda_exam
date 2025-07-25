"""Configuration settings for the Task Manager application."""
#should be .env and not pushed in a commit but this works for now

# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "task_manager"
COLLECTION_NAME = "tasks"

# Task Configuration
PRIORITY_LEVELS = ["High", "Medium", "Low"]
STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]