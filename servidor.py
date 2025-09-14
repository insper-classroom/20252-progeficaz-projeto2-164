from flask import Flask
from views import imoveis_bp

app = Flask(__name__)
app.static_folder = 'static'

app.register_blueprint(imoveis_bp)

if __name__ == "__main__":
    app.run(debug=True)
