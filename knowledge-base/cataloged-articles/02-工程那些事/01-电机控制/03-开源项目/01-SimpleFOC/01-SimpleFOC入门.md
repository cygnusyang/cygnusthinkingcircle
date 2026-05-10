# SimpleFOC 入门指南

## 项目概述

SimpleFOC 是一个跨平台的 FOC 控制库，专为 BLDC 和步进电机设计。

**定位**：
- "解密 FOC 算法"
- 让 FOC 控制变得简单易用
- 支持尽可能多的硬件组合

---

## 官方资源

| 资源 | 链接 |
|---|---|
| GitHub 仓库 | https://github.com/simplefoc/Arduino-FOC |
| 官方文档 | https://docs.simplefoc.com/ |
| 社区论坛 | https://community.simplefoc.com/ |
| Discord | https://discord.gg/kWBwuzY32n |
| 官方驱动板 | https://docs.simplefoc.com/boards |

---

## 支持的硬件

### MCU 平台

| 平台 | 支持型号 |
|---|---|
| **Arduino** | UNO, MEGA, DUE, Nano, MKR, Portenta |
| **STM32** | Nucleo, Bluepill, B-G431B-ESC1, H7 系列 |
| **ESP32** | ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6 |
| **RP2040/2350** | Raspberry Pi Pico |
| **Teensy** | 3.x, 4.x |
| **SAMD** | Arduino Zero, MKR 系列 |
| **MBED** | Portenta, Nano 33 BLE |

### 电机类型

- BLDC 电机（无刷直流）
- 步进电机（两相/四相）

### 传感器

- 编码器 (ABZ 相位)
- 磁编码器 (AS5600, AS5048 等)
- Hall 传感器
- 无传感器（观测器）

---

## 安装方法

### Arduino IDE

1. 打开 Arduino IDE
2. 进入 工具 → 管理库
3. 搜索 "SimpleFOC"
4. 安装最新版本

### PlatformIO

```
[env:uno]
platform = atmelavr
board = uno
lib_deps =
    SimpleFOC
```

---

## SimpleFOC 核心组件

### 1. BLDCMotor 类

电机对象，封装电机参数和控制方法。

```cpp
BLDCMotor motor = BLDCMotor(
    POLE_PAIRS,        // 极对数
    R_PHASE,           // 相电阻 (Ω)
    KV,                // KV 值 (RPM/V)
    INDUCTANCE,         // 相电感 (可选)
    VOLTAGE_LIMIT      // 电压限制 (可选)
);
```

### 2. 驱动器类

不同驱动器继承自 `BLDCDriver`。

**BLDCDriver3PWM**（常用）:
```cpp
BLDCDriver3PWM driver = BLDCDriver3PWM(
    PIN_PWM_U, PIN_PWM_V, PIN_PWM_W,    // PWM 引脚
    PIN_EN_U, PIN_EN_V, PIN_EN_W,      // 使能引脚（可选）
    VOLTAGE_POWER_SUPPLY                 // 电源电压
);
```

### 3. 传感器类

不同传感器继承自 `Sensor`。

**MagneticSensorI2C** (AS5600):
```cpp
MagneticSensorI2C sensor = MagneticSensorI2C(
    AS5600_I2C,     // 传感器地址
    12,              // 总位宽
    0x36,            // I2C 地址
    4.2              // 完整旋转所需位数
);
```

### 4. 电流传感类

不同电流传感继承自 `CurrentSense`。

**InlineCurrentSense**（常用）:
```cpp
InlineCurrentSense current_sense = InlineCurrentSense(
    0.005,      // 增益
    20.0,        // ADC 参考电压
    PIN_A, PIN_B, PIN_C  // ADC 引脚
);
```

---

## SimpleFOC 完整示例

### 最小示例（开环速度控制）

