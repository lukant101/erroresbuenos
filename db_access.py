from flaskblog.models import User

data = User.query.all()

for record in data:
    print(record)
