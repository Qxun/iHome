# -*- coding: utf-8 -*-
from flask_migrate import Manager, MigrateCommand, Migrate
from iHome import create_app, db


app = create_app('developmentconfig')

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)




if __name__ == '__main__':
    # app.run()
    print app.url_map
    manager.run()
