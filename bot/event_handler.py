import json
import logging
import random
import Algorithmia

from textblob import TextBlob
from text_corpus import TextCorpus

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer, trump_corpus):
        self.clients = slack_clients
        self.msg_writer = msg_writer
        self.trump_corpus = trump_corpus

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
            self.msg_writer.send_message(event['channel'], "Let's make America great again!")
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself
        if not self.clients.is_message_from_me(event['user']):

            msg_txt = event['text']

            if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
#                txt_b = TextBlob(msg_txt)
#                response = txt_b.tags
#                self.msg_writer.send_message(event['channel'], response)
                client = Algorithmia.client('sim3x6PzEv6m2icRR+23rqTTcOo1')
                #response = txt_b.tags
                algo = client.algo('StanfordNLP/NamedEntityRecognition/0.2.0')
                entities = algo.pipe(msg_txt)
                response = entities.result[0][0][1]
                self.msg_writer.send_message(event['channel'], response)
                return

        def _is_direct_message(self, channel_id):
            return channel_id.startswith('D')
