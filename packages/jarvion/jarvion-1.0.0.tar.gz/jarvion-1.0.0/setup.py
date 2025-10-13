from setuptools import setup, find_packages

setup(
    name="jarvion",
    version="1.0.0",
    author="Salman Fareed Chishty",
    author_email="salmanfareedchishty135@gmail.com",
    description="A real-time, bilingual AI assistant that listens and talks like Jarvis using OpenAI and ElevenLabs APIs.",
)

packages = find_packages(),

install_requirements=[
    'os',
    'time',
    'threading',
    'queue',
    'tempfile',
    'hashlib',
    'json',
    'requests',
    'sounddevice',
    'soundfile', 
    'speech_recognition',
    'pyttsx3',
    'openai',
    'pyaudio',
    'elevenlabs',
    'pydub',
    'pywin32',
    'google.generativeai'
]

