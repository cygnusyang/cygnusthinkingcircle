# Park 变换（两相静止 → 两相旋转）

## 变换目的

将两相静止坐标系 (αβ) 变换为两相旋转坐标系 (dq)，使交流量变换为直流量。

**原因**：
1. αβ 坐标系下电流为正弦交流
2. dq 坐标系随转子旋转，电流变为直流
3. 直流量便于 PI 控制（无稳态误差）

---

## 坐标系定义

### 两相静止坐标系 (αβ)

```
     β
    |
    O-----α
```

- **α 轴**：固定在定子上，水平向右
- **β 轴**：固定在定子上，垂直向上
- **坐标系不旋转**

### 两相旋转坐标系 (dq)

```
        q
        ↑
        |
   d <--O
        |
```

- **d 轴**（direct）：与转子磁场方向重合
- **q 轴**（quadrature）：d 轴逆时针 90°
- **坐标系随转子旋转，电角度 θ_el**

---

## 变换公式

### 正向 Park 变换 (αβ → dq)

```
i_d = i_α × cos(θ_el) + i_β × sin(θ_el)
i_q = -i_α × sin(θ_el) + i_β × cos(θ_el)
```

**物理意义**：
- **i_d**：与转子磁场平行的电流分量（励磁电流）
- **i_q**：与转子磁场垂直的电流分量（转矩电流）

### 逆 Park 变换 (dq → αβ)

```
u_α = u_d × cos(θ_el) - u_q × sin(θ_el)
u_β = u_d × sin(θ_el) + u_q × cos(θ_el)
```

---

## 矩阵形式

### 正向 Park 变换矩阵

```
[i_d]   [ cos(θ)   sin(θ)] [i_α]
[i_q] = [-sin(θ)   cos(θ)] [i_β]
```

### 逆 Park 变换矩阵

```
[u_α]   [ cos(θ)  -sin(θ)] [u_d]
[u_β] = [ sin(θ)   cos(θ)] [u_q]
```

**注意**：逆变换矩阵是正变换矩阵的转置（正交矩阵）

---

## 时空矢量图

```
dq 坐标系随转子旋转

     β (静止)
    |
    |      q (旋转)
    |      ↑
    |     /
    |    /
    |   / d (旋转)
    |  /
    | /
    O--------α (静止)

θ_el: dq 坐标系相对于 αβ 坐标系的角度
```

---

## 最大转矩条件

### 转矩方程

```
τ = k_t × i_q

其中：
τ = 电磁转矩
k_t = 转矩常数
i_q = q 轴电流（转矩电流）
```

### 最大转矩策略

**i_d = 0 控制**：
- 让所有电流用于产生转矩
- d 轴电流为零，无无效磁场
- 适用于表贴式永磁电机 (SPM)

**i_d < 0 控制**（弱磁）：
- 减弱磁场，提高转速
- 适用于高速运行
- 会牺牲一些转矩

---

## 代码实现 (C++)

```cpp
// Park 变换
typedef struct {
    float d;
    float q;
} DQ_t;

typedef struct {
    float alpha;
    float beta;
} AlphaBeta_t;

DQ_t park_transform(float alpha, float beta, float theta_el) {
    DQ_t dq;

    float sin_theta = sinf(theta_el);
    float cos_theta = cosf(theta_el);

    dq.d = alpha * cos_theta + beta * sin_theta;
    dq.q = -alpha * sin_theta + beta * cos_theta;

    return dq;
}

// 逆 Park 变换
AlphaBeta_t inverse_park_transform(float d, float q, float theta_el) {
    AlphaBeta_t ab;

    float sin_theta = sinf(theta_el);
    float cos_theta = cosf(theta_el);

    ab.alpha = d * cos_theta - q * sin_theta;
    ab.beta = d * sin_theta + q * cos_theta;

    return ab;
}
```

---

## 代码实现 (Python)

