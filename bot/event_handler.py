import json
import logging
import random
import Algorithmia

from textblob import TextBlob
from text_corpus import TextCorpus
from aylienapiclient import textapi
import tensorflow as tf

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
            self.msg_writer.send_message(event['channel'], "Let's make America great again!")
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

            #if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                #txt_b = TextBlob(msg_txt)
            
            #if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                # e.g. user typed: "@pybot tell me a joke!"
            if 'sentiment' in msg_txt:
                client = textapi.Client("a19bb245", "2623b77754833e2711998a0b0bdad9db")
                sentiment = client.Sentiment({"text": msg_txt})
                str = sentiment['polarity']
                str2 = " - %3.3f" % sentiment['polarity_confidence']
                str += str2
                self.msg_writer.send_message(event['channel'], str)
            elif 'tag' in msg_txt:
                #self.msg_writer.write_analytics(event['channel'], msg_txt)
                #if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                #txt_b = TextBlob(msg_txt)
#                   response = txt_b.tags
#                   self.msg_writer.send_message(event['channel'], response)
                count = 0;
                client = Algorithmia.client('sim3x6PzEv6m2icRR+23rqTTcOo1')            
                algo = client.algo('nlp/AutoTag/1.0.0')
                tags = algo.pipe(msg_txt)
                str_final = ""
                #print entities.result
                for item in tags.result:
                    if count == 0:
                        pass
                    else:
                        str_final += item
                        str_final += ", "
                    count = count + 1         
                self.msg_writer.send_message(event['channel'], str_final)
                #algo = client.algo('StanfordNLP/NamedEntityRecognition/0.2.0')
                #entities = algo.pipe(msg_txt)
            elif 'tensor' in msg_txt:
                hello = tf.constant('Hello, TensorFlow!')
                sess = tf.Session()
                value = sess.run(hello)
                self.msg_writer.send_message(event['channel'], value)
            elif 'entity' in msg_txt or 'Entity' in msg_txt or 'ENTITY' in msg_txt:
                client = Algorithmia.client('sim3x6PzEv6m2icRR+23rqTTcOo1')
                msg_txt = msg_txt.split(' ', 1)[1]
                algo = client.algo('StanfordNLP/NamedEntityRecognition/0.2.0')
                entities = algo.pipe(msg_txt)
                str_final = ""
                #print entities.result
                for inner_l in entities.result:
                    for item in inner_l:
                        str = item[0] + " - " + item[1] + ", "
                        str_final += str
                self.msg_writer.send_message(event['channel'], str_final)
                #algo = client.algo('StanfordNLP/NamedEntityRecognition/0.2.0')
                #entities = algo.pipe(msg_txt) 
            elif 'IMAGE' in msg_txt or 'Image' in msg_txt or 'image' in msg_txt:
                import re
                msg_txt = msg_txt.split(' ', 1)[1]
                msg_txt = msg_txt[1:-1]
                url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg_txt)
                url = ''.join(url)
                client = Algorithmia.client('sim3x6PzEv6m2icRR+23rqTTcOo1')
                algo = client.algo('deeplearning/InceptionNet/1.0.2')
                tags = algo.pipe(url).result['tags'][0]['class']
                import unicodedata
                tags = unicodedata.normalize('NFKD', tags).encode('ascii','ignore')
                self.msg_writer.send_message(event['channel'], tags)

            elif 'POS' in msg_txt:                
                from pattern.en import parse
                msg_txt = msg_txt.split(' ', 1)[1]
                s = msg_txt
                s = parse(s, relations=True, lemmata=True)
                self.msg_writer.send_message(event['channel'], s)
                
            elif 'classify' in msg_txt:
                client = textapi.Client("a19bb245", "2623b77754833e2711998a0b0bdad9db")
                classifications = client.ClassifyByTaxonomy({"text": msg_txt, "taxonomy": "iab-qag"})
                sent_str = ""
                for category in classifications['categories']:
                    sent_str += category['label'] + ", "
                sent_str = sent_str[:-1]
                response = sent_str
                self.msg_writer.send_message(event['channel'], response)

            elif 'hash' in msg_txt:
                client = textapi.Client("a19bb245", "2623b77754833e2711998a0b0bdad9db")
                msg_txt = msg_txt.split(' ', 1)[1]
                msg_txt = msg_txt[1:-1]
                url = msg_txt
                import re
                url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
                hashtags = client.Hashtags({"url": url})
                response = ', '.join(hashtags['hashtags'])
                str = ""
                list = response.split(' ')
                for i in range(0, 5):
                    str += list[i]
                    str += " "
                self.msg_writer.send_message(event['channel'], str)
                
            elif 'help' in msg_txt:
                self.msg_writer.write_help_message(event['channel'])
            elif 'joke' in msg_txt:
                self.msg_writer.write_joke(event['channel'])
            elif 'attachment' in msg_txt:
                self.msg_writer.demo_attachment(event['channel'])
            elif 'echo' in msg_txt:
                self.msg_writer.send_message(event['channel'], msg_txt)
            else:
                pass              

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
