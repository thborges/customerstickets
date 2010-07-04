#
# coding: utf-8 

import re
from genshi.core import Markup

from trac.core import ComponentManager
from trac.versioncontrol.api import Repository
from trac.wiki.macros import WikiMacroBase

class GitbranchesMacro(WikiMacroBase):
    """Show the repository branchs which contains the ticket revisions. The revisions are retrieved from comments in the format: "In [revision/repo].
    """
    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        if text:
            repos = self.env.get_repository("gitusers")
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            cursor.execute("select distinct newvalue from ticket_change where ticket = %s and field = 'comment' and newvalue like 'In [%'", (text,));
            revisions = []
            for comment, in cursor:
                m = re.search('.*\[([a-z0-9]*)/(.*)]', comment)
                revision = m.group(1)
                reponame = m.group(2)
                branches = repos.git.get_branches_of_commit(revision)
                revisions.append('<a href="%s/%s">%s</a>: [%s]' % (self.env.href.changeset(revision), reponame, revision, ','.join(branches)))
            return '<br>'.join(revisions)
        else:
            return 'Nenhum branch especificado.'

class GitbranchStatusMacro(WikiMacroBase):
    """Find revisions in tickets of a milestone and map what was merged or not in the branch.
    Sintaxe: GitbranchStatus(milestone, git_branch_name, additional ticket1, ...)
    Ex: GitbranchStatus(milestone1, ver_3301, 123, 124, 125)
    """
    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        if text:
            result = []
            repos = self.env.get_repository("gitusers")
            db = self.env.get_db_cnx()
            params = text.split(',')
            
            milestone = params[0].lstrip()
            milesbranch = params[1].lstrip()
            result.append('O branch para o milestone e <b>"%s"</b>. Abaixo os tickets relacionados. Em verde estao as revisoes ja integradas, e em vermelho as pendencias.<br>' % milesbranch)

            ctickets = db.cursor()
            ctickets.execute("select id from ticket where milestone = %s order by id", (milestone,))
            tickets = []
            [tickets.append(tkt) for tkt, in ctickets]
            [tickets.append(tkt.lstrip()) for tkt in params[2:]]
            tickets.sort(key = lambda i: int(i))

            for ticket in tickets:
                result.append('<p>Ticket <a href="%s">%s</a>:</p><pre class="wiki">' % (self.env.href.ticket(ticket), ticket))
                cursor = db.cursor()
                cursor.execute("select distinct newvalue from ticket_change where ticket = %s and field = 'comment' and newvalue like 'In [%%'", (ticket,));
                for comment, in cursor:
                    m = re.search('.*\[([a-z0-9]*)/(.*)]', comment)
                    revision = m.group(1)
                    reponame = m.group(2)
                    branches = repos.git.get_branches_of_commit(revision)
                    branches = [br.lstrip() for br in branches]
                    merged = "red"
                    if 0 < branches.count(milesbranch):
                      merged = "green"
                    result.append('<a style="color: black; background: %s" href="%s/%s">%s</a>: [%s]<br>' % (merged, self.env.href.changeset(revision), reponame, revision, ' '.join(branches)))
                result.append("</pre>")    
            return ''.join(result)
        else:
            return 'Nenhum branch especificado.'


