#运行此文件可以自动下载仓库中的最新代码并更新本地文件（注意本地文件必须已存在）
#若连接不上请使用北大vpn以实现对仓库的访问
#有些文件会被反复更新，具体原因未知（可能由换行问题引起）
import requests, re, json, hashlib, base64

def CalcSha1(filepath):
    if filepath == '../user/updatetool.py':
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        sha1obj = hashlib.sha1()
        try:
            data = f.read().encode()
        except:
            return None
        sha1obj.update(b"blob " + str(len(data)).encode() + b'\0' + data)
        hash1 = sha1obj.hexdigest()
        return hash1

def grab_code(filename1):
    filename = filename1["path"]
    url = filename1["url"]
    print('下载 %s %s ...' % (filename, url), end='', flush=True)
    web_raw = json.loads(requests.get(url).text)["content"]
    with open("../" + filename, 'w', encoding='utf-8') as file:
        file.write(str(base64.b64decode(web_raw), "utf-8").replace('\r', ''))
    print('完成')

print('连接github仓库...', end='', flush=True)
main = requests.get('https://api.github.com/repos/pkulab409/sessdsa.2048/git/trees/master?recursive=1')
items = json.loads(main.text)["tree"]
codes, path = [], []
for i in range(len(items)):
    try:
        open("../" + items[i]["path"], 'r')
    except:
        continue
    sha1 = CalcSha1("../" + items[i]["path"])
    if sha1 == None:
        continue
    if sha1 != items[i]["sha"]:
        codes.append(items[i])
        path.append(items[i]["path"])
print('完成')
print('%d个代码文件将被更新：%s' % (len(codes), ', '.join(path)))
for code in codes:
    grab_code(code)
