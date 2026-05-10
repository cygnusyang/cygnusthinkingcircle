# STM32 FOC SDK 入门指南

## 概述

STM32 提供官方的电机控制 SDK，包括 X-CUBE-MOTOR 和 STM32 Motor Workbench。

**优势**：
- 官方支持，稳定性高
- 代码生成工具
- 丰富的示例和文档

---

## 官方资源

| 资源 | 链接 |
|---|---|
| X-CUBE-MOTOR 下载 | https://www.st.com/en/development-tools/stm32cubemx |
| STM32 Motor Workbench | https://www.st.com/en/development-tools/stm32-motor-workbench |
| 电机控制培训 | https://www.st.com/en/development-tools/motor-control-sdks |
| 官方论坛 | https://community.st.com/ |

---

## STM32 系列支持

| 系列 | 特性 | 适用场景 |
|---|---|---|
| **STM32G4** | 高分辨率定时器、数学加速器 | FOC 专用，高性能 |
| **STM32F3** | 增强型 FOC | 中高端 FOC 应用 |
| **STM32F4** | 高性能、DSP 指令 | 高速、高精度控制 |
| **STM32H7** | 超高性能、双精度 | 复杂控制算法 |

---

## STM32 Motor Workbench

### 功能概述

Motor Workbench 是图形化配置工具，可以：

1. **生成 FOC 项目代码**
2. **配置电机参数**
3. **调整控制参数**
4. **实时监控**
5. **数据记录和分析**

### 使用流程

```
1. 选择电机类型
   ├─ BLDC
   ├─ PMSM
   ├─ 有刷直流
   └─ 步进电机

2. 配置硬件
   ├─ MCU 选择
   ├─ 功率级配置
   ├─ 反馈设备
   └─ 驱动器类型

3. 设置 FOC 参数
   ├─ 极对数
   ├─ 电机常数
   ├─ 电流环参数
   └─ 速度环参数

4. 生成代码
   ├─ IDE 项目文件
   ├─ HAL 驱动
   └─ 电机控制库

5. 集成到项目
   ├─ 编译调试
   ├─ 功能扩展
   └─ 产品化
```

---

## X-CUBE-MOTOR 包结构

### 核心组件

```
X-CUBE-MOTOR/
├── Drivers/              # HAL 驱动
├── Inc/                 # 头文件
├── Middlewares/          # 中间件
│   └── ST/             # ST 官方库
│       ├── mc_stm32g4xx_hal_p.h    # HAL 配置
│       ├── mc_math.h               # 数学库
│       ├── mc_motor_type.h          # 电机类型定义
│       ├── mc_interface.h           # 接口定义
│       ├── mc_state_machine.h       # 状态机
│       ├── mc_tasks.h             # 任务管理
│       └── mc_config.h             # 配置文件
├── Src/                 # 源文件
│   ├── main.c               # 主程序
│   ├── mc_it.c              # 中断服务
│   └── ...                  # 应用代码
└── EWARM/               # IDE 项目文件
```

### 主要 API 函数

#### 1. 初始化

```c
/* FOC 初始化 */
void MC_Init(void);

/* 电机初始化 */
void MX_Motor_Init(void);

/* PID 初始化 */
PID_Handle_t *PID_Init(float hKpGain, float hKiGain,
                      float hKdGain, uint16_t hLowerLimit,
                      uint16_t hUpperLimit, float hK1);
```

#### 2. 控制函数

```c
/* 设置目标速度 */
void MC_SetMecSpeed(float mecSpeedUnit);

/* 设置目标转矩 */
void MC_SetTorque(float torque);

/* 启用/禁用电机 */
MotorState_t MC_StartMotor(void);
MotorState_t MC_StopMotor(void);

/* 获取电机状态 */
uint16_t MC_GetAppState(void);
int16_t MC_GetMecSpeed(void);
int16_t MC_GetTorque(void);
```

#### 3. 状态机

```c
typedef enum {
    IDLE = 0,          /* 空闲状态 */
    STARTUP,            /* 启动中 */
    RUN,                /* 运行中 */
    STOP,               /* 停止中 */
    FAULT               /* 故障状态 */
} MotorState_t;
```

---

## FOC 实现结构

### 中断服务程序

```c
/* 高优先级 PWM 中断 */
void TIMx_UP_IRQHandler(void) {
    /* 清除中断标志 */
    LL_TIM_ClearFlag(TIMx, LL_TIM_FLAG_UPDATE);

    /* FOC 计算 */
    TSK_FOC();

    /* SVPWM 输出 */
    TSK_PWM_Update();
}

/* 中优先级 ADC 中断 */
void ADCx_IRQHandler(void) {
    /* 电流采样 */
    TSK_CurrentMeasurement();

    /* 触发 FOC 计算 */
    MC_SetCurrentBufferValues();
}
```

### FOC 任务流程

