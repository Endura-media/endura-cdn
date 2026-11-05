import sherpa_onnx, re, subprocess, json, wave, numpy as np
d='sherpa-onnx-whisper-base.en/'
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+'base.en-encoder.int8.onnx',decoder=d+'base.en-decoder.int8.onnx',tokens=d+'base.en-tokens.txt')
w=wave.open("vo16.wav"); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
out=subprocess.run(['ffmpeg','-hide_banner','-i','vo.mp3','-af','silencedetect=noise=-35dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)]
en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
dur=len(a)/sr
bounds=[0.0]+[(s+e)/2 for s,e in zip(st,en)]+[dur]
segs=[]
for i in range(len(bounds)-1):
  s,e=bounds[i],bounds[i+1]
  stream=rec.create_stream(); stream.accept_waveform(sr,a[int(s*sr):int(e*sr)]); rec.decode_stream(stream)
  segs.append((round(s,2),round(e,2),stream.result.text.strip()))
  print(segs[-1])
json.dump(segs,open('segs.json','w'))
