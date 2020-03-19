from flaskblog import create_app
from flaskblog.models import db
app = create_app()
if __name__ == '__main__':

    app.run(debug=True)