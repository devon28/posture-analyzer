from flask_login import UserMixin
from datastore_entity import DatastoreEntity, EntityValue
import datetime


class User(DatastoreEntity, UserMixin):
    username = EntityValue(None)
    password = EntityValue(None)
    status = EntityValue(1)
    date_created = EntityValue(datetime.datetime.utcnow())
    

    # other fields or methods go here...
    #def authenticated(self, password):
    #    ...