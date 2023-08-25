import speech_recognition as sr

# Crie um objeto de reconhecimento
recognizer = sr.Recognizer()

# Carregue o arquivo de áudio
audio_file = "235180338131763200.wav"

# Abra o arquivo de áudio com o Recognizer
with sr.AudioFile(audio_file) as source:
    # Escute o áudio usando o método record()
    audio = recognizer.record(source)

    try:
        # Use a API de reconhecimento de fala para transcrever o áudio
        text = recognizer.recognize_google(audio, language="pt-BR")
        print("Texto transcrito:", text)
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio")
    except sr.RequestError as e:
        print(f"Erro na solicitação à API: {e}")