```cpp
#include <SimpleFOC.h>

// 电机定义
BLDCMotor motor = BLDCMotor(11, 0.3, 120);

// 驱动器
BLDCDriver3PWM driver = BLDCDriver3PWM(
    9, 10, 11,    // PWM 引脚
    5, 6, 7,      // 使能引脚
    12.0           // 电源电压
);

void setup() {
    // 驱动器配置
    driver.voltage_power_supply = 12.0;
    driver.init();

    // 电机链接驱动器
    motor.linkDriver(&driver);

    // 传感器（可选，此处开环不需要）
    // motor.linkSensor(&sensor);

    // 电机初始化
    motor.init();
    motor.initFOC();

    // 设置控制模式
    motor.controller = MotionControlType::velocity_openloop;

    Serial.begin(115200);
    Serial.println("Motor ready.");
    Serial.println("Set target velocity using serial terminal:");
}

void loop() {
    motor.loopFOC();
    motor.move();

    // 串口读取目标速度
    if (Serial.available() > 0) {
        float target_velocity = Serial.parseFloat();
        if (Serial.read() == '\n') {
            motor.target = target_velocity;
            Serial.print("Target velocity: ");
            Serial.println(target_velocity);
        }
    }
}
```

### 闭环速度控制（带编码器）

```cpp
#include <SimpleFOC.h>

// 电机定义
BLDCMotor motor = BLDCMotor(11, 0.3, 120);

// 驱动器
BLDCDriver3PWM driver = BLDCDriver3PWM(
    9, 10, 11, 5, 6, 7, 12.0);

// 编码器
Encoder encoder = Encoder(2, 3, 2048);  // A, B, PPR

void setup() {
    Serial.begin(115200);

    // 编码器初始化
    encoder.init();
    motor.linkSensor(&encoder);

    // 驱动器初始化
    driver.voltage_power_supply = 12.0;
    driver.init();
    motor.linkDriver(&driver);

    // 电机初始化
    motor.init();
    motor.initFOC();

    // PID 整定
    motor.PID_velocity.P = 0.2;
    motor.PID_velocity.I = 20;
    motor.PID_velocity.D = 0;

    // 速度控制模式
    motor.controller = MotionControlType::velocity;

    Serial.println("Motor ready.");
    Serial.println("Set target velocity [rad/s]:");
}

void loop() {
    motor.loopFOC();
    motor.move();

    // 打印状态
    if (Serial.available()) {
        float target_velocity = Serial.parseFloat();
        if (Serial.read() == '\n') {
            motor.target = target_velocity;
            Serial.print("Target: ");
            Serial.println(target_velocity);
        }
    }

    // 定时打印
    static unsigned long last_print = 0;
    if (millis() - last_print > 100) {
        Serial.print("Velocity: ");
        Serial.print(motor.shaft_velocity);
        Serial.print(" rad/s, Angle: ");
        Serial.println(motor.shaft_angle);
        last_print = millis();
    }
}
```

### 位置控制（三环）

```cpp
#include <SimpleFOC.h>

BLDCMotor motor = BLDCMotor(11, 0.3, 120);
BLDCDriver3PWM driver = BLDCDriver3PWM(9, 10, 11, 5, 6, 7, 12.0);
Encoder encoder = Encoder(2, 3, 2048);

void setup() {
    Serial.begin(115200);

    encoder.init();
    motor.linkSensor(&encoder);

    driver.voltage_power_supply = 12.0;
    driver.init();
    motor.linkDriver(&driver);

    motor.init();
    motor.initFOC();

    // 速度环 PID
    motor.PID_velocity.P = 0.2;
    motor.PID_velocity.I = 20;
    motor.PID_velocity.D = 0.001;

    // 位置环 PID (P_angle)
    motor.P_angle.P = 20;

    // 位置控制模式（串级）
    motor.controller = MotionControlType::angle;

    Serial.println("Motor ready.");
    Serial.println("Set target position [rad]:");
}

void loop() {
    motor.loopFOC();
    motor.move();

    if (Serial.available()) {
        float target_angle = Serial.parseFloat();
        if (Serial.read() == '\n') {
            motor.target = target_angle;
            Serial.print("Target: ");
            Serial.println(target_angle);
        }
    }
}
```

