"""Task model definition."""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class Task:
    """Task model representing a task entity with proper encapsulation."""
    
    # Class constants for validation
    VALID_PRIORITIES = ["High", "Medium", "Low"]
    VALID_STATUSES = ["Pending", "In Progress", "Completed"]
    
    def __init__(self, title: str, description: str = "", due_date: Optional[str] = None,
                 priority: str = "Medium", status: str = "Pending",
                 task_id: Optional[ObjectId] = None, created_at: Optional[datetime] = None):
        """
        Initialize a Task instance with validation.
        
        Args:
            title: Task title (required)
            description: Task description
            due_date: Due date in YYYY-MM-DD format
            priority: Priority level (High, Medium, Low)
            status: Task status (Pending, In Progress, Completed)
            task_id: MongoDB ObjectId (auto-generated if None)
            created_at: Creation timestamp (auto-generated if None)
        """
        # Private attributes (convention using underscore)
        self._task_id = task_id or ObjectId()
        self._created_at = created_at or datetime.now()
        
        # Use property setters for validation
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
    
    # Property for task_id (read-only after creation)
    @property
    def task_id(self) -> ObjectId:
        """Get task ID (read-only)."""
        return self._task_id
    
    # Property for created_at (read-only)
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp (read-only)."""
        return self._created_at
    
    # Property for title with validation
    @property
    def title(self) -> str:
        """Get task title."""
        return self._title
    
    @title.setter
    def title(self, value: str):
        """Set task title with validation."""
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        if not value.strip():
            raise ValueError("Title cannot be empty")
        if len(value.strip()) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        self._title = value.strip()
    
    # Property for description with validation
    @property
    def description(self) -> str:
        """Get task description."""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """Set task description with validation."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if len(value) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        self._description = value
    
    # Property for due_date with validation
    @property
    def due_date(self) -> Optional[str]:
        """Get due date."""
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: Optional[str]):
        """Set due date with validation."""
        if value is None or value == "":
            self._due_date = None
            return
        
        if not isinstance(value, str):
            raise TypeError("Due date must be a string or None")
        
        try:
            # Validate date format
            parsed_date = parse_date(value)
            # Store in consistent format
            self._due_date = parsed_date.strftime('%Y-%m-%d')
        except Exception:
            raise ValueError("Due date must be in valid date format (e.g., YYYY-MM-DD)")
    
    # Property for priority with validation
    @property
    def priority(self) -> str:
        """Get task priority."""
        return self._priority
    
    @priority.setter
    def priority(self, value: str):
        """Set task priority with validation."""
        if not isinstance(value, str):
            raise TypeError("Priority must be a string")
        
        value_title = value.strip().title()
        if value_title not in self.VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}")
        
        self._priority = value_title
    
    # Property for status with validation
    @property
    def status(self) -> str:
        """Get task status."""
        return self._status
    
    @status.setter
    def status(self, value: str):
        """Set task status with validation."""
        if not isinstance(value, str):
            raise TypeError("Status must be a string")
        
        value_title = value.strip().title()
        if value_title not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
        
        self._status = value_title
        
    def to_dict(self) -> dict:
        """Convert task to dictionary for MongoDB storage."""
        return {
            "_id": self._task_id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "priority": self._priority,
            "status": self._status,
            "created_at": self._created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Task instance from dictionary."""
        return cls(
            task_id=data.get("_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            created_at=data.get("created_at")
        )
    
    def __str__(self) -> str:
        """String representation of the task."""
        return f"Task(id={self.task_id}, title='{self.title}', status='{self.status}')"
    
    def display(self) -> str:
        """Formatted display string for CLI output."""
        return f"""
ID: {self.task_id}
Title: {self.title}
Description: {self.description}
Due Date: {self.due_date or 'Not set'}
Priority: {self.priority}
Status: {self.status}
Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}
{'-' * 50}"""