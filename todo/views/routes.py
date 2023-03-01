# from flask import Blueprint, jsonify

from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


# @api.route('/todos', methods=['GET'])
# def get_todos():
#     """Return the list of todo items"""
#     return jsonify([TEST_ITEM])

@api.route('/todos', methods=['GET'])
def get_todos():
    args = request.args

    task_completed = args.get('completed')
    task_window = args.get('window')

    todos = []
    if task_completed is not None:
        # task_status = True if task_complete is 'True' else False
        id_query = Todo.query.filter_by(completed=True).all()
        todos.extend(id_query)

    elif task_window is not None:
        # id_query = Todo.query.filter_by(window=task_window).all()
        todos = Todo.query.all()

        today = datetime.now()

        task_window = int(task_window)
        result = []
        for task in todos:
            task_dict = task.to_dict()

            dead_line = task_dict['deadline_at']

            datetime_convert = datetime.fromisoformat(dead_line)

            date_different = datetime_convert - today
            
            if date_different.days < task_window:
                result.append(task_dict)

        
        return jsonify(result)

    else:
        todos = Todo.query.all()

    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

# @api.route('/todos/<int:todo_id>', methods=['GET'])
# def get_todo(todo_id):
#     """Return the details of a todo item"""
#     return jsonify(TEST_ITEM)
@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

# @api.route('/todos', methods=['POST'])
# def create_todo():
#     """Create a new todo item and return the created item"""
#     return jsonify(TEST_ITEM), 201

def test_valid_json():
    task_list = []
    task_list.append(request.json.get('id'))
    task_list.append(request.json.get('title'))
    task_list.append(request.json.get('description'))
    task_list.append(request.json.get('completed'))
    task_list.append(request.json.get('deadline_at'))

    max_task = 5

    num_None = sum(task is None for task in task_list)

    expected_task = max_task - num_None

    if expected_task != len(request.json):
        return False

    if expected_task == 0:
        return False

    return True

@api.route('/todos', methods=['POST'])
def create_todo():
    if not test_valid_json():
        return [], 400

    if request.json.get('title') is None:
        return [], 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )

    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    # Commits the changes to the database, this must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

# @api.route('/todos/<int:todo_id>', methods=['PUT'])
# def update_todo(todo_id):
#     """Update a todo item and return the updated item"""
#     return jsonify(TEST_ITEM)


@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):

    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    todo_id = request.json.get('id')
    
    if todo_id is not None:
        return jsonify({'error': "Can't change id"}), 400

    if not test_valid_json():
        return jsonify({'error': 'Invalid Key'}), 400

    
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

# @api.route('/todos/<int:todo_id>', methods=['DELETE'])
# def delete_todo(todo_id):
#     """Delete a todo item and return the deleted item"""
#     return jsonify(TEST_ITEM)

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
