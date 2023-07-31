# SynologyChatGPT

为群晖Chat设计的ChatGPT机器人，使用`Django`编写。

ChatGPT client for Synology Chat, written with Django

<img width="1220" alt="截屏2023-03-05 16 48 49" src="https://user-images.githubusercontent.com/51039745/222951973-29b72e61-19e6-47cf-9f24-5bd82c1bf20d.png">  

使用本应用共分四步：  
1. 启动服务  
2. 设置斜杠命令  
3. 通过斜杠命令设置用户、密钥   
4. 通过SynologyChat聊天机器人窗口与ChatGpt对话。  
   
## 一、 启动   
支持docker启动或本机运行。  
以下三种择一即可，建议DSM7.2使用第二种docker-compose启动的方式，DSM7.1及以下使用docker图形界面或命令行。  
### 1. 通过命令行docker使用  

```bash
docker run --rm \
    -p 8000:8000 \
    --name synology-chat-gpt \
    -v $(pwd)/data:/app/data \
    -e OPENAI_API_BASE=https://api.openai.com/v1 \ # Set custom OpenAI API base here
    docker-registry.mujiannan.com:5001/mujiannan/synology-chat-gpt:latest
```
-p参数为端口映射，-v为数据目录映射（用于持久化保存聊天记录、api_key等）。  
如果你想要从源码自行制作镜像，请参考项目目录项目目录下的`.debug-docker.sh`。  
### 2. 通过Docker-Compose使用  
DSM7.2以上可以在`container manager`内新建项目，然后通过WebStation建立自定义域名，该方式有不占用母机端口、方便管理、安全等好处。  
```yaml
version: "3.7"
services:
  synology-chat-gpt:
    image: docker-registry.mujiannan.com:5001/mujiannan/synology-chat-gpt:latest
    volumes:
      - /volume1/docker/synology-chat-gpt/data:/app/data
    deploy:
      resources:
        limits:
          cpus: 500m
          memory: 200m
    ports: 
      - "8000:8000"
```  
### 3. 本机运行
建议非开发者不要使用此方式启动。  
### 3.1 安装 Python

