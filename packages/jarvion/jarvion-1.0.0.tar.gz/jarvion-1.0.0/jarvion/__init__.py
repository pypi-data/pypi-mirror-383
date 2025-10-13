"""
jarvisai.core
Main Jarvis class:
- real-time listening (SpeechRecognition -> Google free recognizer)
- provider abstraction (OpenAI, Gemini, both)
- streaming OpenAI, chunked Gemini
- ElevenLabs TTS + caching or pyttsx3 fallback
- interrupt handling to stop TTS when user speaks
"""

import os
import time
import threading
import queue
import tempfile
import hashlib
import json
import requests
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3

# command = None
# openai_model = None
# gemini_model = None
# openai_key = None
# gemini_key = None
# ai_provider = None
# elevenlabs_key = None
# eleven_voice = None
# speak_chunk_threshold = None
# interrupt_on_user_speech = None
# tts_cache_dir = None

def set_command(cmd):
    global command
    command = cmd
    return command

# Optional imports will be attempted only when needed
try:
    import openai
except Exception:
    openai = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

# ---------------- Config dataclass ----------------
class Config:
    global openai_key, openai_model, gemini_key, gemini_model, ai_provider
    global elevenlabs_key, eleven_voice, speak_chunk_threshold, interrupt_on_user_speech, tts_cache_dir
    def __init__(
        self,
        openai_key=None,
        openai_model=None,
        gemini_key=None,
        gemini_model=None,
        ai_provider=None,
        elevenlabs_key=None,
        eleven_voice=None,
        speak_chunk_threshold=None,
        interrupt_on_user_speech=None,
        tts_cache_dir=None,
    ):
        # keys and models
        self.openai_key = openai_key if openai_key is not None else globals().get('openai_key') or os.getenv("OPENAI_API_KEY")
        self.openai_model = openai_model if openai_model is not None else globals().get('openai_model')
        self.gemini_key = gemini_key if gemini_key is not None else globals().get('gemini_key') or os.getenv("GEMINI_API_KEY")
        self.gemini_model = gemini_model if gemini_model is not None else globals().get('gemini_model')
        self.ai_provider = (ai_provider if ai_provider is not None else globals().get('ai_provider') or os.getenv("AI_PROVIDER") or "").lower()
        self.elevenlabs_key = elevenlabs_key if elevenlabs_key is not None else globals().get('elevenlabs_key') or os.getenv("ELEVENLABS_API_KEY")
        self.eleven_voice = eleven_voice if eleven_voice is not None else globals().get('eleven_voice') or os.getenv("ELEVEN_VOICE", "alloy")
        # behavior
        self.speak_chunk_threshold = speak_chunk_threshold if speak_chunk_threshold is not None else globals().get('speak_chunk_threshold')
        self.interrupt_on_user_speech = interrupt_on_user_speech if interrupt_on_user_speech is not None else globals().get('interrupt_on_user_speech')
        self.tts_cache_dir = tts_cache_dir if tts_cache_dir is not None else globals().get('tts_cache_dir') or os.path.join(tempfile.gettempdir(), "jarvis_tts_cache")

