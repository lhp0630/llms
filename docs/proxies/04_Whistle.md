# Whistle

- [安装](#安装)
- [访问控制](#访问控制)
  - [匹配 URL 路径前缀](#匹配-url-路径前缀)
  - [通配符匹配](#通配符匹配)
- [重写 HTTP 请求](#重写-http-请求)
  - [重写请求路径](#重写请求路径)
  - [添加请求头](#添加请求头)

## 安装

```bash
npm install -g whistle
```

启动 Whistle 服务

```bash
ws start
```

> 更多命令说明可以通过 `w2 help` 查看

## 访问控制

### 匹配 URL 路径前缀

```conf
# Rules

myweb.test localhost:5000
```

### 通配符匹配

```conf
# 必须以 ^ 开头，以 $ 结束，$ 符号可以省略
# * 为通配符，可以通过 $1-9 的格式获取通配符匹配的字符

# Rules

^myweb.test/*** localhost:5000/$1
```

## 重写 HTTP 请求

### 重写请求路径

```conf
# 可使用通配符匹配规则实现代理到其他 URL 路径

# 将 api/file/{id}/picture 开始的 HTTP 请求转发到 api/file/{id}/chart
# http://myweb.test/api/file/718/picture/window/100?filename=expamle.png -> http://myweb.test/api/file/718/chart/window/100?filename=expamle.png

# Rules

myweb.test localhost:5000

^myweb.test/api/file/*/picture/*** localhost:5000/api/file/$1/chart/$2
```

### 添加请求头

```conf
# Values

# 创建名称为 websocket 的 Values
x-whistle-policy: tunnel

# Rules

myweb.test localhost:5000

myweb.test reqHeaders://{websocket}
```
