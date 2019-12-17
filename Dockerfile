FROM python:3.6

WORKDIR /usr/src/app    #工作目录

COPY requirements.txt ./  #复制requirements.txt文件
RUN pip install --no-cache-dir -r requirements.txt   #安装依赖包

COPY . .    #复制项目代码

CMD [ "python", "./confirm_login.py" ]   #运行hello.py文件