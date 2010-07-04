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
            cursor.execute("select distinct newvalue from ticket_change where ticket = %s and field = 'comment' and newvalue like 'In [%%'", (text,));
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


