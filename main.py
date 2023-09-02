import requests
from headers import headers
import re
import os
import time


def download(url : str, headers : dict) -> bytes:
    response = requests.head(url=url, headers=headers, allow_redirects=True)
    if response.status_code == 403: # 就挺神奇的，403正常
        return requests.get(url=response.url).content # 加了headers反而不行。。。
    else:
        return None

if __name__ == "__main__":
    url = "https://shuiyuan.sjtu.edu.cn/t/topic/22873/4149?u=东川路第一滑稽"
    # 判断链接是否合法
    url_pattern_1 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+\/\d+\?u=\S+"
    url_pattern_2 = r"https:\/\/shuiyuan\.sjtu\.edu\.cn\/t\/topic\/\d+\/\d+"
    if re.match(url_pattern_1, url) is None and re.match(url_pattern_2, url) is None:
        print("链接不合法")
        exit(1)
    post_id_pattern = r"\d+\/(\d+)" # 用于匹配帖子id的正则表达式
    post_id = re.findall(post_id_pattern, url)[0]
    
    response = requests.get(url=url, headers=headers)
    html_source = response.text
    print(len(response.text))
    with open("response_example.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
    # pattern = rf"<div id='post_{post_id}'.*?<div id='post"
    pattern = rf"<div id='post_{post_id}'.*?<span class='post-likes'>"
    matches = re.findall(pattern, html_source, re.DOTALL)
    print(len(matches))
    pattern_img = r'data-download-href="(.*?\?dl=1)"' # 用于匹配图片的正则表达式
    if len(matches) != 0:
        matches_img = re.findall(pattern_img, matches[0], re.DOTALL)
        matches_img = ["https://shuiyuan.sjtu.edu.cn" + match_img for match_img in matches_img]
        for match_img in matches_img:
            print(match_img)
        
    # 保存图片
    # 创建文件夹
    if not os.path.exists("saved"):
        os.mkdir("saved")
    # 在saved文件夹以当前时间命名一个文件夹
    time_str = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    if not os.path.exists(f"saved/{time_str}"):
        os.mkdir(f"saved/{time_str}")
    # 保存图片
    for i, match_img in enumerate(matches_img):
        # 使用正则表达式匹配图片格式
        pattern_img = r".*?(\.\w+)\?dl=1"
        img_format = re.findall(pattern_img, match_img)[0]
        img_name = str(i+1)+img_format
        img_path = f"saved/{time_str}/{img_name}"
        content = download(match_img, headers=headers)
        if content is not None:
            with open(img_path, "wb") as f:
                f.write(content)
            print(f"图片{img_name}保存成功")
        else:
            print(f"图片{img_name}保存失败")
        