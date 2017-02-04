import json
import logging
import random

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
                txt_b = TextBlob(msg_txt)
                noun_tags = []
                adjc_tags = []
                verb_tags = []
                for sentence in txt_b.sentences:
                    for tag in sentence.tags:
                        if tag[1].startswith('NN'):
                            noun_tags.append(tag)
                        elif tag[1].startswith('JJ'):
                            adjc_tags.append(tag)
                        elif tag[1].startswith('VB'):
                            verb_tags.append(tag)
                logger.debug('nouns {}, adj {}, verbs {}'.format(noun_tags, adjc_tags, verb_tags))

                desired_len = random.choice([1, 2, 3])
                if len(noun_tags) > 0:
                    response = self.trump_corpus.gen_text([(seed[0]) for seed in noun_tags], desired_len)
                    if response is not None:
                        logger.debug('Sending noun message' + response)
                        self.msg_writer.send_message(event['channel'], response)
                        return
                if len(adjc_tags) > 0:
                    response = self.trump_corpus.gen_text([(seed[0]) for seed in adjc_tags], desired_len)
                    if response is not None:
                        logger.debug('Sending adj message' + response)
                        self.msg_writer.send_message(event['channel'], response)
                        return
                if len(verb_tags) > 0:
                    response = self.trump_corpus.gen_text([(seed[0]) for seed in verb_tags], desired_len)
                    if response is not None:
                        logger.debug('Sending verb message' + response)
                        self.msg_writer.send_message(event['channel'], response)
                        return


                # No seed match, so ask a question instead
                question = random.choice(random.choice(self.trump_corpus.nouns_to_quest.values()))
                self.msg_writer.send_message(event['channel'], question.raw)

    def _is_direct_message(self, channel_id):
        return channel_id.startswith('D')
