import requests
import json
import cv2
import base64
from bbox_merge import parse_ocr_result
from error_location import get_error_index_list
from robust import error_correct


def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tostring()).decode('utf8')

# 发送HTTP请求
data = {'images':[cv2_to_base64(cv2.imread("WechatIMG796.jpeg"))]}
headers = {"Content-type": "application/json"}
url = "http://183.173.191.246:8868/predict/ocr_system"
r = requests.post(url=url, headers=headers, data=json.dumps(data))

# 打印预测结果
ocr_results = r.json()
ocr_results = r.json()["results"]
print(r.json()["results"])
labels = parse_ocr_result(ocr_results)

# used for debug
# labels = ['K837.127.5\nS703A2', 'K837.127.5\nS703A6', 'K837.127.5\nS703A7', 'K837.127.5\nS703A7B2', 'K837.127.5\nS703A7B3', 'K837.127.5\nS703A7B4', 'K837.127.5\nS703A8', 'K837.127.5\nW497', 'K837.127.5\nK122A2', 'K837.127.5\nX122A3', 'K837.127.5\nX122A5C3']

print("labels:", labels)
error_indexs = get_error_index_list(labels)
print("err_index: ", error_indexs)
robust_error_indexs = error_correct(labels, error_indexs, 4)
print("after robust: ", robust_error_indexs)
