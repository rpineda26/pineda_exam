# pineda_exam
Technical assessment for a job application

setup:
go to the root directory before proceeding with the scripts
setup installation environment
`python -m venv venv`
windows:
`venv\Scripts\activate`
macos/linux:
`source venv/bin/activate`
then install dependencies
`pip install -r requirements.txt`

then run the application
`python main.py`

note: use python or python3 depending on what you have installed

AVAILABLE COMMANDS:
------------------------------
add     - Add a new task
list    - List all tasks with optional filtering and sorting
          Usage: list [--filter status:value] [--filter priority:value] [--sort field:order]
          Examples:
            list
            list --filter status:Pending
            list --filter priority:High --sort due_date:asc
            list --sort created_at:desc
mark_complete - mark a Pending or In Progress Task as completed
update  - Update an existing task
delete  - Delete a task
help    - Show this help message
exit    - Exit the application


Config:
------------------------------
config.py
# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "task_manager"
COLLECTION_NAME = "tasks"
