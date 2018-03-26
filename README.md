# shjzh_query
登陆到上海市居住证转常住户口系统并查询申办结果

## Requirements
* python3
* beautifulsoup4
* cv2
* numpy
* pytesseract
* requests

On Ubunut, install requirements with below commands:
```
apt install tesseract-ocr
pip3 install opencv-python beautifulsoup4 numpy pytesseract requests
```
Or preferably install in a virtual env, e.g. virtualenv or anaconda

## Usage
```
shjzh_username=$your_id_number shjzh_password=$your_password ./query.py -q
```
