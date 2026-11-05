import sherpa_onnx, wave, numpy as np, json
d='sherpa-onnx-zipformer-en-2023-06-26/'
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=d+'encoder-epoch-99-avg-1.int8.onnx',decoder=d+'decoder-epoch-99-avg-1.onnx',joiner=d+'joiner-epoch-99-avg-1.int8.onnx',tokens=d+'tokens.txt')
w=wave.open("vo16.wav"); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs=json.load(open('segs.json'))
out=[]
for s,e,_ in segs:
    st=rec.create_stream(); st.accept_waveform(sr,a[int(s*sr):int(e*sr)]); rec.decode_stream(st)
    r=st.result
    words=[];cur=None
    for tok,ts in zip(r.tokens,r.timestamps):
        if tok.startswith(' ') or tok.startswith('▁') or cur is None:
            cur=[tok.replace('▁','').strip(),s+ts]; words.append(cur)
        else: cur[0]+=tok
    out.append(words)
    print(round(s,2), [(w_, round(t,2)) for w_,t in words])
json.dump(out,open('words.json','w'))