```c
void TSK_FOC(void) {
    /* 1. 读取电流 */
    int16_t Ia, Ib, Ic;
    MC_GetCurrent(&Ia, &Ib, &Ic);

    /* 2. Clarke 变换 */
    float Ialpha, Ibeta;
    MC_ClarkeTransform(Ia, Ib, Ic, &Ialpha, &Ibeta);

    /* 3. 读取位置 */
    float theta;
    theta = MC_GetRotorAngle();

    /* 4. Park 变换 */
    float Id, Iq;
    MC_ParkTransform(Ialpha, Ibeta, theta, &Id, &Iq);

    /* 5. PI 控制 */
    float Vd, Vq;
    MC_PIController(&PID_d, Id_ref - Id, &Vd);
    MC_PIController(&PID_q, Iq_ref - Iq, &Vq);

    /* 6. 逆 Park 变换 */
    float Valpha, Vbeta;
    MC_InverseParkTransform(Vd, Vq, theta, &Valpha, &Vbeta);

    /* 7. SVPWM 调制 */
    MC_SVPWM(Valpha, Vbeta, &duty_a, &duty_b, &duty_c);
}
```

---

## 常用配置示例

### 电流环 PI 整定

```c
/* 电机参数 */
float R_phase = 0.5f;        // 相电阻
float L_phase = 0.0005f;      // 相电感

/* 期望带宽 */
float bandwidth = 2000.0f;    // 2kHz

/* PI 参数计算 */
float Kp = L_phase * bandwidth;
float Ki = R_phase * bandwidth;

/* 初始化 PID */
PID_Handle_t *pid_d = PID_Init(Kp, Ki, 0, 0, 1000, 1.0f);
PID_Handle_t *pid_q = PID_Init(Kp, Ki, 0, 0, 1000, 1.0f);
```

### 速度环 PID 整定

```c
/* 期望带宽 */
float speed_bandwidth = 100.0f;  // 100Hz

/* PID 参数（试错法开始） */
float Kp_speed = 0.5f;
float Ki_speed = 10.0f;
float Kd_speed = 0.001f;

/* 初始化 PID */
PID_Handle_t *pid_speed = PID_Init(Kp_speed, Ki_speed, Kd_speed,
                                      -2000, 2000, 100.0f);
```

---

## 自定义开发

### 添加自定义算法

1. **创建新文件**：
```c
/* my_custom_foc.c */
#include "mc_interface.h"

void MyCustomFOC(void) {
    /* 自定义 FOC 算法 */
}

void MyCustomControl(void) {
    /* 自定义控制策略 */
}
```

2. **集成到任务**：
```c
/* mc_tasks.c */
extern void MyCustomFOC(void);

void TSK_FOC(void) {
#ifdef USE_CUSTOM_FOC
    MyCustomFOC();
#else
    ST_FOC();  /* 官方实现 */
#endif
}
```

3. **编译测试**：
```bash
# STM32CubeIDE 或 Keil MDK
# 编译项目
# 下载到开发板
# 调试验证
```

---

## 调试技巧

### 实时变量监控

```c
/* 使用 SWV (Serial Wire Viewer) */
void MC_DebugUpdate(void) {
    /* 更新调试变量 */
    DbgVar1 = Id_measured;
    DbgVar2 = Iq_measured;
    DbgVar3 = Speed_measured;
}

/* 在 STM32CubeIDE 中配置 ITM */
/* View → Serial Wire Viewer → Setup */
```

### 数据记录

```c
/* 使用 USB 虚拟串口 */
void MC_SendData(void) {
    char buffer[64];
    sprintf(buffer, "%d,%d,%d\n", Id, Iq, Speed);
    CDC_Transmit_FS((uint8_t *)buffer, strlen(buffer));
}
```

---

## 常见问题

### Q1: 编译错误"undefined reference to..."

**答**：
1. 检查头文件包含
2. 确认库路径配置
3. 重新生成代码

### Q2: 电机不转动或抖动？

**答**：
1. 检查三相接线顺序
2. 确认传感器对齐
3. 调整 PI 参数
4. 检查 PWM 频率

### Q3: 如何切换到自定义 MCU？

**答**：
1. 在 Motor Workbench 中选择目标 MCU
2. 重新生成代码
3. 检查时钟和引脚配置
4. 调整中断优先级

### Q4: 双电机如何实现？

**答**：
1. 使用双定时器
2. 使用双 ADC 组
3. 配置两个电机实例
4. 资源共享冲突处理

---

## 参考资源

- [STM32 官方文档](https://www.st.com/content/st_com/en/products/embedded-software/motor-control-software.html)
- [X-CUBE-MOTOR 用户手册](https://www.st.com/resource/en/user_manual/DM0042485/)
- [电机控制培训材料](https://www.st.com/en/development-tools/motor-control-sdks)

---

## STM32 SDK vs SimpleFOC vs VESC

| 特性 | STM32 SDK | SimpleFOC | VESC |
|---|---|---|---|
| **易用性** | 中（需配置工具） | 高（Arduino 友好） | 中（PC Tool） |
| **性能** | 最高（原生 HAL） | 中（依赖 Arduino） | 高（优化固件） |
| **灵活性** | 高（源码完全） | 中（库封装） | 中（固件限制） |
| **学习曲线** | 陡 | 缓 | 中 |
| **适用场景** | 产品开发 | 原型/学习 | 工程应用 |