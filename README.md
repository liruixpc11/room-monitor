# 机房温湿度监控项目

## 结构

Sensor --> (Python socker server -> Sqlite DB -> web.py) --> Browser/Weixin

| 组件 | 作用 |
| :--: | -- |
| Sensor | 基于树莓派的传感器，通过蜂窝网络连接服务器 |
| Python socket server | 接收传感器TCP长连接及其上传输的数据 |
| Sqlite DB | 存储温度数据，包括当前状态和历史数据 |
| web.py | 提供温湿度数据查询接口 |
| Browser | 在浏览器端通过HighCharts和ECharts展示温湿度数据信息 |
| Wenxin | 当温湿度异常时发送微信报警信息 |