```python
import numpy as np

def park_transform(alpha, beta, theta):
    """Park 变换: αβ -> dq"""
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    d = alpha * cos_theta + beta * sin_theta
    q = -alpha * sin_theta + beta * cos_theta

    return d, q

def inverse_park_transform(d, q, theta):
    """逆 Park 变换: dq -> αβ"""
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    alpha = d * cos_theta - q * sin_theta
    beta = d * sin_theta + q * cos_theta

    return alpha, beta

# 示例：旋转矢量
theta = np.pi / 4  # 45°
alpha, beta = 1, 1  # 45° 矢量

d, q = park_transform(alpha, beta, theta)
print(f"d = {d:.3f}, q = {q:.3f}")
# 结果：d ≈ 1.414, q ≈ 0（矢量与 d 轴对齐）

# 验证逆变换
alpha_back, beta_back = inverse_park_transform(d, q, theta)
print(f"α = {alpha_back:.3f}, β = {beta_back:.3f}")
```

---

## 实例分析

### 例1：矢量与 d 轴对齐

```
αβ 坐标系：α = √2, β = 0（矢量在 α 轴）
电角度：θ_el = 45°
```

计算：
```
cos(45°) = sin(45°) = √2/2 ≈ 0.707

i_d = √2 × 0.707 + 0 × 0.707 = 1
i_q = -√2 × 0.707 + 0 × 0.707 = -1

结果：矢量在 dq 坐标系中为 (1, -1)
```

### 例2：旋转电流

```
αβ 坐标系：α = A·cos(ωt), β = A·sin(ωt)
电角度：θ_el = ωt
```

计算：
```
i_d = A·cos(ωt)·cos(ωt) + A·sin(ωt)·sin(ωt) = A
i_q = -A·cos(ωt)·sin(ωt) + A·sin(ωt)·cos(ωt) = 0

结果：直流量 (A, 0)
```

**物理意义**：
- αβ 空间中是旋转的交流量
- dq 空间中是恒定的直流量
- 这就是 FOC 的核心思想

---

## 完整变换链

```
三相电流采样 (i_a, i_b, i_c)
    ↓ Clarke 变换
两相静止 (i_α, i_β)
    ↓ Park 变换（θ_el 来自位置传感器）
两相旋转 (i_d, i_q)
    ↓ PI 控制
两相旋转电压 (u_d, u_q)
    ↓ 逆 Park 变换
两相静止电压 (u_α, u_β)
    ↓ 逆 Clarke 变换
三相电压调制 (u_a, u_b, u_c)
    ↓ SVPWM
PWM 输出
```

---

## 与 IPM 电机的控制

对于内嵌式永磁电机 (IPM)，d-q 轴电感不同：

```
L_d ≠ L_q  (L_d < L_q 通常)
```

此时可以利用磁阻转矩：

```
τ = k_t × i_q + (3/2) × (L_d - L_q) × i_d × i_q
    └───────┘   └─────────────磁阻转矩────────┘
      永磁转矩
```

**最大转矩/安比 (MTPA)**：
- 需要 i_d < 0 产生磁阻转矩
- 优化 i_d、i_q 分配
- 提高转矩密度

---

## 常见问题

### Q1: 电角度和机械角度的关系？

**答**：
```
电角度 = 机械角度 × P
其中 P = 极对数

例如：4 极电机，P = 2
机械转一圈 = 电角度转两圈
```

### Q2: Park 变换为什么能将交流变直流？

**答**：
- dq 坐标系随转子旋转
- 旋转速度与磁场旋转速度相同
- 相对运动抵消，变为直流

类比：
- 你在转动的汽车内看其他车（相对静止）
- 人在地球上看太阳（东升西落，相对运动）

### Q3: i_d 和 i_q 的物理意义？

**答**：
- **i_d (direct)**：与转子磁场平行的电流
  - i_d > 0：增磁（增强磁场）
  - i_d = 0：无增磁（最大转矩）
  - i_d < 0：弱磁（减弱磁场，提高转速）

- **i_q (quadrature)**：与转子磁场垂直的电流
  - 直接产生电磁转矩
  - 想象为"推"转子的力

---

## 参考资源

- [SimpleFOC 理论](https://docs.simplefoc.com/foc_theory)
- [TI FOC 培训](https://www.ti.com/)
- [Wikipedia: d–q transformation](https://en.wikipedia.org/wiki/Direct-quadrature-zero_transformation)