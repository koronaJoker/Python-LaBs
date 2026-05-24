from gtts import gTTS

def make_voice_report(text):
    tts = gTTS(text=text, lang="ru")
    tts.save("report.mp3")
