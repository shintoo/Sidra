#!/usr/bin/env python

from __future__ import print_function

import os
import subprocess
import random
import webbrowser
import re
from datetime import datetime
from gtts import gTTS
import speech_recognition as sr
import wikipedia as wiki

from sir import SIR
from cmd import cmd


# TODO
#   * redesign - design whole structure bottom-up, split into modules - do this before anything else
#   * add weather getting function      do this next
#   * add google calendar API
#   * add wikipedia query               DONE
#   * add dictionary api                then maybe do this? wikipedia is pretty good though
#   # add ez functions (timers, reminders)
#   * add news headline (maybe newscure?)
#   * create a DSL for writing custom scripts without having to edit python file, and make it easy to write in
#
#  post pi zero w arrival --
#   * make a status led
#   * make a voice led
#       this one might be a bit hard, try getting current output decibels from alsa somehow

class Sidra(object):
    greetings = [
            'Hi.',
            'Hello.',
            'Hey.',
            'What\'s up?',
            'How\'s it going?'
            ]

    prompts = [
            'What can I do for you?',
            'How can I help?',
            'What\'s up?',
            'What do you need?'
            ]

    onits = [
            'Ahn it.',
            'I can do that for you.',
            'Sure, one sec.',
            'Sure, one second.',
            'Just a moment.'
            ]

    goodbyes = [
            'See you.',
            'Goodbye.',
            'Catch you later.',
            'Bye now.'
            ]

    understoods = [
            'Understood.',
            'Got it.',
            'Okay.'
            ]

    affirmatives = [
            'Affirmative.',
            'Yes.',
            'Yeah.',
            'Correct.'
            ]

    negatives = [
            'Negative.',
            'No.',
            'Nope.'
            ]

    uncertains = [
            'I\'m not sure.',
            'I don\'t know.',
            'That is uncertain.',
            'Not sure.'
            ]

    query_string = 'https://www.google.com/search?q='   
    
    def __init__(self, listen_mode='text', voice_mode='speech', name='Sidra', debug=False):
        self.name = name
        self.running = False
        self.debug = False
        self.listen_mode = voice_mode # text | speech
        self.voice_mode = voice_mode # text | speech
        self.recognizer = sr.Recognizer()
        query_string = 'https://www.google.com/search?q='   

        self.sir = SIR()

        self.rules = (
            # SIR directives
            ( "remember (that )?(every|any|an|a) (.*) is (a|an) (.*)",   lambda g: self.remember(g, "2s4|4S2")),
            ( "remember (that )?(.*) is (a|an) (.*)",                    lambda g: self.remember(g, "1m3|3M1")),
            ( "remember (that )?(.*) is (.*)",                           lambda g: self.remember(g, "1e2|2e1")),
            ( "remember (that )?(every|any|an|a) (.*) owns (a|an) (.*)", lambda g: self.remember(g, "2p4|4P2")),
            ( "remember (that )?(.*) owns (a|an) (.*)",                  lambda g: self.remember(g, "1p3|3P1")),

            # SIR queries
            ( "is (every|an|a) (.*) (a|an) (.*)",                        lambda g: self.recall(g, "1e*s*3")),
            ( "is (.*) (a|an) (.*)",                                     lambda g: self.recall(g, "0e*ms*2")),
            ( "does (every|an|a) (.*) own (a|an) (.*)",                  lambda g: self.recall(g, "1e*ms*ps*3")),
            ( "does any (.*) own (a|an) (.*)",                           lambda g: self.recall(g, "0S*Me*ps*2")),
            ( "does (.*) own (a|an) (.*)",                               lambda g: self.recall(g, "0e*ms*ps*2")),

            # Fun things
            ( "(hi|hello|hey)(.*)",                                      lambda g: self.greet(g)),
            ( "say (.*)",                                                lambda g: self.say(g)),
            ( "search (for )?(.*)",                                      lambda g: self.search(g)),
            ( "tell (me )?a (joke|fortune|quote)",                       lambda g: self.tell_a(g)),
            ( "(what's|tell me) the (weather|date|time)",                lambda g: self.tell_the(g)),
            ( "what (day|time) is it",                                   lambda g: self.tell_the((' ',) + g)),
            ( "what does (.*) mean",                                     lambda g: self.dictionary(g)),
            ( "what is (a)?(.*)",                                        lambda g: self.wikipedia(g)),

            # Debug utils
            ( "voice-mode (text|speech)",                                lambda g: self.set_voice_mode(g)),
            ( "input-mode (text|speech)",                                lambda g: self.set_input_mode(g)),
            ( "dump (.*)",                                               lambda g: self.dump(g)),
            ( "debug",                                                   lambda g: self.set_debug(not self.debug)),
            ( "erase memory",                                            lambda g: self.erase_memory()),

            # etc
            ( "(help|what can you do|what are you capable of)",          lambda g: self.help()),
            ( "list all functions",                                      lambda g: self.list_functions()),
            ( "(quit|shut down|turn off)",                               lambda g: self.quit())
         ) 

    def list_functions(self):
        self.say('I can provide jokes, fortunes, quotes, the date, the time, and definitions. More to come soon.')

    def handle(self, inp):
        '''Find which rule applies to input and perform that action'''
        inp = re.sub("  *", " ", inp.strip().lower())

        self.debug_print('handle: ' + inp)

        for pattern, action in self.rules:
            match = re.match(pattern, inp)
            if match:
                self.debug_print('handle: ' + str(match.groups()) + pattern)
                action(match.groups())
                return

        self.say('Sorry, I didn\'t quite get that.')

    def wikipedia(self, g):
        answer = wiki.summary(g[2], sentences=1)
        self.debug_print(answer)
        self.say(answer)
    
    def dictionary(self, g):
        self.say('Sorry, I can\'t do that yet.')

    def greet(self, g):
        self.say(random.choice(self.greetings))

    def get_input(self):
        if self.mode == 'text':
            return self.text_input()
        return self.voice_input()

    def say(self, g):
        text = ''.join(g).encode('ascii', errors='ignore')

        if self.debug:
            print('[*] say: \"{0}\"'.format(text))
 
        if self.voice_mode == 'text':
            print(text)
            return

        tts = gTTS(text=text, lang='en')
        tts.save('.sidra_response.mp3')
        os.system("ffplay -hide_banner -autoexit -loglevel panic -nodisp .sidra_response.mp3 > /dev/null")

    def search(self, g):
        query = ''.join(g)
        self.say('Here\'s your search on ' + query + '.')
        webbrowser.open(self.query_string + query)

    def get_weather(self):
        return 'I hope it\'s sunny!'

    def remember(self, g, connections_string):
        self.sir.add_fact(g, connections_string)
        self.say(random.choice(self.understoods))

    def recall(self, g, connections_string):
        if self.sir.get_path(g, connections_string):
            self.say(random.choice(self.affirmatives))
        else:
            self.say(random.choice(self.uncertains))

    def erase_memory(self):
        self.sir.clear()

    def tell_a(self, g):
        obj = g[1] # 0 is me|None, 1 is joke|fortune|fact

        if obj == 'joke':
            self.say(cmd('fortune riddles'))
        elif obj == 'fortune':
            self.say(cmd('fortune fortunes'))
        elif obj == 'quote':
            self.say(cmd('fortune literature'))

    def tell_the(self, g):
        obj = g[1]
        if obj == 'weather':
            self.say(self.get_weather())
        elif obj == 'date' or obj == 'day':
            self.say('Today is ' + datetime.now().strftime("%A, %B %d"))
        elif obj == 'time':
            self.say('Right now it\'s ' + datetime.now().strftime("%-I %M %p"))

    def set_input_mode(self, g):
        if g == 'text' or g == 'voice':
            self.listen_mode = g
            return
        self.listen_mode = g[0]

    def set_voice_mode(self, g):
        if g == 'text' or g == 'voice':
            self.voice_mode = g
            return
        self.voice_mode = g[0]

    def text_input(self):
        return raw_input(self.text_prompt())

    def text_prompt(self):
        return self.name + '> '

    def voice_input(self):
        audio = None
        text = None

        print('Say something.')

        while text == None:
            with sr.Microphone() as source:
                speech = self.recognizer.listen(source)

            try:
                text = self.recognizer.recognize_google(speech)
            except:
                pass

        self.debug_print('You said: \"' + text + "\"")


    def quit(self):
        self.say(random.choice(self.goodbyes))
        self.running = False

    def run(self):
        self.say(random.choice(self.prompts))
        self.running = True

        while self.running:
            if self.listen_mode == 'text':
                inp = self.text_input()
            else:
                inp = self.voice_input()
            self.debug_print('run: ' + inp)
            self.handle(inp)

    def set_debug(self, d):
        self.debug = d
        self.sir.debug = d

    def debug_print(self, text):
        if self.debug:
            print('[*] ' + text)

    def help(self):
        if self.voice_mode == 'text':
            for pattern, _ in self.rules:
                print(pattern)
        else:
            self.say('You can ask me for things like the time, what something means, or to remember a fact. For a full list of functions, say, \'List all functions.\'.')

    def dump(self, g):
        filepath = g.split(' ')[0]
        self.sir.dump(filepath)
        # dump anything else here too

if __name__ == '__main__':
    import sys
    sidra = []
    if len(sys.argv) == 3:
        sidra = Sidra(name='Sidra', listen_mode = sys.argv[1], voice_mode = sys.argv[2])
    else:
        sidra = Sidra(name='Sidra', listen_mode = 'speech', voice_mode = 'speech')

    sidra.run()
