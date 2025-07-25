"""Command Line Interface for Task Manager."""

from datetime import datetime
from dateutil.parser import parse as parse_date
from app.api.task_service import TaskService
from app.database.connection import DatabaseConnection
from app.logger import default_logger as logger
import config


class TaskCLI:
    """Command Line Interface for managing tasks."""
    
    def __init__(self):
        """Initialize CLI with database connection and task service."""
        self.db_connection = DatabaseConnection()
        self.task_service = None
        self.running = False
    
    def start(self):
        """Start the CLI application."""
        print("=" * 60)
        print("TASK MANAGER CLI")
        print("=" * 60)
        
        if not self.db_connection.connect():
            print("Failed to start application. Please ensure MongoDB is running.")
            return
        
        self.task_service = TaskService(self.db_connection)
        self.running = True
        
        logger.info("Type 'help' for available commands or 'exit' to quit.")
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                self.handle_command(command)
            except KeyboardInterrupt:
                logger.info("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}")
        
        self.db_connection.close()
    
    def handle_command(self, command: str):
        """Handle user commands."""
        # Split command into parts for argument parsing
        command_parts = command.split()
        base_command = command_parts[0] if command_parts else ""
        
        if base_command == "help":
            self.show_help()
        elif base_command == "add":
            self.add_task()
        elif base_command == "list":
            # Parse list command arguments
            args = command_parts[1:] if len(command_parts) > 1 else []
            self.list_tasks(args)
        elif base_command =="mark_complete":
            self.mark_task_complete()
        elif base_command == "update":
            self.update_task()
        elif base_command == "delete":
            self.delete_task()
        elif base_command == "exit":
            self.running = False
            logger.info("Goodbye!")
        elif command == "":
            pass  # Ignore empty input
        else:
            logger.error(f"Unknown command: '{command}'. Type 'help' for available commands.")
        
        logger.info("\n\nType 'help' for available commands or 'exit' to quit.")
    
    def show_help(self):
        """Display help information."""
        print("\nAVAILABLE COMMANDS:")
        print("-" * 30)
        print("add     - Add a new task")
        print("list    - List all tasks with optional filtering and sorting")
        print("          Usage: list [--filter status:value] [--filter priority:value] [--sort field:order]")
        print("          Examples:")
        print("            list")
        print("            list --filter status:Pending")
        print("            list --filter priority:High --sort due_date:asc")
        print("            list --sort created_at:desc")
        print("mark_complete - mark a Pending or In Progress Task as completed")
        print("update  - Update an existing task")
        print("delete  - Delete a task")
        print("help    - Show this help message")
        print("exit    - Exit the application")
    
    
    def add_task(self):
        """Add a new task."""
        print("\n➕ ADD NEW TASK")
        print("-" * 20)
        
        try:
            title = input("Enter task title: ").strip()
            if not title:
                print("Title is required!")
                return
            
            description = input("Enter description (optional): ").strip()
            
            due_date_str = input("Enter due date (YYYY-MM-DD, optional): ").strip()
            due_date = None
            if due_date_str:
                try:
                    # Validate date format
                    parse_date(due_date_str)
                    due_date = due_date_str
                except:
                    logger.warning("Invalid date format. Due date not set.")
            
            logger.info(f"Priority options: {', '.join(config.PRIORITY_LEVELS)}")
            priority = input("Enter priority (High/Medium/Low): ").strip().title()
            if priority not in config.PRIORITY_LEVELS:
                priority = "Low"
                logger.warning("Invalid priority. Set to 'Low'.")
            
            # Create task
            task = self.task_service.create_task(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority
            )
            
            logger.info(f"Task created successfully! ID: {task.task_id}")
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
    
    def list_tasks(self, args=None):
        """List all tasks with optional filtering and sorting via arguments or interactive mode."""
        print("\n📝 LIST TASKS")
        print("=" * 30)
        
        try:
            # Initialize filter and sort variables
            status_filter = None
            priority_filter = None
            sort_field = None
            sort_order = 'desc'  # default
            
            # Parse command line arguments if provided
            if args:
                i = 0
                while i < len(args):
                    if args[i] == '--filter' and i + 1 < len(args):
                        filter_arg = args[i + 1]
                        if ':' in filter_arg:
                            filter_type, filter_value = filter_arg.split(':', 1)
                            if filter_type.lower() == 'status':
                                if filter_value.title() in config.STATUS_OPTIONS:
                                    status_filter = filter_value.title()
                                else:
                                    logger.warning(f"Invalid status '{filter_value}'. Available: {', '.join(config.STATUS_OPTIONS)}")
                            elif filter_type.lower() == 'priority':
                                if filter_value.title() in config.PRIORITY_LEVELS:
                                    priority_filter = filter_value.title()
                                else:
                                    logger.warning(f"Invalid priority '{filter_value}'. Available: {', '.join(config.PRIORITY_LEVELS)}")
                        i += 2
                    elif args[i] == '--sort' and i + 1 < len(args):
                        sort_arg = args[i + 1]
                        if ':' in sort_arg:
                            field, order = sort_arg.split(':', 1)
                            available_fields = ['title', 'priority', 'status', 'created_at', 'due_date']
                            if field.lower() in available_fields:
                                sort_field = field.lower()
                                sort_order = order.lower() if order.lower() in ['asc', 'desc'] else 'desc'
                            else:
                                logger.warning(f"Invalid sort field '{field}'. Available: {', '.join(available_fields)}")
                        else:
                            # Just field provided, use default desc order
                            available_fields = ['title', 'priority', 'status', 'created_at', 'due_date']
                            if sort_arg.lower() in available_fields:
                                sort_field = sort_arg.lower()
                        i += 2
                    else:
                        logger.warning(f"Unknown argument: {args[i]}")
                        i += 1
            else:
                # Interactive mode - ask for filtering and sorting options
                print("\nFiltering and Sorting Options:")
                print("Filter by status? (y/N):", end=" ")
                filter_status = input().strip().lower() == 'y'
                
                if filter_status:
                    print(f"Available statuses: {', '.join(config.STATUS_OPTIONS)}")
                    status_input = input("Enter status: ").strip().title()
                    if status_input in config.STATUS_OPTIONS:
                        status_filter = status_input
                    else:
                        logger.warning("Invalid status. No status filter applied.")
                
                print("Filter by priority? (y/N):", end=" ")
                filter_priority = input().strip().lower() == 'y'
                
                if filter_priority:
                    print(f"Available priorities: {', '.join(config.PRIORITY_LEVELS)}")
                    priority_input = input("Enter priority: ").strip().title()
                    if priority_input in config.PRIORITY_LEVELS:
                        priority_filter = priority_input
                    else:
                        logger.warning("Invalid priority. No priority filter applied.")
                
                # Sorting options
                print("Sort tasks? (y/N):", end=" ")
                sort_tasks = input().strip().lower() == 'y'
                
                if sort_tasks:
                    available_fields = ['title', 'priority', 'status', 'created_at', 'due_date']
                    print(f"Available sort fields: {', '.join(available_fields)}")
                    sort_field_input = input("Enter sort field: ").strip().lower()
                    if sort_field_input in available_fields:
                        sort_field = sort_field_input
                        print("Sort order: (1) Ascending (2) Descending")
                        order_choice = input("Enter choice (1/2): ").strip()
                        sort_order = 'asc' if order_choice == '1' else 'desc'
                    else:
                        logger.warning("Invalid sort field. Default sorting will be used.")
            
            # Get tasks based on filters
            if status_filter and priority_filter:
                # Get all tasks and filter manually for both conditions
                tasks = self.task_service.get_all_tasks()
                tasks = [task for task in tasks if task.status == status_filter and task.priority == priority_filter]
            elif status_filter:
                tasks = self.task_service.get_tasks_by_status(status_filter)
            elif priority_filter:
                tasks = self.task_service.get_tasks_by_priority(priority_filter)
            else:
                tasks = self.task_service.get_all_tasks()
            
            # Apply sorting if requested
            if sort_field and tasks:
                reverse_order = (sort_order == 'desc')
                
                if sort_field == 'title':
                    tasks.sort(key=lambda x: x.title.lower(), reverse=reverse_order)
                elif sort_field == 'priority':
                    # Custom priority sorting: High > Medium > Low
                    priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
                    tasks.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=reverse_order)
                elif sort_field == 'status':
                    tasks.sort(key=lambda x: x.status, reverse=reverse_order)
                elif sort_field == 'created_at':
                    tasks.sort(key=lambda x: x.created_at, reverse=reverse_order)
                elif sort_field == 'due_date':
                    # Handle None due dates by putting them at the end
                    def due_date_key(task):
                        if task.due_date is None:
                            return datetime.max if not reverse_order else datetime.min
                        try:
                            return parse_date(task.due_date)
                        except:
                            return datetime.max if not reverse_order else datetime.min
                    
                    tasks.sort(key=due_date_key, reverse=reverse_order)
            
            # Display results
            if not tasks:
                logger.warning("No tasks found matching the criteria.")
                return
            
            # Show applied filters and sorting
            filter_info = []
            if status_filter:
                filter_info.append(f"Status: {status_filter}")
            if priority_filter:
                filter_info.append(f"Priority: {priority_filter}")
            
            if filter_info:
                print(f"Filters applied: {', '.join(filter_info)}")
            
            if sort_field:
                print(f"Sorted by: {sort_field} ({sort_order}ending)")
            
            print("-" * 50)
            
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.display()}")
            
            logger.info(f"\nTotal tasks displayed: {len(tasks)}")
            
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {e}")
    
    def mark_task_complete(self):
        """List all tasks."""
        print("\nMakr task as complete (provide the task_id)")
        print("=" * 30)
        
        try:
            tasks = self.task_service.get_tasks_by_status('In Progress')
            check_tasks = 0
            if(tasks):
                logger.info("All In Progress tasks.")
                for task in tasks:
                    print(task.task_id)
                check_tasks += 1
            else:
                logger.info("No In Progress tasks")
            tasks_incomplete = self.task_service.get_tasks_by_status('Pending')

            if(tasks_incomplete):
                logger.info("All in Pending tasks")
                for task in tasks_incomplete:
                    print(task.task_id)
                check_tasks +=1
            else:
                logger.info("No In Pending tasks")
            
            if check_tasks >0:
                task_id = input(f"Task ID: ").strip()
                #validate input
                if task_id:
                    validated_task = self.task_service.get_task_by_id(task_id)
                    if not validated_task:
                        logger.warning(f"{task_id} -  not found.")
                        return
                    else:
                        #make sure that the status of the selected task is incomplete to provide appropriate message
                        if validated_task.status == 'Completed':
                            logger.warning(f"{validated_task.task_id} - {validated_task.title} is already completed!")
                            return
                        else:
                            #execute command
                            if self.task_service.mark_task_completed(validated_task.task_id):
                                logger.info(f"Successfully completed task {validated_task.task_id}-{validated_task.title}")
                            else:
                                logger.error(f"Failed to complete task {validated_task.task_id}")
            else:
                logger.info("No incomplete tasks available to mark as complete.")

            
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {e}")
    def update_task(self):
        """Update an existing task."""
        print("\nUPDATE TASK")
        print("-" * 20)
        
        try:
            task_id = input("Enter task ID: ").strip()
            if not task_id:
                logger.wanring("Task ID is required!")
                return
            
            # Check if task exists
            existing_task = self.task_service.get_task_by_id(task_id)
            if not existing_task:
                logger.warning("Task not found!")
                return
            
            logger.info(f"\nCurrent task details:")
            logger.info(existing_task.display())
            
            print("\nEnter new values (press Enter to keep current value):")
            
            # Get updates
            updates = {}
            
            new_title = input(f"Title [{existing_task.title}]: ").strip()
            if new_title:
                updates["title"] = new_title
            
            new_description = input(f"Description [{existing_task.description}]: ").strip()
            if new_description or new_description == "":  # Allow empty description
                updates["description"] = new_description
            
            new_due_date = input(f"Due date [{existing_task.due_date or 'Not set'}]: ").strip()
            if new_due_date:
                try:
                    parse_date(new_due_date)
                    updates["due_date"] = new_due_date
                except:
                    logger.warning("Invalid date format. Due date not updated.")
            
            logger.info(f"Priority options: {', '.join(config.PRIORITY_LEVELS)}")
            new_priority = input(f"Priority [{existing_task.priority}]: ").strip().title()
            if new_priority and new_priority in config.PRIORITY_LEVELS:
                updates["priority"] = new_priority
            elif new_priority:
                logger.warning("Invalid priority. Not updated.")
            
            logger.info(f"Status options: {', '.join(config.STATUS_OPTIONS)}")
            new_status = input(f"Status [{existing_task.status}]: ").strip().title()
            if new_status and new_status in config.STATUS_OPTIONS:
                updates["status"] = new_status
            elif new_status:
                logger.warning("Invalid status. Not updated.")
            
            if not updates:
                logger.info("No changes made.")
                return
            
            # Update task
            if self.task_service.update_task(task_id, **updates):
                logger.info("Task updated successfully!")
            else:
                logger.error("Failed to update task.")
                
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
    
    def delete_task(self):
        """Delete a task."""
        print("\nDELETE TASK")
        print("-" * 20)
        
        try:
            task_id = input("Enter task ID: ").strip()
            if not task_id:
                logger.error("Task ID is required!")
                return
            
            # Check if task exists
            existing_task = self.task_service.get_task_by_id(task_id)
            if not existing_task:
                logger.error("Task not found!")
                return
            
            print(f"\nTask to delete:")
            print(existing_task.display())
            
            confirm = input("Are you sure you want to delete this task? (y/N): ").strip().lower()
            if confirm != 'y':
                logger.info("Deletion cancelled.")
                return
            
            if self.task_service.delete_task(task_id):
                logger.info("Task deleted successfully!")
            else:
                logger.warning("Failed to delete task.")
                
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")