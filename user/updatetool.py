#运行此文件可以自动下载仓库中的最新代码并更新本地文件（注意本地文件必须已存在）
#可能需要使用北大vpn以实现对仓库的访问
import requests, re, urllib.parse


def grab_code(filename):
    url = 'https://raw.githubusercontent.com/pkulab409/sessdsa.2048/master/%s' % filename
    print('下载 %s ...' % url, end='', flush=True)
    web_raw = requests.get(url)
    filename = urllib.parse.unquote(filename)
    with open("../" + filename, 'w', encoding='utf-8') as file:
        file.write(web_raw.text.replace('\r\n', '\n'))
    print('完成')


print('连接github仓库...', end='', flush=True)
main = requests.get('https://github.com/pkulab409/sessdsa.2048')
items = re.findall(r'href="/pkulab409/sessdsa.2048/blob/master/(.+?)"',
                   main.text)
print('完成')
codes = [i for i in items if (i.endswith('.md') or i.endswith('.py')) and not 'updatetool' in i]
print('获取到%d个代码文件：%s' % (len(codes), ', '.join(codes)))
for code in codes:
    grab_code(code)
