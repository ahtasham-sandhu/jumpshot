from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, get_failure_response, parse_request_body, validate_required_fields
from app.helpers.decorators import login_required
from common.app_config import config
from common.services import TodoService
from common.models.todo import Todo

todo_api = Namespace('todo', description="Todo-related APIs")

@todo_api.route('/')
class TodoList(Resource):
    
    @login_required()
    def get(self, person):
        # Get filter parameter from query string (default to None for all todos)
        filter_status = request.args.get('filter', None)
        
        # Validate filter parameter
        valid_filters = [None, 'all', 'completed', 'incomplete']
        if filter_status not in valid_filters:
            return get_failure_response(
                message="Invalid filter. Use 'all', 'completed', or 'incomplete'.",
                status_code=400
            )
        
        # Convert 'all' to None for service layer
        if filter_status == 'all':
            filter_status = None
        
        todo_service = TodoService(config)
        todos = todo_service.get_todos_by_person(person.entity_id, filter_status)

        todos_list = [todo.as_dict() for todo in todos]
        
        return get_success_response(todos=todos_list, count=len(todos_list))
    
    @login_required()
    def post(self, person):
        parsed_body = parse_request_body(request, ['title', 'is_completed'])
        validate_required_fields({'title': parsed_body['title']})
        
        # Create new todo
        todo = Todo(
            person_id=person.entity_id,
            title=parsed_body['title'],
            is_completed=parsed_body.get('is_completed', False) or False
        )
        
        todo_service = TodoService(config)
        saved_todo = todo_service.save_todo(todo)
        
        return get_success_response(
            message="Todo created successfully.",
            todo=saved_todo.as_dict(),
            status_code=200
        )


@todo_api.route('/<string:todo_id>')
class TodoItem(Resource):
    
    @login_required()
    def get(self, person, todo_id):
        todo_service = TodoService(config)
        todo = todo_service.get_todo_by_id(todo_id)

        if not todo or todo.person_id != person.entity_id:
            return get_failure_response(message="Todo not found or not authorized to access this todo")
        
        return get_success_response(todo=todo.as_dict())
    
    @login_required()
    def put(self, person, todo_id):
        parsed_body = parse_request_body(request, ['title', 'is_completed'], default_value=None)
        
        # At least one field should be provided
        if not parsed_body.get('title') and parsed_body.get('is_completed') is None:
            return get_failure_response(
                message="At least one field (title or is_completed) must be provided.",
                status_code=400
            )
        
        todo_service = TodoService(config)
        todo = todo_service.get_todo_by_id(todo_id)
        
        if not todo or todo.person_id != person.entity_id:
            return get_failure_response(message="Todo not found or not authorized to access this todo")
        
        # Update fields if provided
        if parsed_body.get('title'):
            todo.title = parsed_body['title']
        
        if parsed_body.get('is_completed') is not None:
            todo.is_completed = parsed_body['is_completed']
        
        updated_todo = todo_service.save_todo(todo)
        
        return get_success_response(
            message="Todo updated successfully.",
            todo=updated_todo.as_dict()
        )
    
    @login_required()
    def delete(self, person, todo_id):
        todo_service = TodoService(config)
        todo = todo_service.get_todo_by_id(todo_id)
        
        if not todo or todo.person_id != person.entity_id:
            return get_failure_response(message="Todo not found or not authorized to access this todo")
        
        # Delete the todo
        todo_service.delete_todo(todo)
        
        return get_success_response(message="Todo deleted successfully.")

