from mcp.server.fastmcp import FastMCP
import os
import sys
import logging
import time

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DoorLockMCP")


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# 引入模块
from DoorLockController import mqtt_client
from JC_packet.JC_packet_action import set_payload_action
from JC_packet.JC_packet import set_packet


app = FastMCP("DoorLockController")


@app.tool()
def unlock_door(lock_id: str) -> str:
    """
    通过 MQTT 发布开门指令
    参数:
        lock_id: 门锁网关编号
    """
    # try:
    #     #生成payload数据
    #     aes_key = None
    #     time_Stamp = (int)(time.time())
    #     payload = []
    #     payload = set_payload_action(        
    #         aes_key,        # 加密密钥
    #         1,              # uint32_t 自增计数值
    #         time_Stamp,     # uint32_t 服务器时间戳
    #         666     ,       # uint32_t 用户账户信息
    #         1     ,         # uint8_t  钥匙等级
    #         1,              # uint8_t  执行通道
    #         1,              # uint8_t  执行动作
    #     )


    #     #封装完整通信帧
    #     frame = set_packet(0x0108, payload)

    #     #转换为十六进制字符串
    #     data_str = ''.join(format(x, '02X') for x in frame)
    data_str = "9C010108000000C20020F3716310B7D6F7A7F6E9FF0BDA723E06EFA9804149414AAC0FFFCD78C332B6F8710D"
        #发布MQTT消息
    mqtt_client.publish_command(lock_id, data_str)

    logger.info(f"开门指令已发送到网关 {lock_id}，数据帧: {data_str}")
    return f"已发送开门指令到网关 {lock_id}\n帧内容: {data_str}"

    # except Exception as e:
    # logger.error(f"发送开门指令失败: {e}", exc_info=True)
    # return f"发送失败: {str(e)}"


def run():
    """启动 MQTT 客户端与 MCP 工具"""
    mqtt_client.start()
    app.run(transport="stdio")




