# VESC 入门指南

## 项目概述

VESC (Vedder's Electric Speed Controller) 是一个开源的直流/无刷/FOC 电机控制器固件项目。

**定位**：工业级、功能全面的电机控制器

---

## 官方资源

| 资源 | 链接 |
|---|---|
| GitHub 仓库 | https://github.com/vedderb/bldc |
| 官方网站 | https://vesc-project.com/ |
| 论坛 | https://vesc-project.com/forum |
| Discord | https://discord.gg/JgvV5NwYts |
| 固件构建指南 | https://github.com/vedderb/bldc/wiki |

---

## 主要特性

### 支持的电机类型

- **有刷直流电机**：简单、低成本
- **无刷电机 (BLDC)**：六步换相或 FOC
- **FOC 模式**：精确控制、高效率

### 高级功能

- **无传感器控制**：滑模观测器
- **电流闭环**：精确转矩控制
- **速度闭环**：PID 控制
- **位置控制**：伺服模式
- **CAN 总线**：多电机协同
- **UART 通信**：PC 工具通信
- **ADC 输入**：模拟量采集
- **故障保护**：过压、过流、过温

---

## 支持的硬件

### VESC 版本

| 版本 | 特点 | 适用场景 |
|---|---|---|
| **VESC 4.12** | 小尺寸，适合小电机 | 桌面机器人、小型无人机 |
| **VESC 6** | 中等尺寸，功能齐全 | 电动车、滑板 |
| **VESC 75/300** | 大功率，高性能 | 电动汽车、工业驱动 |
| **Flipsky Mini** | 小尺寸、低成本 | 教育、业余项目 |

### 支持的 MCU

- STM32F405（VESC 4）
- STM32F407（VESC 6）
- STM32F405/F411（Flipsky）

---

## 固件编译

### 环境准备

1. **安装 ARM GCC 工具链**
```bash
# Ubuntu/Debian
sudo apt-get install gcc-arm-none-eabi

# macOS
brew install gcc-arm-embedded
```

2. **安装 STM32CubeCL**
   用于烧录固件

### 编译固件

```bash
# 克隆仓库
git clone https://github.com/vedderb/bldc.git
cd bldc

# 编译默认配置
make

# 查看所有目标
make

# 编译特定目标
make HW_VERSION=VESC6
```

### 烧录固件

1. 连接 ST-Link 或 USB
2. 运行 STM32CubeCL
3. 选择固件文件（.hex）
4. 烧录

---

## VESC Tool

VESC Tool 是官方的 PC 配置和监控工具。

### 下载

- Windows: https://vesc-project.com/vesc-tool
- macOS: https://vesc-project.com/vesc-tool
- Linux: 从源码编译

### 主要功能

#### 1. 连接设置

- USB 连接（默认）
- CAN 连接（多电机）
- 配置波特率

#### 2. 电机设置

```
电机配置页面：
├── 电机极数
├── 电流限制（启动/运行）
├── 电池电流限制
├── 输入电压范围
└── 最小/最大转速
```

#### 3. FOC 设置

```
FOC 配置页面：
├── 观测器增益
├── 观测器偏置
├── 电流控制带宽
├── Ld/Lq 电感
└── R_phase 相电阻
```

#### 4. PID 调试

```
PID 调试页面：
├── 实时曲线显示
├── 速度环 PID 参数
├── 电流环 PID 参数
├── 输入阶跃测试
└── 自动整定（部分版本）
```

#### 5. 数据记录

```
数据记录页面：
├── 选择记录变量（电流、电压、速度、位置）
├── 设置采样率
├── 开始/停止记录
└── 导出 CSV 文件
```

---

## VESC 通信协议

### UART 协议

VESC 使用自定义的 UART 协议，支持：

1. **命令格式**
   - 起始字节：0x02
   - 命令字节
   - 数据长度
   - 数据
   - CRC 校验
   - 结束字节：0x03

2. **常用命令**

| 命令 | ID | 功能 |
|---|---|---|
| COMM_GET_VALUES | 0x00 | 获取实时数据 |
| COMM_SET_DUTY | 0x01 | 设置占空比 |
| COMM_SET_CURRENT | 0x02 | 设置电流 |
| COMM_SET_RPM | 0x03 | 设置转速 |
| COMM_SET_POS | 0x04 | 设置位置 |
| COMM_SET_CURRENT_BRAKE | 0x05 | 设置制动电流 |
| COMM_GET_MCCONF | 0x0E | 获取电机配置 |
| COMM_SET_MCCONF | 0x0F | 设置电机配置 |

### CAN 总线协议

支持多电机 CAN 通信：

```
CAN 消息格式：
├── CAN ID：电机地址
├── 数据字节：命令 + 参数
└── 扩展帧支持
```

**常用场景**：
- 双轮驱动（左/右电机）
- 多轴机器人
- 主从控制

---

## 配置步骤

### 新电机配置流程

1. **连接 VESC**
   - USB 连接
   - 打开 VESC Tool
   - 选择正确的端口

2. **检测电机参数**
   - 进入 Motor Setup
   - 使用"检测电感"功能
   - 使用"检测电阻"功能

3. **极对数设置**
   - 根据电机规格设置
   - 不确定可尝试 7, 11, 14 等

4. **电流限制**
   - 设置启动电流（较小）
   - 设置运行电流（额定）
   - 设置电池电流限制

5. **速度限制**
   - 设置最小/最大转速
   - 反电动势限制

6. **FOC 模式启用**
   - 开启 FOC
   - 设置观测器参数
   - 调试电流环

7. **PID 整定**
   - 速度环 PID
   - 电流环 PID（如需要）
   - 使用阶跃响应测试

8. **保存配置**
   - 写入固件
   - 断电重启验证

---

## PID 整定（VESC Tool）

### 速度环整定

1. 进入 PID 调试页面
2. 选择速度控制模式
3. 设置初始 PID：
   - Kp: 0.01
   - Ki: 0.05
   - Kd: 0.0001
4. 给定阶跃速度指令
5. 观察响应曲线：
   - **超调**：减小 Kp 或增加 Kd
   - **响应慢**：增大 Kp
   - **稳态误差**：增大 Ki
6. 迭代优化

### 电流环整定（FOC 模式）

1. 进入 FOC 设置
2. 调整电流环带宽：
   - 太低：响应慢
   - 太高：噪声大
3. 典型值：2000-5000 rad/s

---

## 常见问题

### Q1: VESC 无法连接？

**答**：
1. 检查 USB 线和端口
2. 确认 VESC 已上电
3. 尝试不同波特率（115200/230400/460800）
4. 检查驱动是否安装

### Q2: 电机不转动？

**答**：
1. 检查电机接线（U、V、W）
2. 检查霍尔传感器连接
3. 确认极对数设置
4. 检查电流限制（可能太低）
5. 尝试低占空比测试

### Q3: 电机抖动或噪声大？

**答**：
1. PID 参数不当，重新整定
2. 观测器增益太大
3. 电流环带宽不当
4. 检查电源质量

### Q4: 如何使用 CAN 多电机？

**答**：
1. 连接 CAN 总线
2. 配置不同 CAN ID
3. 主控制器发送 CAN 指令
4. 参考 VESC Wiki CAN 协议

---

## 进阶功能

### 无传感器 FOC

VESC 内置滑模观测器，实现无传感器 FOC：

```
优势：
├── 无需编码器/Hall
├── 成本低
└── 维护简单

缺点：
├── 低速性能差
├── 启动需要开环
└── 动态响应慢
```

### ADC 输入使用

VESC 提供 3 个 ADC 输入，可用于：

- 节气阀控制
- 油门信号读取
- 电压/电流采样

### 自定义应用

VESC 支持自定义应用开发：

1. 修改固件源码
2. 编译自定义固件
3. 烧录测试

---

## 参考资源

- [VESC GitHub Wiki](https://github.com/vedderb/bldc/wiki)
- [VESC 论坛](https://vesc-project.com/forum)
- [Benjamin Vedder 的 YouTube 频道](https://www.youtube.com/c/Vedder)

---

## SimpleFOC vs VESC

| 特性 | SimpleFOC | VESC |
|---|---|---|
| 易用性 | 高（面向 Arduino） | 中（需要 PC Tool） |
| 硬件支持 | 广泛（多种 MCU） | 专用 VESC 硬件 |
| 功能 | 基础 FOC 控制 | 全面（工业级） |
| 学习曲线 | 低 | 中高 |
| 成本 | 低（自备硬件） | 中（购买硬件） |
| 开源 | 是 | 是（GPL v3） |
| 社区支持 | 活跃（中文友好） | 活跃（英文） |

**推荐**：
- **初学者**：从 SimpleFOC 开始
- **工程应用**：考虑 VESC