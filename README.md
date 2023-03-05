# SynologyChatGPT

为群晖Chat设计的ChatGPT机器人，使用`Django`编写。

ChatGPT client for Synology Chat, written with Django

<img width="1220" alt="截屏2023-03-05 16 48 49" src="https://user-images.githubusercontent.com/51039745/222951973-29b72e61-19e6-47cf-9f24-5bd82c1bf20d.png">

## 安装依赖

### 安装 Python

去群晖套件中心安装 Python3 即可。

### 安装 pip

群晖安装的 `python3` 没有自带 `pip`，请参照[这篇文章](https://homepea.top/2020/35.DSM-Synology-pip/)安装。下面假设你为 `root` 用户安装了`pip`，因为普通用户会遇到权限问题。

### 安装依赖

在项目目录下，执行

```
sudo pip install -r requirements.txt
```

## 运行服务器

在项目目录下，执行

```
sudo python manage.py runserver <port>
```

在`<port>`中填入你指定的端口。注意，`port`是一个数字，不包含尖括号，如`1999`。如果服务器启动正常（没有端口冲突），按`Ctrl C`中断服务器。然后执行。

```
sudo nohup python manage.py runserver <port>
```

现在服务器就在后台执行，可以关闭SSH窗口了。（注意不要按`Ctrl C`中断`nohup`执行）

## 创建斜杠命令和机器人。

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
| 命令  | setsavedir |
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

然后，你就可以愉快地开始使用啦！
