# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    """
    Entry point for the Flask application.
    """
    app.run(debug=True)