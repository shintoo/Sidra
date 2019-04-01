# Sidra

Sidra is a virtual assistant who can be interacted with using voice or text. Sidra serves as a testbed for dialogue-based interactions with minimal underlying frameworks. The purpose of Sidra is to build a virtual assistant whose functionality can easily be added to. (The actual purpose is just for fun, of course).

#### Memory and Reasoning System

Part of Sidra is the Semantic Information Retrieval System, which is a very simple and barebones approach to building a knowledge base from which basic inferences can be made. Relationships between sets can be declared to Sidra, and questions regarding those sets can be asked. 

This project is still in its early stages, and serves mostly as a playground for me than as an actually useful assistant.

#### Dependencies

* gtts (for text-to-speech)
* SpeechRecognition (for... speech recognition)
* Wikipedia (my fork) (for looking things up)
* fortune (for jokes, riddles, etc.)
* PyAudio (for voice input)
