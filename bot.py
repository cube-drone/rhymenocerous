#! /usr/bin/env python
#

#libs
from ircbot import SingleServerIRCBot
import irclib
import sys
import re
import time
import datetime
import rhyme

import config

class Rhymer(irclib.SimpleIRCClient):
    
    def __init__(self, server, port, channel, nick): 
    
        irclib.SimpleIRCClient.__init__(self)
        
        #IRC details
        self.server = server
        self.port = port
        self.target = channel
        self.channel = channel
        self.nick = nick
        
        #Regexes
        self.nick_reg = re.compile("^" + nick + "[:,](?iu)")
        
        self.ircobj.delayed_commands.append( (time.time()+5, self._no_ping, [] ) )
    
        self.connect(self.server, self.port, self.nick)
        self.last_ping = 0

    
    def _no_ping(self):
        if self.last_ping >= 1200:
            raise irclib.ServerNotConnectedError
        else:
            self.last_ping += 10
        self.ircobj.delayed_commands.append( (time.time()+10, self._no_ping, [] ) )


    def _dispatcher(self, c, e):
    # This determines how a new event is handled. 
        if(e.eventtype() == "pubmsg"):
            try: 
                source = e.source().split("!")[0]
            except IndexError:
                source = ""
            try:
                text = e.arguments()[0]
            except IndexError:
                text = ""
            
        m = "on_" + e.eventtype()   
        if hasattr(self, m):
            getattr(self, m)(c, e)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, connection, event):
        if irclib.is_channel(self.target):
            connection.join(self.target)

    def on_disconnect(self, connection, event):
        connection.disconnect()
        raise irclib.ServerNotConnectedError

    def on_ping(self, connection, event):
		self.last_ping = 0

    def on_pubmsg(self, connection, event):
        text = event.arguments()[0]
        
        try: 
            source = event.source().split("!")[0]
        except IndexError:
            source = ""

        # If you talk to the bot, this is how he responds.
        if self.nick_reg.search(text):
            if len(text.split(":")) > 1:
                message = ":".join(text.split(":")[1:])
                connection.privmsg(self.channel, source+": "+rhyme.rhyme(message)) 
            else:
                print text

def main():
    irc_settings = config.config("irc_config.txt")
    
    c = Rhymer(
                irc_settings["server"], 
                int(irc_settings["port"]), 
                irc_settings["channel"], 
                irc_settings["nick"] )
    c.start()
    
if __name__ == "__main__":
    irc_settings = config.config("irc_config.txt")
    reconnect_interval = irc_settings["reconnect"]
    while True:
        try:
            main()
        except irclib.ServerNotConnectedError:
            print "Server Not Connected! Let's try again!"             
            time.sleep(float(reconnect_interval))
            