去群晖套件中心安装 Python3 即可。
### 3.2 安装 pip
群晖安装的 `python3` 没有自带 `pip`，请参照[这篇文章](https://homepea.top/2020/35.DSM-Synology-pip/)安装。下面假设你为 `root` 用户安装了`pip`，因为普通用户会遇到权限问题。  
如果你执行提示语法错误/其他错误，首先试试把命令中的`python`和`pip`换成`python3` 和 `pip3`。你的`python`可能是python2。  
### 3.3 通过pip安装依赖包  
在项目目录下，执行
```
sudo pip install -r requirements.txt
```
### 3.4 运行服务器
如果本项目不部署在群晖上，会遇到`HTTP 400`错误。解决方案请参考这个Issue：[#4](https://github.com/GaiZhenbiao/SynologyChatGPT/issues/4)

在项目目录下，依次执行以下两条命令，创建数据库：

```
sudo python manage.py makemigrations chat
sudo python manage.py migrate
```

然后执行下面的命令启动服务器：

```
sudo python manage.py runserver <port>
```

在`<port>`中填入你指定的端口。注意，`<port>`是一个数字，不包含尖括号，如`1999`。如果服务器启动正常（没有端口冲突），按`Ctrl C`中断服务器。然后执行。

```
sudo nohup python manage.py runserver <port>
```

现在服务器就在后台执行，可以关闭SSH窗口了。（注意不要按`Ctrl C`中断`nohup`执行）

## 二、 创建斜杠命令和机器人。

在Chat界面右上角，创建整合。

<img width="280" alt="截屏2023-03-05 17 22 45" src="https://user-images.githubusercontent.com/51039745/222952288-2ac585a8-e652-4fe2-ba5e-de6158f1c402.png">

### 斜杠命令

先创建一些斜杠命令。斜杠命令可以在Chat对话框里输入`/`执行。

<img width="624" alt="image" src="https://user-images.githubusercontent.com/51039745/222952325-d8a75623-4cc8-40d0-90e8-529eb4bfba82.png">

点击创建按钮创建。

<img width="682" alt="image" src="https://user-images.githubusercontent.com/51039745/222952364-a39c16bb-608c-4317-afff-29c4d872c3ef.png">

像这样填写表单内容。`请求URL`均为`http://127.0.0.1:<port>/webhook`。其中`<port>`是你刚刚指定的端口，图中的示例使用了`1999`端口。你可以在`自定义名称`中填入任何合法名称，但`命令`必须按下面的指示填写。本项目不使用`令牌`参数，可以忽略它。

<img width="645" alt="image" src="https://user-images.githubusercontent.com/51039745/222952493-016eb4f4-8b36-4192-98d9-30137d7a67cc.png">

接下来列出本项目支持的命令及其参数。

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | clear |
| 命令说明  | 清除对话历史记录 |
| 描述  | 清除ChatGPT的上下文，但Chat中的聊天记录仍然会被保留。 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | totaltoken |
| 命令说明  | 查看当前token用量 |
| 描述  | token上限为4096 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | retry |
| 命令说明  | 重新回答上一个问题 |
| 描述  | 让ChatGPT重新回答一次你的上一个提问 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | whoami |
| 命令说明  | 返回当前用户ID |
| 描述  | 用户ID是每位用户的唯一身份证明 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | newuser |
| 命令说明  | 创建新ChatGPT用户 |
| 描述  | 接受可选两个参数：BaseURL，群晖的URL；BotKey，为机器人界面展示的令牌。 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | setapikey |
| 命令说明  | 设置当前用户的OpenAI API密钥 |
| 描述  | 接受一个参数：OpenAI API密钥。 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | setbotkey |
| 命令说明  | 设置当前用户的Bot令牌 |
| 描述  | 接受一个参数：Bot令牌 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | setbaseurl |
| 命令说明  | 设置群晖Chat的URL |
| 描述  | 接受一个参数：URL，如https://www.example.com:5001 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | setsavedir |
| 命令说明  | 设置自动保存的目录 |
| 描述  | 接受一个参数：/path/to/a/dir，是一个目录的路径 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | getsavedir |
| 命令说明  | 获取自动保存的目录路径 |
| 描述  | 返回当前自动保存的目录 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | saveas |
| 命令说明  | 保存目前与ChatGPT的聊天到txt文件 |
| 描述  | 接受一个参数：filename，保存到默认保存路径中 |

|  字段名   | 内容  |
|  ----  | ----  |
| 命令  | savenow |
| 命令说明  | 自动保存目前与ChatGPT的聊天到txt文件 |
| 描述  | 使用当前系统时间作为文件名 |

### 然后创建机器人。

<img width="625" alt="image" src="https://user-images.githubusercontent.com/51039745/222953273-ddeb6843-3417-40bd-a62c-1b1df6365f5a.png">

在`自定义名称`中填入机器人名称，可以任意指定，比如`ChatGPT`。

`传出URL`设定为`http://127.0.0.1:<port>`。其中`<port>`为你指定的端口号。上面的截图使用了`1999`端口号。

### 开始使用

本项目支持多用户。因此，第一次使用时，需要创建ChatGPT机器人用户。使用`/newuser`命令创建。可以在此时指定`BaseURL`与`BotKey`，也可以稍后指定。`BaseURL`是群晖面板的URL，如`https://www.example.com:5001`，注意最后没有斜线`/`。`BotKey`是机器人的令牌。

```
/newuser <(可选)BaseURL> <(可选)BotKey>
```

如果稍后指定，用`/setbotkey`命令指定`Bot Key`

```
/setbotkey <BotKey>
```

用`setbaseurl`命令指定`BaseURL`

```
/setbaseurl <BaseURL>
```

注意，在设定BaseURL和BotKey之前，机器人无法给你发送信息，Chat可能会提示机器人不可用。

然后，需要设定你的OpenAI API密钥。

```
/setapikey <OpenAI API Key>
```

如果你想使用将当前聊天记录保存成文件的功能，还需要配置默认文件保存文件夹的路径，路径中不允许含有空格：

```
/setsavedir /path/to/your/dir
```

然后，你就可以愉快地开始使用啦！

## 已知问题

在使用`saveas`和`savenow`命令时，Chat会提示机器人不可用，然后收到保存成功的提示。文件可以正常保存。

## 问题排查  
1. 容器问题排查  
   建议使用图形化`container manager`查看容器日志，或者使用命令行
    ```bash  
    docker logs -n 50 -f your-container-name
    ```  
    如有必要，可携带日志至github issue提问。
## 赞助

感谢 [rashida](https://github.com/RashidaKAKU) 的慷慨赞助
