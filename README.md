# 机房温湿度监控项目

## 结构

Sensor --> (Python socker server -> Sqlite DB -> web.py) --> Browser/Weixin

- Sensor (roomonitor.get_tem+roomonitor.update_controller): 基于树莓派的传感器，通过蜂窝网络连接服务器。
- Python socket server (roomonitor.update_server+roomonitor.settings): 接收传感器TCP长连接及其上传输的数据。
- Sqlite DB (roomonitor.db): 存储温度数据，包括当前状态和历史数据。
- web.py (roomonitor.app+roomonitor.utils): 提供温湿度数据查询接口。
- Browser (static/): 在浏览器端通过HighCharts和ECharts展示温湿度数据信息。
- Wenxin (roomonitor.utils): 当温湿度异常时发送微信报警信息。
