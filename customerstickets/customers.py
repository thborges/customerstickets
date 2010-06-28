import re

from genshi.builder import tag

from trac.core import *
from trac.web import IRequestHandler
from trac.web.chrome import INavigationContributor, ITemplateProvider 
from trac.web.chrome import add_notice, add_warning
from trac.ticket import model
from trac.util.translation import _
from trac.resource import ResourceNotFound

from model import Customer

class CustomersTicketsPlugin(Component):
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    def get_active_navigation_item(self, req):
        return 'customers'

    def get_navigation_items(self, req):
        yield ('mainnav', 'customers',
            tag.a('Customers', href=req.href.customers()))

    def match_request(self, req):

        if req.path_info == '/customers':
            return True

        match = re.match(r'/customers/([0-9]+)$', req.path_info)
        if match:
            req.args['id'] = match.group(1)
            return True

    def process_request(self, req):

        db = self.env.get_db_cnx()

        if req.method == 'POST':
            if not req.args.get('name') or not req.args.get('mininame'):
                raise TracError(_('Name and Label are required fields.'))

            cust = Customer(self.env, req.args.get('id')) 
            cust.name = req.args.get('name')
            cust.mininame = req.args.get('mininame')
            cust.curmilestone = req.args.get('curmilestone')

            if req.args.get('submit') == "add":
                cust.insert(db)
                add_notice(req, _('The customer %(name)s has been added.', name=cust.name))

            elif req.args.get('submit') == "update":
                cust.update(db)
                add_notice(req, _('The customer %(name)s has been updated.', name=cust.name))
              
            req.redirect(req.href.customers(None))
        else:
            data = {}
            cursor = db.cursor()
            cursor.execute('select id, name, mininame, curmilestone from customer order by mininame')
            customers = []
            for id, name, mininame, curmilestone in cursor:
                cust = Customer(self.env)
                cust.id = id
                cust.name = name
                cust.mininame = mininame
                cust.curmilestone = curmilestone
                customers.append(cust)

            data.update({'customers': customers})
            data.update({'milestones': model.Milestone.select(self.env, db=db)})

            if req.args.get('id'):
                data.update({'customer': Customer(self.env, req.args.get('id'))})
            else:
                data.update({'customer': None})

            return 'customers.html', data, None

    def get_htdocs_dirs(self):
        pass

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
