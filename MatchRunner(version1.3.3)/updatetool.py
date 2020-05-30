#运行此文件可以自动下载仓库中的最新代码并更新本地文件，也可以下载其它文件，文件不存在时将被自动创建
#文件未存放在项目中时可以下载整个项目到本地
#若连接不上请使用北大vpn以实现对仓库的访问
import requests, re, json, hashlib, base64, os

def CalcSha1(filepath):
    if os.path.splitext(os.path.basename(filepath))[1] == '':
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        return None
    if filepath.endswith(".png") or filepath.endswith(".pdf") or filepath.endswith(".vsix"):#此处的拓展名可以增添或删除
        try:
            sha1obj = hashlib.sha1()
            data = open(filepath, "rb").read()
            sha1obj.update(b"blob " + str(len(data)).encode() + b'\0' + data)
            hash1 = sha1obj.hexdigest()
            return hash1
        except:
            return 1
    else:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sha1obj = hashlib.sha1()
                data = f.read().encode()
                sha1obj.update(b"blob " + str(len(data)).encode() + b'\0' + data)
                hash1 = sha1obj.hexdigest()
                return hash1
        except:
            return 1

def grab_code(filename1):
    filename = filename1["path"]
    url = filename1["url"]
    print('下载 %s %s ...' % (filename, url), end='', flush=True)
    web_raw = json.loads(requests.get(url).text)["content"]
    with open(prefix + filename, 'w', encoding='utf-8') as file:
        file.write(str(base64.b64decode(web_raw), "utf-8").replace('\r', ''))
    print('完成')

def grab_file(filename1):
    filename = filename1["path"]
    url = filename1["url"]
    print('下载 %s %s ...' % (filename, url), end='', flush=True)
    web_raw = json.loads(requests.get(url).text)["content"]
    with open(prefix + filename, 'wb') as file:
        file.write(base64.b64decode(web_raw))
    print('完成')

print('连接github仓库...', end='', flush=True)
main = requests.get('https://api.github.com/repos/pkulab409/sessdsa.2048/git/trees/master?recursive=1')#项目地址，可以修改
try:  #判断文件是否存放在项目中
    if os.path.abspath("../").endswith("sessdsa.2048"):
        prefix = "../"
    else:
        prefix = "./sessdsa.2048/"
        try:
            os.mkdir("./sessdsa.2048")
        except:
            pass
except:
    prefix = "./sessdsa.2048/"
    try:
        os.mkdir("./sessdsa.2048")
    except:
        pass
items = json.loads(main.text)["tree"]
codes, path = [], []
for i in range(len(items)):
    sha1 = CalcSha1(prefix + items[i]["path"])
    if sha1 == None:
        continue
    if sha1 != items[i]["sha"]:
        codes.append(items[i])
        path.append(items[i]["path"])
        continue
print('完成')
print('%d个代码文件将被更新：%s' % (len(codes), ', '.join(path)))
for code in codes:
    if code["path"].endswith(".png") or code["path"].endswith(".pdf") or code["path"].endswith(".vsix"):
        grab_file(code)
    else:
        grab_code(code)
