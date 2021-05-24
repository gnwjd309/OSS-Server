import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import TTS
import scipy.io.wavfile as swavfile
cred = credentials.Certificate('oss-project-f6fb6-firebase-adminsdk-9vwfe-27b8f530ff.json')
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://oss-project-f6fb6-default-rtdb.firebaseio.com/'
})
SAMPLING_RATE = 22050
def aritcle_dbsaver(title, content, category, summary, keyword, sentiment):
    num = 0;
    ref = db.reference('news/%s'%(category))
    snapshot = ref.get()
    if snapshot:
        for key in snapshot:
            num=num+1
        print(num)
    else:
        print(num)
    audio=TTS.tts(title+content)
    swavfile.write("news/%s/%s.wav"%(category,num), rate=SAMPLING_RATE, data=audio.numpy())
    audio=TTS.tts("".join(summary))
    swavfile.write("summary/%s/%s.wav" % (category, num), rate=SAMPLING_RATE, data=audio.numpy())
    dir = db.reference('news/%s/%s'% (category,num))
    dir.update({'title':'%s'%(title)})
    dir.update({'content':'%s'%(content)})
    dir.update({'summary': '%s' % (','.join(summary))})
    dir.update({'keyword': '%s' % (','.join(keyword))})
    dir.update({'sentiment': '%s' % (','.join(sentiment))})
    del audio,dir,snapshot
