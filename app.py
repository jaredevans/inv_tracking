# app.py
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db  # Import the db instance and models from models.py

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shh'  # Change this for production.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/inv/inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Simple static credentials; for production, use a proper user system.
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'password'

# Configure ProxyFix (x_prefix set to 0 since we’re not using X-Script-Name now)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=0)

# Initialize the database with the app
db.init_app(app)

# Import and register blueprint from the inventory package.
from inventory.routes import inv_bp
app.register_blueprint(inv_bp)

if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run(debug=True, port=5003)
