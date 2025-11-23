from common.repositories.base import BaseRepository
from common.models.todo import Todo

class TodoRepository(BaseRepository):
    MODEL = Todo

    def bulk_delete_completed(self, person_id: str) -> int:
        """Delete all completed todos for a person. Returns count of deleted todos."""
        query = """
            DELETE FROM todo
            WHERE person_id = %s AND is_completed = TRUE
            RETURNING entity_id;
        """
        params = (person_id,)

        with self.adapter:
            results = self.adapter.execute_query(query, params)
            return len(results) if results else 0

    def bulk_update_to_completed(self, person_id: str) -> int:
        """Mark all todos as completed for a person. Returns count of updated todos."""
        query = """
            UPDATE todo
            SET is_completed = TRUE
            WHERE person_id = %s AND is_completed = FALSE
            RETURNING entity_id;
        """
        params = (person_id,)

        with self.adapter:
            results = self.adapter.execute_query(query, params)
            return len(results) if results else 0

    def bulk_update_to_pending(self, person_id: str) -> int:
        """Mark all todos as pending (incomplete) for a person. Returns count of updated todos."""
        query = """
            UPDATE todo
            SET is_completed = FALSE
            WHERE person_id = %s AND is_completed = TRUE
            RETURNING entity_id;
        """
        params = (person_id,)

        with self.adapter:
            results = self.adapter.execute_query(query, params)
            return len(results) if results else 0