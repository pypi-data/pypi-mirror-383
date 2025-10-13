from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
description = (HERE / "README.md").read_text(encoding="utf-8")

# with open("README.md", "r") as f:
#     description = f.read()

setup(
    name="jarvion",
    version="1.0.1",
    author="Salman Developer",
    author_email="salmanfareedchishty135@gmail.com",
    # description="A real-time, bilingual AI assistant that listens and talks like Jarvis using OpenAI and ElevenLabs APIs.",
    long_description=description,
    long_description_content_type="text/markdown",
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

