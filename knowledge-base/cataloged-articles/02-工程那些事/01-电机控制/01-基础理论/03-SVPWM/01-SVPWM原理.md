# SVPWM（空间矢量脉宽调制）

## 基本概念

SVPWM (Space Vector Pulse Width Modulation) 是一种 PWM 技术，通过合成空间矢量来控制电机电压。

**与 SPWM 的区别**：
- **SPWM**：按正弦波调制，各相独立
- **SVPWM**：按空间矢量合成，三相协同控制

**SVPWM 优势**：
1. 电压利用率提高 15.47%（从 0.866 到 1）
2. 转矩脉动更小
3. 算法统一，便于数字实现
4. 适合 FOC 控制

---

## 开关状态

### 三相逆变器拓扑

```
      +Vdc
        |
  S1──┬──┬──S3──┬──┬──S5
      │  │      │  │
     U  V     W  │
      │  │      │  │
  S4──┴──┴──S6──┴──┴──N
        |
       GND
```

### 八个基本矢量

| 矢量 | S1 S2 S3 S4 S5 S6 | u_α | u_β | 状态 |
|---|---|---|---|---|
| V0 | 0 1 0 1 0 1 | 0 | 0 | 零矢量（下桥臂） |
| V7 | 1 0 1 0 1 0 | 0 | 0 | 零矢量（上桥臂） |
| V1 | 1 0 0 1 0 1 | 2/3 | 0 | 100 |
| V2 | 1 1 0 0 0 1 | 1/3 | √3/3 | 110 |
| V3 | 0 1 0 0 1 1 | -1/3 | √3/3 | 010 |
| V4 | 0 1 1 1 0 1 | -2/3 | 0 | 011 |
| V5 | 0 0 1 1 1 0 | -1/3 | -√3/3 | 001 |
| V6 | 1 0 1 0 0 0 | 1/3 | -√3/3 | 101 |

**注**：S1, S3, S5 为上桥臂；S2, S4, S6 为下桥臂

---

## 空间矢量图

```
       β
       ↑
    V3 |     V2
       |    /|
   120°|   / |
       |  /  |
   ___,| /___|___________ α
      60°/  30°
       V4     V1

       V5     V6
```

**六扇区划分**：
- 扇区 1：0° - 60° (V1, V2)
- 扇区 2：60° - 120° (V2, V3)
- 扇区 3：120° - 180° (V3, V4)
- 扇区 4：180° - 240° (V4, V5)
- 扇区 5：240° - 300° (V5, V6)
- 扇区 6：300° - 360° (V6, V1)

---

## 矢量合成原理

### 目标矢量

给定参考电压矢量 V_ref，用相邻两个基本矢量合成：

```
V_ref = (T_a / T_s) × V_x + (T_b / T_s) × V_y + (T_0 / T_s) × V_0

其中：
T_a, T_b：基本矢量作用时间
T_0：零矢量作用时间
T_s：PWM 周期
T_a + T_b + T_0 = T_s
```

### 时间计算

参考电压坐标：
```
u_α = V_ref × cos(θ)
u_β = V_ref × sin(θ)
```

扇区判断：
```
B1 = u_β
B2 = (√3 × u_α - u_β) / 2
B3 = (-√3 × u_α - u_β) / 2

扇区号 = 4 × sign(B3) + 2 × sign(B2) + sign(B1)
```

作用时间：
```
X = √3 × T_s × u_β / V_dc
Y = (√3 × T_s × u_β + 3 × T_s × u_α) / (2 × V_dc)
Z = (√3 × T_s × u_β - 3 × T_s × u_α) / (2 × V_dc)
```

根据扇区选择 T_a, T_b：

| 扇区 | T_a | T_b | T_0 |
|---|---|---|---|
| 1 | -Z | X | T_s - T_a - T_b |
| 2 | Z | Y | T_s - T_a - T_b |
| 3 | X | -Y | T_s - T_a - T_b |
| 4 | -X | Z | T_s - T_a - T_b |
| 5 | -Y | -Z | T_s - T_a - T_b |
| 6 | Y | -X | T_s - T_a - T_b |

---

## 开关序列

### 七段式 SVPWM（常用）

以扇区 1 为例，对称分布：

```
时序：  V0  →  V1  →  V2  →  V7  →  V2  →  V1  →  V0
时间： T_0/2 T_a   T_b   T_0/2 T_b   T_a   T_0/2

开关： 000 → 100 → 110 → 111 → 110 → 100 → 000
       U V W   U V W U V W   U V W U V W U V W
```

**优点**：
- 对称分布，开关损耗小
- 零矢量时间均分，中性点稳定

### 五段式 SVPWM

```
时序：  V0  →  V1  →  V2  →  V1  →  V0
时间： T_0/2 T_a   T_b   T_a   T_0/2
```

---

## 代码实现 (C++)

