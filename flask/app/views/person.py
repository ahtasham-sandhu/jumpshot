from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, parse_request_body
from app.helpers.decorators import login_required
from common.app_config import config
from common.services import PersonService

# Create the organization blueprint
person_api = Namespace('person', description="Person-related APIs")


@person_api.route('/me')
class Me(Resource):
    
    @login_required()
    def get(self, person):
        return get_success_response(person=person)
    
    @login_required()
    def put(self, person):
        parsed_body = parse_request_body(request, ['first_name', 'last_name'])
        
        # At least one field should be provided
        if not parsed_body.get('first_name') and not parsed_body.get('last_name'):
            return get_success_response(
                message="At least one field (first_name or last_name) must be provided.",
                status_code=400
            )
        
        # Update person name fields if provided
        if parsed_body.get('first_name') is not None:
            person.first_name = parsed_body['first_name']
        
        if parsed_body.get('last_name') is not None:
            person.last_name = parsed_body['last_name']
        
        # Save updated person
        person_service = PersonService(config)
        updated_person = person_service.save_person(person)
        
        return get_success_response(
            message="Profile updated successfully.",
            person=updated_person.as_dict()
        )