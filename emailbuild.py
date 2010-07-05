#!/usr/bin/python
# coding: ISO-8859-1

from poplib import *
from subprocess import *
import smtplib
import time
import re

popserver = "pop3.siagri.com.br"
smtpserver = "smtp.siagri.com.br"
user = "thiago.oliveira@siagri.com.br"
passwd = ""
caminho_repos = "/home/th/git/clones/clone1"

class Solicitacao():
    def __init__(self, fromaddr, ccs, subject):
        self.fromaddr = fromaddr
        self.ccs = ccs
        self.subject = subject


def get_emails():
    global popserver
    global user
    global passwd
    server = POP3(popserver)
    server.getwelcome()
    server.user(user)
    server.pass_(passwd)

    messagesInfo = server.list()[1]

    solicitacoes = []
    for msg in messagesInfo:
        msgNum = int(msg.split(" ")[0])
        msgSize = int(msg.split(" ")[1])
        if (msgSize < 20000):
            message = server.retr(msgNum)[1]
            ccs = []
            subject = ""
            fromaddr = "" 
            for linha in message:
                if linha.startswith("Subject:"):
                    subject = linha
                if linha.startswith("From:"):
                    fromaddr = linha.split(":")[1] 
                if linha.startswith("CC:"):
                    ccs.append(linha) 
            solicitacoes.append(Solicitacao(fromaddr, ccs, subject))
    return solicitacoes



def build_branch(solicitacao, branch):
    global caminho_repos
    print "cd %s; BRANCH=%s make -j3" % (caminho_repos, branch)

    output = ""
    try:
        output = Popen("cd %s; BRANCH=%s make -j3" % (caminho_repos, branch), shell=True, stdout=PIPE).communicate()[0]
        caminho = "file://server/bin/%s.tar.bz2" % branch
        inicio = "O branch %s foi compilado com sucesso. O arquivo compactado com os executáveis pode ser copiado de %s." % (branch, caminho)
    except Exception, e:
        output += str(e)
        inicio = "Ocorreu um erro ao compilar o branch %s." % (branch,)

    return "%s\r\n\r\nO log completo da compilação foi:\r\n\r\n%s" % (inicio, output)


def process_solicitacao(solicitacao):
    print "Processando solicitação: %s" % solicitacao.subject
    
    # Compilar um branch
    m = re.search("[Cc]ompile.*branch ([_a-z0-9]*).*", solicitacao.subject)
    if (m and m.group(1)):
        send_email(solicitacao, build_branch(solicitacao, m.group(1))) 
        return

    # Não entendi a mensagem!
    send_email(solicitacao, """
        Infelizmente não consegui entender a solicitação! Tente novamente, reformulando o subject do email.
        As solicitações que entendo são:
        - Compile o branch *nome* para mim.
        """)
    pass


def send_email(solicitacao, message):
    global user, passwd, smtpserver
    message = message + "\r\n--\r\nSistema de Build"
    msg = ("Content-Type: text/plain; charset=ISO-8859-1\r\nFrom: %s\r\nTo: %s\r\nCC: %s\r\nSubject: Re: %s\r\n\r\n%s" % 
        (user, solicitacao.fromaddr, ", ".join(solicitacao.ccs), solicitacao.subject, message))
    server = smtplib.SMTP(smtpserver)
    server.login(user, passwd)
    server.sendmail(user, solicitacao.fromaddr, msg)
    server.quit()


if __name__ == "__main__":
    while (1):
        try:
            emails = get_emails();
            for e in emails:
                process_solicitacao(e)
        except Exception, e:
            print "Erro ao obter solicitações. %s" % e
        time.sleep(60)


