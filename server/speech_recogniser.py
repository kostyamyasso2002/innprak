import wave
import json
from vosk import Model, KaldiRecognizer
import vosk
from moviepy.editor import VideoFileClip, AudioFileClip
import moviepy.editor as mp
from tqdm import tqdm


def decouple_audio(video_name, audio_name):
    clip = VideoFileClip(video_name)
    original_audio = clip.audio
    original_audio.write_audiofile(audio_name, ffmpeg_params=["-ac", "1"])
    clip.reader.__del__()
    clip.audio.reader.__del__()


def transcript_audio(audio_name: str,
                     model_path: str = "model/vosk-model-small-ru-0.22") -> dict:
    vosk.SetLogLevel(-1)

    wf = wave.open(audio_name, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print(wf.getnchannels(), wf.getsampwidth(), wf.getcomptype())
        raise Exception("Audio should be in WAV format")

    model = Model(model_path)

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    ans = {'result': []}
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            try:
                dop = json.loads(rec.Result())['result']
            except KeyError:
                dop = []
            ans['result'].extend(dop)
        else:
            pass
    try:
        dop = json.loads(rec.FinalResult())['result']
    except KeyError:
        dop = []
    ans['result'].extend(dop)
    return ans


stopwords = frozenset(['ну', 'короче'])


def get_left_fragments(transcript: list, indent: float = 0.2) -> list:
    ans = []
    for token in transcript:
        if token['word'] in stopwords:
            continue
        if len(ans) == 0:
            ans.append((token['start'] - indent, token['end'] + indent))
            continue
        if ans[len(ans) - 1][1] >= token['start'] - indent:
            last = ans.pop()
            assert type(last) == tuple
            ans.append((last[0], token['end'] + indent))
        else:
            ans.append((token['start'] - indent, token['end'] + indent))
    return ans


def process_video(input_video_path: str, output_video_path: str, left_fragments: list):
    clip = VideoFileClip(input_video_path)
    clips = []
    print("Start processing")
    for i in tqdm(left_fragments):
        clips.append(clip.subclip(max(i[0], 0), min(i[1], clip.duration)))
    print("Middle processing")
    mp.concatenate_videoclips(clips).write_videofile(output_video_path)
    print("Finish processing")
