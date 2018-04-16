# -*- coding: utf-8 -*-
from flask_migrate import Manager, MigrateCommand, Migrate
from iHome import create_app, db


app = create_app()

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    # redis_store.set('age', 18)
    # session['city'] = 'beijing'
    return 'Hello World!'


if __name__ == '__main__':
    # app.run()
    manager.run()