---

## PID 参数整定

### SimpleFOC PID 控制器

```cpp
// 速度环
motor.PID_velocity.P = 0.2;   // 比例增益
motor.PID_velocity.I = 20.0;  // 积分增益
motor.PID_velocity.D = 0.0;   // 微分增益
motor.PID_velocity.output_ramp = 100; // 输出限幅率

// 位置环 (P_angle)
motor.P_angle.P = 20.0;

// 电流环（需要电流传感）
motor.PID_current_q.P = 5;
motor.PID_current_q.I = 100;
motor.PID_current_d.P = 5;
motor.PID_current_d.I = 100;
```

### 整定步骤

1. **电流环整定**（如有电流传感）
   - 使用 `motor.voltage_limit` 限制
   - 逐步增大 Kp 直到快速响应
   - 添加 Ki 消除稳态误差

2. **速度环整定**
   - 设置 `controller = MotionControlType::velocity`
   - 从小 Kp 开始，逐步增大
   - 观察 speed 响应曲线

3. **位置环整定**
   - 设置 `controller = MotionControlType::angle`
   - 调整 P_angle 实现精确定位

---

## SimpleFOCStudio

SimpleFOC 提供可视化调试工具：

### 功能

- 实时监控电机状态
- PID 参数实时调整
- 数据记录和导出
- 多电机支持

### 使用

1. 下载 SimpleFOCStudio
2. 连接电机串口
3. 选择 COM 端口和波特率
4. 开始监控和调整

---

## 实用函数

### 电机参数测量

```cpp
// 自动参数测量
motor.useMonitoring(Serial);
motor.init();
motor.initFOC();
motor.alignSensor();  // 传感器对齐
```

### 低功耗模式

```cpp
motor.enable();   // 启用电机
motor.disable();  // 禁用电机
```

### 保护功能

```cpp
// 电压限制
motor.voltage_limit = 6.0;

// 速度限制
motor.velocity_limit = 10.0;

// 电流限制（需要电流传感）
motor.current_limit = 2.0;
```

---

## 常见问题

### Q1: 如何选择极对数？

**答**：
- 极对数 = 物理极数 / 2
- 例如：12 极电机，极对数 = 6
- 不确定可测量：缓慢转动，观察编码器变化

### Q2: encoder.init() 失败？

**答**：
- 检查引脚是否正确
- 确认编码器类型（ABZ）
- 尝试手动旋转，观察输出

### Q3: 电机抖动或振荡？

**答**：
1. PID 参数过大，减小 P
2. 采样频率不够，增加 `loopFOC()` 调用频率
3. 噪声干扰，添加滤波

### Q4: FOC 初始化失败？

**答**：
1. 检查驱动器使能引脚
2. 确认电源电压正确
3. 检查传感器连接
4. 查看 `initFOC()` 错误消息

---

## 进阶主题

### 电流传感

```cpp
InlineCurrentSense current_sense = InlineCurrentSense(0.005, 20.0, A0, A1, A2);
motor.linkCurrentSense(&current_sense);
current_sense.init();
```

### 无传感器 FOC

```cpp
HALLSensor hall = HALLSensor(2, 3, 4, 7, 5);  // U, V, W, Pin, Poles
motor.linkSensor(&hall);
hall.init();
```

### 多电机控制

```cpp
BLDCMotor motor1 = BLDCMotor(...);
BLDCMotor motor2 = BLDCMotor(...);
// 两个独立的电机对象和控制循环
```

---

## 参考资源

- [SimpleFOC 官方文档](https://docs.simplefoc.com/)
- [SimpleFOC 示例代码](https://github.com/simplefoc/Arduino-FOC/tree/master/examples)
- [SimpleFOC 理论角](https://docs.simplefoc.com/theory_corner)
- [社区论坛](https://community.simplefoc.com/)