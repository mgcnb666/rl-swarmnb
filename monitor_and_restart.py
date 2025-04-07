#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import logging
import signal
import sys
from datetime import datetime

# 设置工作目录
WORK_DIR = "/home/jovyan/rl-swarmnb/"
os.chdir(WORK_DIR)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(WORK_DIR, "monitor.log")),
        logging.StreamHandler()
    ]
)

# 配置参数
SCRIPT_PATH = os.path.join(WORK_DIR, "run_rl_swarm.sh")
CHECK_INTERVAL = 60  # 检查间隔（秒）
MAX_RESTARTS = 20    # 最大重启次数
PROCESS_NAME = "hivemind_exp.gsm8k.train_single_gpu"  # 要监控的进程名

def is_process_running(process_name):
    """检查指定名称的进程是否在运行"""
    try:
        # 使用pgrep命令检查进程
        result = subprocess.run(
            ["pgrep", "-f", process_name], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        logging.error(f"检查进程时出错: {e}")
        return False

def restart_script():
    """重启训练脚本"""
    try:
        logging.info(f"正在重启训练脚本: {SCRIPT_PATH}")
        
        # 设置HF_TOKEN环境变量和自动回答
        hf_token = "hf的token"
        restart_cmd = f"""
        cd {WORK_DIR} && 
        export HF_TOKEN="{hf_token}" && 
        (echo "y"; echo "{hf_token}"; cat) | 
        nohup sh {SCRIPT_PATH} > {WORK_DIR}/restart_$(date '+%Y%m%d_%H%M%S').log 2>&1 &
        """
        
        # 执行命令
        subprocess.Popen(
            restart_cmd,
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        logging.info("重启命令已执行，已自动提供Hugging Face选择和访问令牌")
        return True
    except Exception as e:
        logging.error(f"重启脚本时出错: {e}")
        return False

def handle_signal(signum, frame):
    """处理信号（如CTRL+C）"""
    logging.info("收到终止信号，监控程序退出")
    sys.exit(0)

def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    restart_count = 0
    logging.info(f"监控程序启动，将检查进程 '{PROCESS_NAME}'")
    logging.info(f"工作目录: {WORK_DIR}")
    logging.info(f"脚本路径: {SCRIPT_PATH}")
    logging.info(f"检查间隔: {CHECK_INTERVAL}秒")
    
    try:
        while restart_count < MAX_RESTARTS:
            if not is_process_running(PROCESS_NAME):
                logging.warning(f"进程 '{PROCESS_NAME}' 未运行！")
                
                # 执行重启
                success = restart_script()
                if success:
                    restart_count += 1
                    logging.info(f"已重启 {restart_count}/{MAX_RESTARTS} 次")
                    
                    # 等待一段时间，让程序有机会启动
                    time.sleep(30)
                else:
                    logging.error("重启失败")
            else:
                logging.info(f"进程 '{PROCESS_NAME}' 正在运行")
            
            # 等待下一次检查
            time.sleep(CHECK_INTERVAL)
    
    except Exception as e:
        logging.error(f"监控程序遇到错误: {e}")
    
    logging.info("监控程序结束")

if __name__ == "__main__":
    main() 