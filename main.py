import requests
import re
import os
import json
from tqdm import trange


def download(url : str, headers : dict) -> bytes:
    response = requests.head(url=url, headers=headers, allow_redirects=True)
    if response.status_code == 403: # 就挺神奇的，403正常
        return requests.get(url=response.url).content # 加了headers反而不行。。。
    else:
        return None
    

def download_post(url : str, save_path : str, **kwards) -> None:
    response = requests.get(url=url, headers=headers)
    post_id_pattern = r"\d+\/(\d+)" # 用于匹配帖子id的正则表达式
    post_id = re.findall(post_id_pattern, url)[0]
    html_source = response.text
    # print(len(response.text))
    # with open("response_example.txt", "w", encoding="utf-8") as f:
    #     f.write(response.text)
    # pattern = rf"<div id='post_{post_id}'.*?<div id='post"
    pattern = rf"<div id='post_{post_id}'.*?<span class='post-likes'>"
    matches = re.findall(pattern, html_source, re.DOTALL)
    # print(len(matches))
    pattern_img = r'data-download-href="(.*?\?dl=1)"' # 用于匹配图片的正则表达式
    if len(matches) != 0:
        matches_img = re.findall(pattern_img, matches[0], re.DOTALL)
        matches_img = ["https://shuiyuan.sjtu.edu.cn" + match_img for match_img in matches_img]
        # for match_img in matches_img:
        #     print(match_img)
    else:
        # print("没有找到图片。")
        # exit(1)
        return
    if len(matches_img) == 0:
        return
    # 创建文件夹
    if not os.path.exists(save_path):
        os.mkdir(save_path)
        
    # 保存图片
    fail_sum = 0
    fail = False
    show_name = "下载图片"
    if "post_sum" in kwards.keys():
        show_name = f"进度：{kwards['post_num']}/{kwards['post_sum']}"
    for i in trange(len(matches_img), desc=show_name):
        # 使用正则表达式匹配图片格式
        match_img = matches_img[i]
        pattern_img = r".*?(\.\w+)\?dl=1"
        img_format = re.findall(pattern_img, match_img)[0]
        img_name = str(i+1)+img_format
        img_path = f"{save_path}/{img_name}"
        content = download(match_img, headers=headers)
        if content is not None:
            with open(img_path, "wb") as f:
                f.write(content)
        else:
            fail_sum += 1
            fail = True
    if fail:
        print(f"共有{fail_sum}张图片保存失败。")


def download_topic(url : str, save_path : str) -> None:
    # 首先获取话题共有多少post
    topic_id_pattern = r"\d+" # 用于匹配帖子id的正则表达式
    topic_id = re.findall(topic_id_pattern, url)[0]
    response = requests.get(url=f"https://shuiyuan.sjtu.edu.cn/t/topic/{topic_id}/99999", headers=headers)
    html_source = response.text
    post_id_pattern = r"<div id='post_(\d+)'" # 用于匹配帖子id的正则表达式 <div id='post_4229'
    max_post_id = re.findall(post_id_pattern, html_source)[-1]
    download_range = input(f"话题共有 {max_post_id} 个post，下载全部直接回车，下载部分输入1：")
    if download_range == "":
        start_id, stop_id = 1, int(max_post_id)
    elif download_range == "1":
        start_id, stop_id = input("请输入下载范围（空格分隔）：").split(" ")
        start_id, stop_id = int(start_id), int(stop_id)
    else:
        print("输入错误，程序退出。")
        exit(1)
    print(f"话题共有 {max_post_id} 个post，下载post_id在 {start_id} 到 {stop_id} 之间的post。")
    # 然后下载图片
    for i in range(start_id, stop_id+1):
        download_post(f"https://shuiyuan.sjtu.edu.cn/t/topic/{topic_id}/{i}", f"{save_path}/post_{i}", post_num=i-start_id+1, post_sum=stop_id-start_id+1)


if __name__ == "__main__":
    COOKIE=""
    COOKIE=input("请输入Cookies（留空使用上次的cookies）：")
    if COOKIE == "":
        try:
            with open("headers.json", "r", encoding="utf-8") as f:
                headers = json.load(f)
        except Exception as e:
            print("没有找到headers.json，程序退出。")
            exit(1)
    else:
        headers = {
            "Host": "shuiyuan.sjtu.edu.cn",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            "DNT": '1',
            "sec-ch-ua-mobile": '?0',
            "Upgrade-Insecure-Requests": '1',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Site": 'same-origin',
            "Sec-Fetch-Mode": 'navigate',
            "Sec-Fetch-Dest": 'empty',
            "Accept-Encoding": 'gzip, deflate, br',
            "Accept-Language": 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            "Cookie": COOKIE
            }
        with open("headers.json", "w", encoding="utf-8") as f:
            json.dump(headers, f, ensure_ascii=False, indent=4) # 保存headers
    url = input("请输入链接：")
    # 判断链接是否合法
    url_pattern_1 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+\/\d+\?u=\S+"
    url_pattern_2 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+\/\d+" # 帖子
    url_pattern_3 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+\?u=\S+"
    url_pattern_4 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+" # 话题
    topic, post = None, None
    if re.match(url_pattern_1, url) or re.match(url_pattern_2, url):
        print("链接合法，判定为帖子")
        topic, post = False, True
    elif re.match(url_pattern_3, url) or re.match(url_pattern_4, url):
        print("链接合法，判定为话题")
        topic, post = True, False
    else:
        print("链接不合法，程序退出。")
        exit(1)
    # 创建运行文件夹
    i = 0
    if not os.path.exists("runs"):
        os.mkdir("runs")
    while os.path.exists(f"runs/run_{i}"):
        i += 1
    os.mkdir(f"runs/run_{i}")
    SAVE_PATH = f"runs/run_{i}" # 保存路径
    # 下载图片
    if topic:
        download_topic(url, SAVE_PATH)
    elif post:
        download_post(url, SAVE_PATH)
        