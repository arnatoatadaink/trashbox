from PIL import Image
import numpy as np
import re
import requests

# 訓練形式のデータ、htmlや画面への出力は追加調整が必要
# 上から順に実装
def readfile_2dimage(path,file,**options):
    pathkey = "{}\\{}".format(path,file)
    files   = glob.glob(pathkey)
    pics    = []
    for i, file in enumerate(files):

        pic = Image.open(file)
        pic = pic.convert("RGB")
        pic = np.asarray(pic)
#         if _grayScale:
#             pic = np.average(pic,axis=(2))
#             pic = pic.reshape(pic.shape+(1,))
#         pic = inverseFunc(pic) # for mnist
        pic = pic.astype("float32")
        pic = pic.reshape((1,)+pic.shape)
        pics.append(pic)
    if len(pics) > 0:
        return pics
    elif len(pics) > 1:
        return np.concatenate(pics,axis=0)
    else:
        return None

def readurl_2dimage(path,file,**options):
    request_url  = "{}/{}".format(path,file)
    check_domains = []
    domain = options.get("domain",False)
    if domain is not None:
        check_domains.append("http://"+domain)
        check_domains.append("https://"+domain)
    else:
        domain = "farm[0-9]{1,2}.staticflickr.com/"
        check_domains.append("http://"+domain)
        check_domains.append("https://"+domain)
        domain = "images.cocodataset.org/"
        check_domains.append("http://"+domain)
        check_domains.append("https://"+domain)
        
    call_request = len(check_domains) == 0
    for check_domain in check_domains:
        if re.search(check_domain,request_url) is not None:
            call_request = True
            break

    if not call_request:
        return None

    get_item  = requests.get(request_url)
    if str(get_item)[-5] != "2":
        return None
    get_image = Image.open(io.BytesIO(get_item.content))
    get_item.close()
    get_image = get_image.convert("RGB")
    get_image = np.asarray(get_image)
    get_image = get_image.astype("float32")
    get_image = get_image.reshape((1,)+get_image.shape)
    return get_image


def readfile_text(path,file,**options):
    pass
def readurl_text(path,file,**options):
    pass

def readfile_csv(path,file,**options):
    pass
def readurl_csv(path,file,**options):
    pass
def readfile_binary(path,file,**options):
    pass
def readurl_binary(path,file,**options):
    pass

def readfile_3dimage(path,file,**options):
    pass
def readurl_3dimage(path,file,**options):
    pass
def readfile_music(path,file,**options):
    pass
def readurl_music(path,file,**options):
    pass
def readfile_movie(path,file,**options):
    pass
def readurl_movie(path,file,**options):
    pass

readfuncs = {
    "readfile_2dimage" :readfile_2dimage,
    "readurl_2dimage"  :readurl_2dimage,

    "readfile_text"    :readfile_text,
    "readurl_text"     :readurl_text,

    "readfile_csv"     :readfile_csv,
    "readurl_csv"      :readurl_csv,
    "readfile_binary"  :readfile_binary,
    "readurl_binary"   :readurl_binary,

    "readfile_3dimage" :readfile_3dimage,
    "readurl_3dimage"  :readurl_3dimage,
    "readfile_music"   :readfile_music,
    "readurl_music"    :readurl_music,
    "readfile_movie"   :readfile_movie,
    "readurl_movie"    :readurl_movie,
}

