from typing import List, Optional
from common.repositories.factory import RepositoryFactory, RepoType
from common.models.todo import Todo

class TodoService:
    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.todo_repo = self.repository_factory.get_repository(RepoType.TODO)

    def save_todo(self, todo: Todo) -> Todo:
        return self.todo_repo.save(todo)

    def update_todo(self, todo_id: str, title: Optional[str] = None, is_completed: Optional[bool] = None) -> Todo:
        """
        Update a todo by ID. Handles version management by fetching fresh data before save.
        This prevents version conflicts in optimistic locking.
        """
        # Fetch the latest version from database
        todo = self.todo_repo.get_one({"entity_id": todo_id})

        if not todo:
            return None

        # Apply updates
        if title is not None:
            todo.title = title

        if is_completed is not None:
            todo.is_completed = is_completed

        # Save and return updated todo
        return self.todo_repo.save(todo)

    def get_todo_by_id(self, entity_id: str) -> Optional[Todo]:
        return self.todo_repo.get_one({"entity_id": entity_id})
    
    def get_todos_by_person(self, person_id: str, filter_status: Optional[str] = None) -> List[Todo]:

        query = {"person_id": person_id}
        
        if filter_status == "completed":
            query["is_completed"] = True
        elif filter_status == "incomplete":
            query["is_completed"] = False
        
        todos = self.todo_repo.get_many(query)
        return todos if todos else []

    def delete_todo(self, todo: Todo):
        self.todo_repo.delete(todo)

    def delete_completed_todos(self, person_id: str) -> int:
        """Delete all completed todos for a person using bulk operation. Returns count of deleted todos."""
        return self.todo_repo.bulk_delete_completed(person_id)

    def mark_all_todos_completed(self, person_id: str) -> int:
        """Mark all todos as completed for a person using bulk operation. Returns count of updated todos."""
        return self.todo_repo.bulk_update_to_completed(person_id)

    def mark_all_todos_pending(self, person_id: str) -> int:
        """Mark all todos as pending for a person using bulk operation. Returns count of updated todos."""
        return self.todo_repo.bulk_update_to_pending(person_id)
