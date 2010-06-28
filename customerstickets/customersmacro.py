from genshi.core import Markup

from trac.wiki.macros import WikiMacroBase

class CustomersMacro(WikiMacroBase):
    """Convert customer codes to theirs mininames.
    """

    revision = "$Rev$"
    url = "$URL$"

    def expand_macro(self, formatter, name, text, args):
        if text:
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            cursor.execute("select name, mininame from customer where id in (%s)" % text)
            mininames = []
            for name, mininame in cursor:
                mininames.append('%s (%s)' % (name, mininame))
            return '<br>'.join(mininames)
        else:
            return 'Nenhum cliente especificado.'


