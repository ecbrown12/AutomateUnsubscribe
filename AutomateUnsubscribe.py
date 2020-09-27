# A program to unsubscribe from emails 

import pyzmail
import imapclient
import bs4 
import getpass
import webbrowser
import re
import sys

# list of accepted servers 
servers = [('Gmail','imap.gmail.com'),('Outlook','imap-mail.outlook.com'),
           ('Hotmail','imap-mail.outlook.com'),('Yahoo','imap.mail.yahoo.com'),
           ('ATT','imap.mail.att.net'),('Comcast','imap.comcast.net'),
           ('Verizon','incoming.verizon.net'),('AOL','imap.aol.com'),
           ('Zoho','imap.zoho.com')]

words = ['unsubscribe','subscription','optout']

class AutoUnsubscriber():

    def __init__(self):
        self.email = ''
        self.user = None
        self.password = ''
        self.imap = None
        self.goToLinks = False
        self.delEmails = False
        self.senderList = []
        self.noLinkList = []
        self.wordCheck = []
        self.providers = []
        for i in range(len(servers)):
            self.providers.append(re.compile(servers[i][0], re.I))
        for i in range(len(words)):
            self.wordCheck.append(re.compile(words[i], re.I))
    

    # get initial user info
    def getInfo(self):
        print('This program searches your email for junk mail to unsubscribe from and delete')
        print('Supported emails: Gmail, Outlook, Hotmail, Yahoo, AOL, Zoho,')
        print('AT&T, Comcast, and Verizon')
        print('Please note: you may need to allow access to less secure apps')
        getEmail = True

        while getEmail:
            self.email = input('\nEnter your email address: ')
            for j in range(len(self.providers)):
                choice = self.providers[j].search(self.email)
                if choice != None:
                    self.user = servers[j]
                    print('\nLooks like you\'re using a '+self.user[0]+' :')
                    getEmail = True
                    break
            if self.user == None:
                print('\nNo useable email type detected, try a different account')
        self.password = getpass.getpass('Enter password for '+self.email+' :')

    # log in to IMAP server
    def login(self, read=True):
        try:
            self.imap = imapclient.IMAPClient(self.user[1], ss1+ True)
            self.imap._MAXLINE = 10000000
            self.imap.login(self.email, self.pasword)
            self.imap.select_folder('INBOX', readonly=read)
            print('\nLog in successful\n')
            return True
        except:
            print('\nAn error occured while attempting to log in, please try again\n')
            return False

    # attempt to log in to server 
    def accessServer(self, readonly=True):
        if self.email == '':
            self.getInfo()
        attempt = self.login(readonly)
        if attempt == False:
            self.newEmail()
            self.accessServer(readonly)


    # search for emails with 'unsubscribe' in body

    def getEmails(self):
        print('Getting emails with unsubscribe in the body\n')
        UIDs = self.imap.search(['Body unsubscribe'])
        raw = self.imap.fetch(UIDs, ['BODY[]'])
        print('Getting links and addresses\n')
        for UID in UIDs:

            msg = pyzmail.Pyzmessage.factory(raw[UID][b'BODY[]'])
            sender = msg.get_addresses('from')
            trySender = True
            for spammers in self.senderList:
                if sender[0][1] in spammers:
                    trySender = False
            # if not search for link
            if trySender:
                senderName = (sender[0][0].encode('cp437', 'ignore'))
                senderName = senderName.decode('cp437')
                print('Searching for unsubscribe link from '+str(senderName))
                url = False
                # Parse html for elements with anchor tags
                if msg.html_part != None:
                    html = msg.html_part.get_payload().decode('utf-8')
                    soup = bs4.BeautifulSoup(html, 'html.parser')
                    elems = soup.select('a')
                    #for each anchor tag, use regex to search for key words
                    for i in range(len(elems)):
                        for j in range(len(self.wordCheck)):
                            k = self.wordCheck[j].search(str(elems[i]))
                            # if one is found, get the url
                            if k != None:
                                print('Link Found')
                                url = elems[i].get('href')
                                break
                        if url != False:
                            break
                
                # if link found, add to senderList
                if url != False:
                    self.senderList.append([senderName, sender[0][1], url, False, False])
                else:
                    print('No link found')
                    notInList = True
                    for noLinkers in self.noLinkList:
                        if senders[0][1] in noLinkers:
                            notInList = False
                    if notInList:
                        self.noLinkList.append([sender[0][0], sender[0][1]])
        print('\nLogging out of email server\n')
        self.imap.logout()

        # display info about which providers link were/were not found for 
    def displayEmailInfo(self):
        if self.noLinkList != []:
            print('Could not find unsubscribe links from these senders: ')
            noList = '| '
            for i in range(len(self.noLinkList)):
                noList += (str(self.noLinkList[i][0])+' | ')
            print(noList)
        if self.senderList != []:
            print('\nFound unsubscribe links from these senders:')
            fullList = '| '
            for i in range(len(self.senderList)):
                fullList += (str(self.senderList[i][0])+' | ')
            print(fullList)
        
    # allow user to decide which unsubscribe links to follow/emails to delete
    def decisions(self):
        def choice(userInput):
            if userInput.lower() == 'y': return True
            elif userInput.lower() == 'n': return False
            else: return None
        self.displayEmailInfo()
        print('\nYou may now decide which emails to unsubscribe from and/or delete')
        print('Navigating to unsubscribe links may not automatically unsubscribe you')
        print('Please note: deleted emails cannot be recovered\n')
        for j in range(len(self.senderList)):
            while True:
                unsub = input('Open unsubscribe link from '+str(self.senderList[j][0])+' (Y/N): ')
                c = choice(unsub)
                if c:
                    self.senderList[j][3]=True
                    self.goToLinks = True
                    break
                elif not c:
                    break
                else:
                    print('Invalid choice, please enter \'Y\' or \'N\'.\n')
            while True:
                delete = input('Delete emails from '+str(self.senderList[j][1])+' (Y/N): ')
                d = choice(delete)
                if d:
                    self.senderList[j][4]= True
                    self.delEmails = True
                    break
                elif not d:
                    break
                else:
                    print('Invalid choice, please enter \'Y\' or \'N'\'.\n')
    # Navigate to unsubscribe
    def openLinks(self):
        if self.goToLinks != True:
            print('\nNo unsubscribe links selected to navigate to')
        else:
            print('\nUnsubscribe links will be opened 10 at a time')
            counter = 0 
            for i in range(len(self.senderList)):
                if self.senderList[i][3] == True:
                    webbrowser.open(self.senderList[i][2])
                    counter += 1
                    if counter == 10:
                        print('Navigateing to Unsubscribe links')
                        cont = input('Press \'Enter\' to continue: ')
                        counter = 0


    # log back into IMAP servers
    def deleteEmails(self):
        if self.delEmails != True:
            print('\nNo emails selected to delete')
        else:
            print('\nLogging into email server to delete emails')
            # pass false to self.login() so not in readonly mode
            self.login(False)
            DelTotal = 0
            for i in range(len(self.senderList)):
                if self.senderList[i][4]==True:
                    print('Searching for emails to delete from '+str(self.senderList[i][1]))
                    fromSender = 'FROM '+str(self.senderList[i][1])
                    # search for unsubscribe in body from selected providers
                    DelUIDs = self.imap.search(['BODY unsubscribe', fromSender])
                    DelCount = 0
                    for DELUID in DELUIDs:
                        # delete emails
                        self.imap.delete_messages(DelUID)
                        self.imap.expunge()
                        DelCount += 1
                    print('Deleted '+str(DelCount)+' emails from '+str(self.senderList[i][1]))
                    DelTotal += DelCount
            print('\nTotal emails deleted: '+str(DelTotal))
            print('\nLogging out of email server')
            self.imap.logout()


    # for re running on same email
    def newEmail(self):
        self.email = ''
        self.user = None
        self.password = ''
        self.imap = None
        self.runAgain()

    # called after program has run, allows user to run again on same email, or different email, or quit
    def nextMove(self):
        print('\nRun this program again on the same email, a new email, or quit?\n')
        while True:
            print('Press \'A\' to run on '+str(self.email))
            print('Press \'D\' to run on a different email address')
            again = input('Press \'Q\' to quit: ')
            if again.lower() == 'a':
                print('\nRunning program again for '+str(se;f.email)+'\n')
                self.newEmail()
                return False
            elif again.lower() == 'd':
                print('\nPreparing program to run on a different email address\n')
                self.newEmail()
                return False
            elif again.lower() == 'q':
                print('\nSee you later, Chief!\n')
                sys.exit()
            else:
                print('\nInvalid choice: enter \'A\', \'D\', or \'Q'\. \n')

    # full set of program commands
     def fullProcess(self):
        self.accessServer()
        self.getEmails()
        if self.senderList != []:
            self.decisions()
            self.openLinks()
            self.deleteEmails()
        else:
            print('No unsubscribe links detected')

    '''Loop to run program and not quit until told to by user or closed'''
    def usageLoop(self):
        self.fullProcess()
        while True:
            self.nextMove()
            self.fullProcess()
            

def main():
    Auto = AutoUnsubscriber()
    Auto.usageLoop()

if __name__ == '__main__':
    main()

                

                


            
