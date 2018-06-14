# shjzh_query
登陆到上海市居住证转常住户口系统并查询申办结果

## Requirements
* python3
* beautifulsoup4
* cv2
* numpy
* pytesseract
* requests
* recode (for social security card or sbk)

On Ubunut, install requirements with below commands:
```
apt install tesseract-ocr
pip3 install opencv-python beautifulsoup4 numpy pytesseract requests
```
Or preferably install in a virtual env, e.g. virtualenv or anaconda

## Usage

* To query the result:
```
shjzh_username=$your_id_number shjzh_password=$your_password python3 query.py -q
```

* To query and send mail:
```
shjzh_username=$your_id_number shjzh_password=$your_password shjzh_mailto=$your_email ./check_and_mail.sh
```

* To put into a crontab run at 12:00 daily:
```
0 12 * * * shjzh_username=$your_id_number shjzh_password=$your_password shjzh_mailto=$your_email /path/to/check_and_mail.sh
```
