import requests
from headers import headers

if __name__ == "__main__":
    url = "https://shuiyuan.sjtu.edu.cn/t/topic/22873/4148"
    response = requests.get(url=url, headers=headers)
    print(len(response.text))