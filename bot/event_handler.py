import json
import logging
import random
import Algorithmia
import nltk

from textblob import TextBlob
from text_corpus import TextCorpus
from aylienapiclient import textapi


logger = logging.getLogger(__name__)

class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer
        #self.trump_corpus = trump_corpus

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        # if event_type == 'error':
            # error
            # ignore self.msg_writer.write_error(event['channel'], json.dumps(event))
        if event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.send_message(event['channel'], "Welcome, Interact with the Tantal Slack bot ...")
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'file_shared':
            self.msg_writer.send_message(event['channel'], "Got your file, thanks!")            
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself
        if not self.clients.is_message_from_me(event['user']):

            msg_txt = event['text']

            if 'help' in msg_txt:
                self.msg_writer.write_help_message(event['channel'])
            elif 'joke' in msg_txt:
                self.msg_writer.write_joke(event['channel'])
            elif 'attachment' in msg_txt:
                self.msg_writer.demo_attachment(event['channel'])
            elif 'button' in msg_txt:
                self.msg_writer.demo_button(event['channel'])
            elif 'echo' in msg_txt:
                self.msg_writer.send_message(event['channel'], msg_txt)
            else:
                self.msg_writer.send_message(event['channel'], 'What do you want me to do? Find out more at http://nlpapps.nl')              

            return

        def _is_direct_message(self, channel_id):
            client = Algorithmia.client('sim3x6PzEv6m2icRR+23rqTTcOo1')
            algo = client.algo('StanfordNLP/NamedEntityRecognition/0.2.0')
            entities = algo.pipe(msg_txt)
            str_final = ""
            count = 0;
            for inner_l in entities.result:
                for item in inner_l:
                    if count == 0:
                        pass
                    else:
                        str = item[0] + " - " + item[1] + ", "
                    str_final += str
                    count = count + 1    
            self.msg_writer.send_message(event['channel'], str_final)
            return channel_id.startswith('D')
