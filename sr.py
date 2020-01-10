import speech_recognition as sr
from time import sleep, time
import audioop
import sys


def energy(recognizer: sr.Recognizer, audio: sr.AudioData):
    e = audioop.rms(audio.frame_data, audio.sample_width)  # energy of the audio signal
    seconds_per_buffer = len(audio.frame_data) / audio.sample_rate / audio.sample_width
    # dynamically adjust the energy threshold using asymmetric weighted average
    # account for different chunk sizes and rates
    damping = recognizer.dynamic_energy_adjustment_damping ** seconds_per_buffer
    target_energy = e * recognizer.dynamic_energy_ratio
    energy_threshold = recognizer.energy_threshold * damping + target_energy * (1 - damping)
    return e, energy_threshold


def on_listen(recognizer: sr.Recognizer, audio: sr.AudioData):
    l = len(audio.frame_data) / audio.sample_rate / audio.sample_width
    e, tr = energy(recognizer, audio)
    print(f'+{l:6.2f}s {e:6.2f}; [{recognizer.energy_threshold:.2f}]: ', end='')
    try:
        t = time()
        text = recognizer.recognize_google(audio, language='ru-RU').lower()
    except sr.UnknownValueError as e:
        print()
    else:
        dt = time() - t
        print(f'Вы сказали ({dt:5.2f}s): {text}')


r = sr.Recognizer()
with sr.Microphone() as source:
    # r.pause_threshold = 1
    r.dynamic_energy_ratio = 3  # 1.5
    phrase_time_limit = 30
    print('Тихо...')
    r.adjust_for_ambient_noise(source, duration=1)
    print(f'Уровень шума: {r.energy_threshold}')

print('Нажмите Enter для выхода...')
print('Говорите...')
stop = r.listen_in_background(sr.Microphone(), on_listen, phrase_time_limit=phrase_time_limit)
input()
stop()
print('Стоп.')
