import requests
import io
import sounddevice
import numpy as np
import soundfile as sf
from more_scores import score_gate

url = 'https://timeout2-ovo53lgliq-uc.a.run.app'
# method : 'POST'
# body : let formData = new FormData();
#   formData.append('file', new Blob([editor.getValue('\n')], {type : 'text/plain'}), 'file.sco');


def webrtc_request(score_str: str) -> np.ndarray:
    files = {"file": ('text/plain', score_str.encode('utf-8'), "file.sco"), 'pitch': (None, 48)}
    request = requests.post(url=url, files=files)
    bytesio = io.BytesIO(request.content)  #
    nparr, sr = sf.read(bytesio, dtype='float32')
    print(nparr.shape)
    return nparr


def play_np(nparr: np.ndarray):
    print("Playing back wav file with sounddevice")
    sounddevice.play(nparr)
    sounddevice.wait()


if __name__ == "__main__":
    #play_np(webrtc_request(score_str3))
    score_txt = open("astral_ocean_gliss.sco")
    play_np(webrtc_request(score_txt.read()))