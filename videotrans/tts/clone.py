import os
import re
import shutil
import requests
from videotrans.configure import config
from videotrans.util import tools


def get_voice(*,text=None, role=None,rate=None, language=None, filename=None,set_p=True):

    try:
        api_url=config.params['clone_api'].strip().rstrip('/')
        if not api_url:
            raise Exception("get_voice:"+config.transobj['bixutianxiecloneapi'])
        api_url='http://'+api_url.replace('http://','')
        config.logger.info(f'clone-voice:api={api_url}')
        data={"text":text.strip(),"language":language}

        # role=clone是直接复制
        if role!='clone':
            #不是克隆，使用已有声音
            data['voice']=role
            files=None
        else:
            #克隆声音
            files={"audio":open(filename,'rb')}
        res=requests.post(f"{api_url}/apitts",data=data,files=files,proxies={"http":"","https":""})
        config.logger.info(f'clone-voice:{data=}')
        config.logger.info(f'clone-voice:{res.text=}')

        res=res.json()
        if "code" not in res or res['code']!=0:
            raise Exception(f'{res}')
        if api_url.find('127.0.0.1')>-1 or api_url.find('localhost'):
            tools.wav2mp3(re.sub(r'\\{1,}','/',res['filename']),filename)
        else:
            resb=requests.get(res['url'])
            if resb.status_code!=200:
                raise Exception(f'clonevoice:{res["url"]=}')
            config.logger.info(f'clone-voice:resb={resb.status_code=}')
            with open(filename+".wav",'wb') as f:
                f.write(resb.content)
                tools.wav2mp3(filename+".wav",filename)
                if os.path.exists(filename+".wav"):
                    os.unlink(filename+".wav")
        return True
    except Exception as e:
        error=str(e)
        if set_p:
            tools.set_process(error)
        config.logger.error(f"cloneVoice合成失败:{error},{api_url=}")
        raise Exception(f"cloneVoice:{error}")
