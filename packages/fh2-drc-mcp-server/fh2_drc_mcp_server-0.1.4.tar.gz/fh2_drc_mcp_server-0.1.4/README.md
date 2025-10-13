# FH2 DRC MCP Server

大疆无人机远程控制 MCP 服务器

## 功能特性

### 设备管理
- `device_recommendation` - 推荐最适合的无人机和网关设备
- `cloud_controls_create` - 申请云控权限

### 飞行控制
- `drone_takeoff` - 一键起飞
- `fly_to_points` - 飞向目标点
- `drone_return_home` - 返航

### 相机控制
- `camera_photo_take` - 拍照
- `camera_aim` - 调整相机角度
- `camera_look_at` - 相机朝向指定坐标
- `gimbal_reset_horizontal` - 云台水平复位
- `gimbal_reset_downward` - 云台向下复位

### POI任务
- `poi_enter` - 开始POI环绕
- `poi_exit` - 停止POI环绕

### 状态监控
- `get_flight_status` - 查询飞行状态
- `analyze_flight_status` - 智能分析飞行状态

### 地图Pin点
- `get_pin_points` - 查询所有Pin点
- `create_pin_point` - 创建Pin点标记
- `get_default_group_id` - 获取默认分组ID

### AI告警
- `get_alert_config` - 查询告警配置
- `update_alert_config` - 更新告警配置
- `enable_llm_alert` - 快速开启LLM告警
- `disable_alert` - 关闭告警

## 安装运行

### 1. 激活虚拟环境并安装依赖

```bash
cd /Users/leslie.zhang/PycharmProjects/es-mcp-service/fh2-drc-mcp-server
source .venv/bin/activate
pip install -e .
```

### 2. 运行服务器

```bash
fh2-drc-mcp-server
```

或者直接使用 Python 运行：

```bash
python -m fh2_drc_mcp_server
```

## 在 Cursor 中配置

编辑 `~/.cursor/mcp.json` 文件，添加以下配置：

```json
{
  "mcpServers": {
    "fh2-drc-mcp-server": {
      "command": "/Users/leslie.zhang/PycharmProjects/es-mcp-service/fh2-drc-mcp-server/.venv/bin/python",
      "args": [
        "-m",
        "fh2_drc_mcp_server"
      ],
      "env": {
        "DRC_USER_TOKEN": "your-user-token-here"
      }
    }
  }
}
```

重启 Cursor 后即可使用。
