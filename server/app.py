from flask import Flask, send_from_directory
from pathlib import Path
import os
import sys

# Add server directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db
from routes import auth, children, chores, history

app = Flask(__name__, static_folder=str(Path(__file__).parent.parent / 'static'))


# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    # Try to serve the exact file
    file_path = Path(app.static_folder) / path
    if file_path.is_file():
        return send_from_directory(app.static_folder, path)
    # For SPA routing, serve index.html for non-file routes
    return send_from_directory(app.static_folder, 'index.html')


# Register API blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(children.bp, url_prefix='/api/children')
app.register_blueprint(chores.bp, url_prefix='/api')
app.register_blueprint(history.bp, url_prefix='/api/history')


if __name__ == '__main__':
    init_db()
    print("Starting Chores App on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
