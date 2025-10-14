#!/usr/bin/env python3
"""
MCUSH 基础使用示例

这个示例展示了如何使用 MCUSH 库进行基本的设备控制操作。
"""

import mcush

def basic_example():
    """基础使用示例"""
    print("MCUSH 基础使用示例")
    print("=" * 50)
    
    # 创建 MCUSH 控制器实例
    # 注意：请根据您的实际设备修改串口路径
    try:
        # 尝试连接到设备
        controller = mcush.Mcush('/dev/ttyUSB0')  # 修改为您的设备路径
        
        # 获取设备信息
        print("设备连接成功!")
        print(f"固件版本: {controller.scpiIdn()}")
        print(f"LED 数量: {controller.getLedNumber()}")
        print(f"运行时间: {controller.uptime()} 秒")
        
        # 简单的 LED 控制示例
        led_count = controller.getLedNumber()
        if led_count > 0:
            print(f"\n控制第一个 LED (索引 0):")
            controller.ledOn(0)
            print("LED 已打开")
            
            # 等待一段时间
            import time
            time.sleep(1)
            
            controller.ledOff(0)
            print("LED 已关闭")
        
        # GPIO 控制示例
        print("\nGPIO 控制示例:")
        # 这里可以添加 GPIO 控制代码
        
        # 内存操作示例
        print("\n内存操作示例:")
        # 这里可以添加内存操作代码
        
    except Exception as e:
        print(f"连接设备时出错: {e}")
        print("请检查:")
        print("1. 设备是否正确连接")
        print("2. 串口路径是否正确")
        print("3. 设备是否已上电")
        print("\n在没有实际设备的情况下，这个示例仅展示 API 用法")

def list_available_ports():
    """列出可用的串口"""
    print("\n可用串口列表:")
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(f"  - {port.device}: {port.description}")
    except ImportError:
        print("  pyserial 未安装，无法列出串口")

if __name__ == "__main__":
    basic_example()
    list_available_ports()
    
    print("\n" + "=" * 50)
    print("示例执行完成!")
    print("要使用此库，请:")
    print("1. 连接您的 MCUSH 设备")
    print("2. 修改串口路径为您的设备路径")
    print("3. 运行此脚本")