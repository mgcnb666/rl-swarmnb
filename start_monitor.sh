#!/bin/bash

# 设置工作目录
WORK_DIR="/home/jovyan/rl-swarmnb/"

# 切换到工作目录
cd "$WORK_DIR" || {
    echo "无法进入工作目录: $WORK_DIR"
    exit 1
}

# 确保监控脚本有执行权限
chmod +x "$WORK_DIR/monitor_and_restart.py"

# 确保训练脚本有执行权限
chmod +x "$WORK_DIR/run_rl_swarm.sh"

# 检查是否已有监控进程在运行
if pgrep -f "monitor_and_restart.py" > /dev/null; then
    echo "监控程序已经在运行中，无需重复启动"
    exit 0
fi

# 使用nohup在后台运行监控脚本
nohup python3 "$WORK_DIR/monitor_and_restart.py" > "$WORK_DIR/monitor_nohup.log" 2>&1 &
MONITOR_PID=$!

# 输出进程ID
echo "监控程序已在后台启动，PID: $MONITOR_PID"
echo "工作目录: $WORK_DIR"
echo "可以通过查看 $WORK_DIR/monitor.log 文件来跟踪监控程序的运行状态"
echo "可以通过 'kill $MONITOR_PID' 命令停止监控程序" 