# ---------------- Jarvis class ----------------
class Jarvis:
    def __init__(self, config: Config = None):
        self.cfg = config or Config()
        # provider selection
        self.use_openai = bool(self.cfg.openai_key) and (self.cfg.ai_provider in ("", "openai", "both") or (self.cfg.ai_provider == "openai"))
        self.use_gemini = bool(self.cfg.gemini_key) and (self.cfg.ai_provider in ("", "gemini", "both") or (self.cfg.ai_provider == "gemini"))
        if not (self.use_openai or self.use_gemini):
            # fallback preference: openai then gemini
            if self.cfg.openai_key:
                self.use_openai = True
            elif self.cfg.gemini_key:
                self.use_gemini = True

        # init SDKs only if chosen
        if self.use_openai:
            if openai is None:
                raise RuntimeError("openai package is required for OpenAI provider. pip install openai")
            openai.api_key = self.cfg.openai_key

        if self.use_gemini:
            if genai is None:
                raise RuntimeError("google-generativeai package required for Gemini. pip install google-generativeai")
            genai.configure(api_key=self.cfg.gemini_key)

        # queues & control
        self.user_text_q = queue.Queue()
        self.assistant_q = queue.Queue()
        self._interrupt_event = threading.Event()
        self._stop_event = threading.Event()

        # speech recognition
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        # TTS engine (pyttsx3 fallback)
        self.pytt_engine = pyttsx3.init()
        self.pytt_engine.setProperty("rate", 165)

        # create cache dir
        os.makedirs(self.cfg.tts_cache_dir, exist_ok=True)

        # threads
        self.listener_thread = threading.Thread(target=self._background_listen, daemon=True)
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)

    # ---------------- Public API ----------------
    def start(self):
        """Start background listener and TTS player."""
        self._stop_event.clear()
        self.listener_thread.start()
        self.tts_thread.start()
        print("[Jarvis] started.")

    def stop(self):
        """Stop Jarvis gracefully."""
        self._stop_event.set()
        # allow threads to break loops
        self.user_text_q.put(None)
        self.assistant_q.put(None)
        # try to stop playback
        try:
            sd.stop()
        except Exception:
            pass
        try:
            self.pytt_engine.stop()
        except Exception:
            pass
        print("[Jarvis] stopping...")

    def send_text(self, text: str):
        """Send text programmatically to be processed by the AI (like user speaking)."""
        if text:
            self.user_text_q.put(text)
    # ---------------- Internals ----------------
    def _background_listen(self):
        """Continuously listen in background and enqueue recognized phrases into user_text_q."""
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("[Jarvis] Listening... (say 'exit' to stop)")
            while not self._stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=6)
                except sr.WaitTimeoutError:
                    continue
                # signal interrupt (stop TTS)
                self._interrupt_event.set()
                # process recognition in worker so loop continues
                threading.Thread(target=self._recognize_and_enqueue, args=(audio,), daemon=True).start()
                # small debounce
                time.sleep(0.05)

    def _recognize_and_enqueue(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            text = text.strip()
            if text:
                command = text
                set_command(command)
                print(f"\n[User]: {text}")
                if text.lower().strip() in ("exit", "quit", "stop"):
                    self.stop()
                    return
                self.user_text_q.put(text)
                # spawn processing thread
                threading.Thread(target=self._process_user_text, args=(text,), daemon=True).start()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("[Jarvis] STT error:", e)
        finally:
            # resume speaking after short delay
            def clear_interrupt():
                time.sleep(0.6)
                self._interrupt_event.clear()
            threading.Thread(target=clear_interrupt, daemon=True).start()

    def _process_user_text(self, text):
        """Send text to selected provider(s) and stream results into assistant queue."""
        system_prompt = "You are Jarvis, a concise helpful assistant. Keep responses short and conversational."
        provider = self.cfg.ai_provider or ("both" if (self.use_openai and self.use_gemini) else ("openai" if self.use_openai else "gemini"))

        if provider == "openai" and self.use_openai:
            self._openai_stream(text, system_prompt)
        elif provider == "gemini" and self.use_gemini:
            self._gemini_chunked(text, system_prompt)
        elif provider == "both":
            # run both in parallel
            if self.use_openai:
                threading.Thread(target=self._openai_stream, args=(text, system_prompt), daemon=True).start()
            if self.use_gemini:
                threading.Thread(target=self._gemini_chunked, args=(text, system_prompt), daemon=True).start()
        else:
            # fallback
            if self.use_openai:
                self._openai_stream(text, system_prompt)
            elif self.use_gemini:
                self._gemini_chunked(text, system_prompt)

    # ---------- OpenAI streaming ----------
    def _openai_stream(self, user_text, system_prompt):
        if not self.use_openai:
            return
        try:
            resp = openai.ChatCompletion.create(
                model=self.cfg.openai_model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
                temperature=0.6,
                stream=True,
            )
            buffer = ""
            for chunk in resp:
                delta = chunk.get("choices", [])[0].get("delta", {})
                piece = delta.get("content", "")
                if piece:
                    # feed assistant queue for TTS
                    self.assistant_q.put(piece)
                    # also print progressively
                    print(piece, end="", flush=True)
            print()
        except Exception as e:
            print("[Jarvis] OpenAI error:", e)
            self.assistant_q.put("Sorry, I couldn't get a response from OpenAI.")

    # ---------- Gemini (chunked) ----------
    def _gemini_chunked(self, user_text, system_prompt):
        if not self.use_gemini:
            return
        try:
            model = genai.GenerativeModel(self.cfg.gemini_model)
            prompt = f"{system_prompt}\nUser: {user_text}"
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or str(response)
            # stream in small chunks to simulate streaming
            chunk_size = 8
            for i in range(0, len(text), chunk_size):
                piece = text[i:i + chunk_size]
                self.assistant_q.put(piece)
                print(piece, end="", flush=True)
                time.sleep(0.01)
        except Exception as e:
            print("[Jarvis] Gemini error:", e)
            self.assistant_q.put("Sorry, I couldn't get a response from Gemini.")

    # ---------- ElevenLabs TTS helper ----------
    def _elevenlabs_tts_bytes(self, text, voice=None):
        key = self.cfg.elevenlabs_key
        if not key:
            raise RuntimeError("ElevenLabs key not set")
        voice = voice or self.cfg.eleven_voice
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {"xi-api-key": key, "Content-Type": "application/json"}
        payload = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"ElevenLabs TTS failed: {resp.status_code} {resp.text}")
        return resp.content

    def _tts_cache_get_path(self, text, voice):
        # hash by text + voice
        h = hashlib.sha256((voice + "|" + text).encode("utf-8")).hexdigest()
        return os.path.join(self.cfg.tts_cache_dir, f"{h}.wav")

    # ---------- TTS worker ----------
    def _tts_worker(self):
        """Consume assistant_q and play TTS in chunks. Honors interrupt_event to stop playback."""
        buffer = ""
        while not self._stop_event.is_set():
            try:
                item = self.assistant_q.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                break
            buffer += item
            # play when buffer big enough or ends in punctuation
            if len(buffer) >= self.cfg.speak_chunk_threshold or buffer.endswith((".", "?", "!", "\n")):
                text_to_speak = buffer.strip()
                buffer = ""
                if not text_to_speak:
                    continue
                # if user speaking, postpone
                if self.cfg.interrupt_on_user_speech and self._interrupt_event.is_set():
                    continue
                # attempt ElevenLabs if available
                if self.cfg.elevenlabs_key:
                    # check cache
                    cache_path = self._tts_cache_get_path(text_to_speak, self.cfg.eleven_voice)
                    if os.path.exists(cache_path):
                        try:
                            data, rate = sf.read(cache_path, dtype="float32")
                            sd.play(data, rate)
                            while sd.get_stream() and not self._interrupt_event.is_set():
                                time.sleep(0.05)
                            # if self._interrupt_event.is_set():
                            #     sd.stop()
                            #     continue
                        except Exception as e:
                            print("[Jarvis] TTS playback error (cache):", e)
                    else:
                        try:
                            audio_bytes = self._elevenlabs_tts_bytes(text_to_speak, voice=self.cfg.eleven_voice)
                            # write cache
                            with open(cache_path, "wb") as f:
                                f.write(audio_bytes)
                            # play
                            data, rate = sf.read(cache_path, dtype="float32")
                            sd.play(data, rate)
                            while sd.get_stream() and not self._interrupt_event.is_set():
                                time.sleep(0.05)
                            # if self._interrupt_event.is_set():
                            #     sd.stop()
                            #     continue
                        except Exception as e:
                            print("[Jarvis] ElevenLabs TTS failed, falling back to pyttsx3:", e)
                            # fallback to pyttsx3
                            try:
                                # if self._interrupt_event.is_set():
                                #     continue
                                self.pytt_engine.say(text_to_speak)
                                self.pytt_engine.runAndWait()
                            except Exception as e2:
                                print("[Jarvis] pyttsx3 error:", e2)
                else:
                    # pyttsx3 fallback
                    try:
                        # if self._interrupt_event.is_set():
                        #     continue
                        self.pytt_engine.say(text_to_speak)
                        self.pytt_engine.runAndWait()
                    except Exception as e:
                        print("[Jarvis] pyttsx3 error:", e)

    # ---------------- Utility ----------------
    def is_running(self):
        return not self._stop_event.is_set()