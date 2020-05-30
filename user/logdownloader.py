def get_log_from_net():
    import requests
    import json

    token = "6nrjaSIVIT89niKBsRP396gO66GHRDw1sJoXc8qz087GfHZ2pHZcjqc27O0ldOB7"
    sessionid = "vniwps9utog5sy3uywj4bvza7sokvd5i"

    headers = {
        "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-Hans-CN, zh-Hans; q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "Keep-Alive",
        "Content-Length": "414",
        "Content-Type": "multipart/form-data; boundary=---------------------------7e4dc1cc0980",
        "Cookie": f"csrftoken={token}; sessionid={sessionid}",
        "Host": "gis4g.pku.edu.cn",
        "Referer": "http://gis4g.pku.edu.cn/ai_arena/login/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    }
    
    print('请输入查看比赛页面的地址:')
    while True:
        try:
            url = input()
            if url == '':
                print("地址无效")
                return
            if not url.startswith("http"):
                url = "http://" + url
            if not url.startswith("http://162.105.17.143:9580/match/"):
                print("地址无效")
                return
            if not url.endswith("match/"):
                if url[-3] == "/":
                    url = url[:-2]
                elif url[-4] == "/":
                    url = url[:-3]
            r = requests.get(url, headers=headers)
        except:
            continue
        break
    items = json.loads(r.text.split('使用比赛参数')[1].split("<div>")[1].split("</div>")[0].replace("&quot;", "\""))
    import os
    print('存储在哪个文件夹?:')
    while True:
        try:
            dirname = input()
            if not os.path.exists(dirname):
                os.mkdir(dirname)
        except:
            continue
        break
    for i in range(int(items["rounds"])):
        r = requests.get(url + str(i) + "/", headers=headers)
        print(i)
        items = json.loads(r.text.replace("\'", "\"").split('<div id="record_receiver" style="display:none">')[1].split("</div>")[0].replace("&quot;", "\""))
        f = open(dirname + "/" + str(i) + ".txt", "w")
        f.write(repr(items["time"]))
        for i in items["logs"]:
            f.write("&d" + str(i['D']['r']) + ":player " + str(i['D']['p']) + " set " + i['D']['d'][0] + " " + str(i['D']['d'][1]) + "\n")
            f.write("&p" + str(i['D']['r']) + ":\n" + '\n'.join([' '.join([('+' if i['P'][row][column] > 0 or (i['P'][row][column] == 0 and column < 8 / 2) else '-')\
                                 + str(abs(i['P'][row][column])).zfill(2) \
                                 for column in range(8)]) for row in range(4)]))
        for i in items["logs"][-1]["E"]:
            f.write("&e:" + i)
        f.write("&e:cause" + items["cause"])
        f.write("&e:winner" + str(items["winner"]))
        try:
            f.write("&e:error" + items["error"])
        except:
            pass
        f.close()
    print('已完成')

if __name__ == '__main__':
    get_log_from_net()