```cpp
#include <math.h>

typedef struct {
    float a;
    float b;
    float c;
} PWM_Duty_t;

PWM_Duty_t svpwm(float alpha, float beta, float vdc, float pwm_period) {
    PWM_Duty_t duty = {0};

    // 扇区判断
    float b1 = beta;
    float b2 = (sqrtf(3.0f) * alpha - beta) / 2.0f;
    float b3 = (-sqrtf(3.0f) * alpha - beta) / 2.0f;

    int sector = 0;
    if (b1 > 0) sector |= 1;
    if (b2 > 0) sector |= 2;
    if (b3 > 0) sector |= 4;

    // 作用时间计算
    float X = sqrtf(3.0f) * pwm_period * beta / vdc;
    float Y = (sqrtf(3.0f) * pwm_period * beta + 3.0f * pwm_period * alpha) / (2.0f * vdc);
    float Z = (sqrtf(3.0f) * pwm_period * beta - 3.0f * pwm_period * alpha) / (2.0f * vdc);

    float Ta = 0, Tb = 0, T0 = 0;

    // 根据扇区选择
    switch (sector) {
        case 1: Ta = -Z; Tb = X; break;
        case 2: Ta = Z;  Tb = Y; break;
        case 3: Ta = X;  Tb = -Y; break;
        case 4: Ta = -X; Tb = Z; break;
        case 5: Ta = -Y; Tb = -Z; break;
        case 6: Ta = Y;  Tb = -X; break;
    }

    T0 = pwm_period - Ta - Tb;

    // 七段式分配
    float T0_2 = T0 / 2.0f;
    float Ta_2 = Ta / 2.0f;
    float Tb_2 = Tb / 2.0f;

    // PWM 占空比计算 (0-1)
    duty.a = (T0_2 + Ta_2 + Tb_2) / pwm_period;
    duty.b = (T0_2 - Ta_2 + Tb_2) / pwm_period;
    duty.c = (T0_2 + Ta_2 - Tb_2) / pwm_period;

    // 限幅
    duty.a = fmaxf(0.0f, fminf(1.0f, duty.a));
    duty.b = fmaxf(0.0f, fminf(1.0f, duty.b));
    duty.c = fmaxf(0.0f, fminf(1.0f, duty.c));

    return duty;
}
```

---

## 代码实现 (Python)

```python
import numpy as np

def svpwm(alpha, beta, vdc, pwm_period):
    """SVPWM 算法"""

    # 扇区判断
    b1 = beta
    b2 = (np.sqrt(3) * alpha - beta) / 2
    b3 = (-np.sqrt(3) * alpha - beta) / 2

    sector = (1 if b1 > 0 else 0) | (2 if b2 > 0 else 0) | (4 if b3 > 0 else 0)

    # 作用时间计算
    X = np.sqrt(3) * pwm_period * beta / vdc
    Y = (np.sqrt(3) * pwm_period * beta + 3 * pwm_period * alpha) / (2 * vdc)
    Z = (np.sqrt(3) * pwm_period * beta - 3 * pwm_period * alpha) / (2 * vdc)

    # 扇区时间分配
    Ta, Tb = 0, 0
    if sector == 1:
        Ta, Tb = -Z, X
    elif sector == 2:
        Ta, Tb = Z, Y
    elif sector == 3:
        Ta, Tb = X, -Y
    elif sector == 4:
        Ta, Tb = -X, Z
    elif sector == 5:
        Ta, Tb = -Y, -Z
    elif sector == 6:
        Ta, Tb = Y, -X

    T0 = pwm_period - Ta - Tb

    # 七段式 PWM 占空比
    duty_a = (T0 + Ta + Tb) / (2 * pwm_period)
    duty_b = (T0 - Ta + Tb) / (2 * pwm_period)
    duty_c = (T0 + Ta - Tb) / (2 * pwm_period)

    # 限幅
    duty_a = np.clip(duty_a, 0, 1)
    duty_b = np.clip(duty_b, 0, 1)
    duty_c = np.clip(duty_c, 0, 1)

    return duty_a, duty_b, duty_c, sector

# 示例
alpha, beta = 0.5, 0.3
vdc = 24.0
pwm_period = 1.0 / 20000.0  # 20kHz

da, db, dc, sector = svpwm(alpha, beta, vdc, pwm_period)
print(f"扇区: {sector}, 占空比: a={da:.3f}, b={db:.3f}, c={dc:.3f}")
```

---

## 电压利用率

### SPWM 最大输出

```
V_spwm_max = V_dc / √2 ≈ 0.707 × V_dc
```

### SVPWM 最大输出

```
V_svpwm_max = V_dc / √3 × √3 = V_dc / √3 × 2/√3 = V_dc / √3 × 1.1547
          = V_dc / √3 × 1.1547 ≈ 0.866 × V_dc
```

**提高比例**：0.866 / 0.707 ≈ 1.1547 → 提高 15.47%

---

## 过调制

当参考矢量超过内切圆时，进入过调制区：

1. **线性区**：|V_ref| ≤ V_dc/√3
2. **过调制 I 区**：V_dc/√3 < |V_ref| < V_dc/√2
3. **过调制 II 区（六步模式）**：|V_ref| ≥ V_dc/√2

处理方法：
- 幅值限幅
- 角度修正
- 逐步过渡到六步换相

---

## 常见问题

### Q1: SVPWM 为什么比 SPWM 电压利用率高？

**答**：
- SPWM：各相独立，最大相电压 = V_dc/2
- SVPWM：合成空间矢量，利用零矢量，最大线电压 = V_dc
- SVPWM 将电压"集中"利用，提高 15.47%

### Q2: 为什么需要零矢量？

**答**：
1. 控制矢量幅值
2. 均分开关时间，对称性
3. 提供死区时间
4. 降低开关损耗

### Q3: 死区时间如何处理？

**答**：
- 插入死区时间 T_dead
- 确保上下桥臂不直通
- 影响输出电压，需要补偿

```cpp
duty.a = min(max(duty.a - T_dead/T_period, 0), 1);
```

---

## 参考资源

- [SimpleFOC 理论文档](https://docs.simplefoc.com/foc_theory)
- [TI SVPWM 应用报告](https://www.ti.com/)
- [Wikipedia: Space vector modulation](https://en.wikipedia.org/wiki/Space_vector_modulation)