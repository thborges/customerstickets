from trac.core import *
from trac.util.translation import _
from trac.resource import ResourceNotFound

class Customer(object):

    def __init__(self, env, id=None, db=None):
        self.env = env
        if id:
            self._fetch(id, db)
        else:
            self.id = None
            self.name = ''
            self.mininame = ''
            self.curmilestone = None

    def _fetch(self, id, db=None):
        if not db:
            db = self.env.get_read_db()
        cursor = db.cursor()
        cursor.execute("""
            select id, name, mininame, curmilestone
            from customer where id=%s
            """, (id,))
        
        row = cursor.fetchone()
        if not row:
            raise ResourceNotFound(_('Customer %(id)s does not exist.',
                                   id=id), _('Invalid customer id'))
        
        self.id = id
        self.name = row[1]
        self.mininame = row[2]
        self.curmilestone = row[3]
    
    def insert(self, db=None):
        if not db:
            db = self.env.get_read_db()
        @self.env.with_transaction(db)
        def do_insert(db):
            cursor = db.cursor()
            cursor.execute("""
                insert into customer(name,mininame,curmilestone) values (%s,%s,%s)
                """, (self.name, self.mininame, self.curmilestone))
            db.commit()

    def update(self, db=None):
        if not db:
            db = self.env.get_read_db()
        @self.env.with_transaction(db)
        def do_update(db):
            cursor = db.cursor()
            cursor.execute("""
                update customer set name=%s, mininame=%s, curmilestone=%s where id=%s
                """, (self.name, self.mininame, self.curmilestone, self.id))
            db.commit()


