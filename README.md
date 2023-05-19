# monitor_ssl_certificate_expire

监控域名的SSL证书是否即将过期,如果在指定时间(默认30天内,包括30天)SSL证书即将过期,那么就发送告警通知(支持邮件、钉钉等多种通知方式,支持同时开启多种告警通知或者选择任意一种通知方式接收告警)。

## 项目说明

- **将你需要监控的证书域名按照**`config/all.yaml`**文件中的格式进行填写**;
- 每个环境变量都有对应的默认配置文件的值,配置文件在`utils/settings.py`文件中(需要改成你自己的默认配置);
- 配置文件默认会读取环境变量设置的值。如果不设置环境变量,则环境变量的值就用该文件中设置的默认值;
- `APP_ENV`环境变量分为`prod`(生产环境)和`dev`(开发环境),如果不设置该环境变量,则默认为`dev`环境。`dev`环境下更改代码后会自动触发重载配置。

为了便于调试,我将项目根目录加入到 sys.path 中,如果不需要调试,则可以直接在`main.py`文件中加入这段代码即可. 代码如下:

```shell
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
```

## 环境变量说明

- **APP_PORT**: 应用侦听的端口,建议设置为 8080
- **APP_HOST**: 应用侦听的主机地址,建议设置为 0.0.0.0
- **APP_ENV**: 应用启动的模式,dev(开发环境)或者prod(生产环境)
- **APP_MAIL_PORT**: 邮件服务器端口
- **APP_MAIL_USER**: 发件人邮箱的用户名
- **APP_MAIL_PASS**: 发件人邮箱的密码
- **APP_MAIL_HOST**: SMTP邮件服务器
- **APP_MAIL_SENDER**: 发件人邮箱
- **APP_OPEN_EMAIL**: 只有两个可选值。1: 表示发送告警到邮件,0: 表示不发送告警到邮件
- **APP_OPEN_DINGTALK**: 只有两个可选值。1: 表示发送告警到钉钉,0: 表示不发送告警到钉钉
- **APP_DINGTALK_TOKEN**: 钉钉机器人的 webhook 地址中,access_token= 后面的这部分信息
- **APP_DINGTALK_SECRET**: 钉钉机器人的安全设置中的加签秘钥
- **APP_DINGTALK_PHONE_MEMBER**: 钉钉群组接受被艾特的成员手机号,可以写多个,以逗号分隔. 格式: "135xxxx0000" 或者 "135xxxx0000,151xxxx1111,177xxxx2222"
- **SSL_EXPIRE_DAYS**: 表示你想要设置的证书过期前几天发送告警信息,默认30天

以上环境变量在 **`utils/settings.py`** 中均设置了默认参数,该配置中也是以这些环境变量的值为优先,获取不到环境变量才会使用该文件中设置的默认值

## 构建镜像

```shell
sh build_docker.sh
```

## docker-compose 部署服务

```shell
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down -v
```

## GitLab CI/CD 部署服务

- 每个公司都不太一样,我这边使用`helm`渲染`chart`包的方式部署.我会预定义我需要的配置在项目根目录下的`helm-values.yaml`文件中,渲染`chart`包之前会将`helm-values.yaml`文件中的信息合并到`chart`包中的`values.yaml`文件在进行发布.整个过程只需要你更改项目代码后,`push`或者`merge`即可实现`GitLab CI/CD`，发布到`Kubernetes`集群之上。
- **注意**: 如果你的`CI/CD`方式和我的不一样,请不要用这种方式来进行部署服务.或者换成你自己的发布方式进行服务发布.

## APScheduler文档

```shell
https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html
```
