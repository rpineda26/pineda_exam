"""Task service layer for business logic."""

from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.task import Task
from app.database.connection import DatabaseConnection


class TaskService:
    """Service class for task operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize TaskService with database connection.
        
        Args:
            db_connection: Database connection instance
        """
        self.db_connection = db_connection
        self.collection = db_connection.get_collection()
    
    def create_task(self, title: str, description: str = "", due_date: Optional[str] = None,
                   priority: str = "Medium") -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            due_date: Due date string
            priority: Priority level
            
        Returns:
            Task: Created task instance
        """
        task = Task(title=title, description=description, due_date=due_date, priority=priority)
        
        # Insert into database
        result = self.collection.insert_one(task.to_dict())
        task.task_id = result.inserted_id
        
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks from database.
        
        Returns:
            List[Task]: List of all tasks
        """
        tasks = []
        cursor = self.collection.find().sort("created_at", -1)  # Latest first
        
        for doc in cursor:
            tasks.append(Task.from_dict(doc))
        
        return tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by its ID.
        
        Args:
            task_id: Task ID string
            
        Returns:
            Task or None: Task instance if found, None otherwise
        """
        try:
            object_id = ObjectId(task_id)
            doc = self.collection.find_one({"_id": object_id})
            
            if doc:
                return Task.from_dict(doc)
            return None
            
        except InvalidId:
            return None
    def mark_task_completed(self, task_id: str) ->bool:
        """
        Update a task with new values.
        
        Args:
            task_id: Task ID string
            **updates: Fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            object_id = ObjectId(task_id)
        
            # Filter out None values and empty strings (except for description)
            filtered_updates = {"status": "Completed"}
  
            if not filtered_updates:
                return False
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": filtered_updates}
            )
            
            return result.modified_count > 0
            
        except InvalidId:
            return False
    
    def update_task(self, task_id: str, **updates) -> bool:
        """
        Update a task with new values.
        
        Args:
            task_id: Task ID string
            **updates: Fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            object_id = ObjectId(task_id)
            
            # Filter out None values and empty strings (except for description)
            filtered_updates = {}
            for key, value in updates.items():
                if value is not None and (value != "" or key == "description"):
                    filtered_updates[key] = value
            
            if not filtered_updates:
                return False
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": filtered_updates}
            )
            
            return result.modified_count > 0
            
        except InvalidId:
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from database.
        
        Args:
            task_id: Task ID string
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            object_id = ObjectId(task_id)
            result = self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
            
        except InvalidId:
            return False
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """
        Get tasks filtered by status.
        
        Args:
            status: Task status
            
        Returns:
            List[Task]: List of tasks with specified status
        """
        tasks = []
        cursor = self.collection.find({"status": status}).sort("created_at", -1)
        
        for doc in cursor:
            tasks.append(Task.from_dict(doc))
        
        return tasks
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """
        Get tasks filtered by priority.
        
        Args:
            priority: Task priority
            
        Returns:
            List[Task]: List of tasks with specified priority
        """
        tasks = []
        cursor = self.collection.find({"priority": priority}).sort("created_at", -1)
        
        for doc in cursor:
            tasks.append(Task.from_dict(doc))
        
        return tasks