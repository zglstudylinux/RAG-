# RAG 真实检索测试结果

> 自动生成，模型：deepseek-v4-pro-0813 + 本地 BGE。

### [芯片规格] AB5766C 的 CPU 是什么架构，主频多少？

AB5766C 的 CPU 为 **32 位 RISC-V 处理器核心**，主频为 **140MHz** [2]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\wireless\mic_proc.c`
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5

### [芯片规格] AB5766C 的 Flash 和 RAM 容量分别是多少？

根据资料，AB5766C 的 Flash 容量为 **2Mbit** [1][2]。

RAM 容量方面，[1] 中列出为 **64KB + 8K Cache**，合计 72KB；[2] 中描述为 **72KB RAM**。因此可理解为：RAM 为 **64KB + 8K Cache（共 72KB）** [1][2]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [3] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [4] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1

### [芯片规格] AB5766C 的 2.4G 射频最大发射功率和接收灵敏度是多少？

资料中未找到相关内容。[1] 仅说明 AB5766C 集成高性能 2.4GHz RF 收发器，但未提供最大发射功率和接收灵敏度等具体射频指标。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\libs\cpu\api_smoke.h`

### [芯片规格] AB5766C 的供电电压范围、封装尺寸和工作温度？

根据提供的资料：

- **供电电压范围**：VUSB 供电范围 4.5–5.5V，VBAT 2.3–4.5V，VDDIO 2.3–3.6V [1][2]。
- **封装尺寸**：QFN20 3x3（资料中标注为“QFN20_3*3”或“QFN20 3*3”）[1][2][3]。
- **工作温度**：资料中未找到相关内容。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [4] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1

### [外设] AB5766C 有哪些 UART 串口？

资料中未找到 AB5766C 具体 UART 串口列表（如 UART0/UART1 等）的相关内容。  
仅能确认资料中提及以下相关信息：

- UART、HUART 被列为可任意分配功能的 GPIO 功能 [2][4]。
- 调试串口打印可使能并配置在 GPIO PB9，波特率为 1500000 [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5706a_le_mic.h`
- [4] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1

### [外设] AB5766C 的 SAR ADC 分辨率是多少？有几个？触摸按键有几个？

根据资料，AB5766C 的 SAR ADC 分辨率为 **10-bit**，共有 **7 个**；硬件 Cap-sense 触摸按键有 **3 个** [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.4
- [4] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1

### [驱动API] 如何初始化 AB5766C 的 GPIO？用哪个函数和结构体？

资料中未找到初始化 AB5766C GPIO 所需的函数和结构体。

现有资料仅包含：
- GPIO 特性说明，如 PA0、PA1 为高压 IO（耐 5V），其他 IO 为 3.3V GPIO；上下拉配置等 [1]。
- GPIO 索引宏定义，如 `GPIO_PA0`、`GPIO_PB0` 等 [4]。

但未提供 GPIO 初始化函数、初始化结构体或相关调用方式。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\SDK\app\libs\api_alg.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\libs\api_alg.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_define.h`

### [驱动API] GPIO 的 CrossBar 功能映射用什么函数配置？

GPIO 的 CrossBar 功能映射使用 `gpio_func_mapping_config` 函数配置 [1]。

示例：
```c
gpio_func_mapping_config(UART_DEBUG_PORT_SEL, UART_DEBUG_PIN_SEL, GPIO_CROSSBAR_IN_UART0RX);
gpio_func_mapping_config(UART_DEBUG_PORT_SEL, UART_DEBUG_PIN_SEL, GPIO_CROSSBAR_OUT_UART0TX);
```
[1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK\app\bsp\bsp_uart_debug.c`
- [2] `D:\Code\AI\RAG_Test\5766\SDK\app\driver\driver_gpio.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\driver\driver_gpio.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\driver\driver_gpio.h`

### [驱动API] GPIO 上拉/下拉电阻有哪些可选阻值？

根据资料 [2]，GPIO 内部上拉/下拉电阻的可选阻值包括：

- **0.3 kΩ**
- **10 kΩ**
- **200 kΩ**

其中，内部上拉/下拉电阻精度为 **±20%** [2]。  
对于 PA2~PA15、PB0~PB3、PB5~PB8、PG1/2/4/5、PB4 等端口，上拉和下拉均可选 **0.3K/10K/200K** [2]。  
PB9 和 PA0~PA1 的上拉/下拉电阻为 **10 kΩ** [2]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK\app\libs\cpu\api_smoke.h`
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.11
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5766_le_mic.h`
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.10

### [BSP] BSP 层包含哪些模块？

根据提供的资料，BSP 层包含的模块可以从总头文件 `bsp.h` 和 BSP 目录下的源文件看出。

从 [1] 的 `bsp.h` 可以看到，BSP 层包含/聚合了以下模块（头文件）：
- `bsp_param`：参数模块
- `bsp_sys`：系统模块
- `bsp_uart_debug`：UART 调试模块
- `bsp_saradc`：SAR ADC 模块
- `bsp_saradc_vbat`：SAR ADC VBAT 检测模块
- `bsp_key`：按键模块
- `bsp_charge`：充电模块
- `bsp_led`：LED 模块
- `bsp_sdadc`：Sigma-Delta ADC 模块
- `bsp_sddac`：Sigma-Delta DAC 模块
- `bsp_huart`：硬件 UART 模块
- `bsp_le_dut`：LE DUT 模块

同时 `bsp.h` 中还包含了 `func.h`、`msg.h` [1]。

另外，从 [4] 的 `bsp_iis.c` 可以看到，BSP 层还包含 `bsp_iis`（IIS）模块。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK\app\bsp\bsp.h`
- [2] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\audio\mic_eq_drc.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\voice\room_reverb.c`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\bsp\bsp_iis.c`

### [音频] SDK 里支持哪些音频解码格式？

根据提供的资料，SDK 中仅明确支持 **MP3** 音频解码格式 [4]。资料中未找到其他音频解码格式的相关信息。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config.h`
- [2] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5700_kbox.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\wireless\wireless_cmd_api.c`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\audio\dec\mp3_dec.c`

### [无线] 无线麦克风 wireless mic 相关的处理模块有哪些？

资料中未直接列出名为“处理模块”的清单；从现有片段看，无线麦克风涉及以下相关配置/处理功能：

- 无线MIC上行音频配置：采样率、每帧采样点数、声道、压缩帧大小、重传次数、传输周期、支持连接路数等 [1][2][3]
- 编解码处理：编码/解码运算时长，开PLC时解码约900us [1][2][3]
- 发射端SDADC低通滤波 [1][2][3]
- 麦能量检测接口 [1][2][3]
- 音频参数关机保存（echo、magic、soft_gain、mic_mute）[1][2][3]
- 发射端省晶振方案配置 [1][2][3]
- 工作模式：普通、FCC测试、BQB RF BLE测试 [4]
- 蓝牙通知/回调：连接、断开、连接失败、接收数据、虚拟数据/音频链路事件等 [4]
- 特性：FEAT_D2A、FEAT_A2D、FEAT_BONDING [4]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5766_le_mic.h`
- [2] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5706a_le_mic.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\projects\microphone\config_ab5700_kbox.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\libs\ble\api_wireless_mic.h`

### [原理图] 领夹MIC 接收端(Receiver)原理图包含哪些主要器件和接口？

根据 [1]，接收端原理图（AB5766C QFN20_3*3 领夹MIC_Receiver V1.0）包含的主要器件和接口如下：

**主要器件：**

- 主控芯片：AB5766C QFN20_3*3  
- 晶振：Y1，24MHz，规格为 24M_9pF 或 7.5pF 负载_±10ppm，接 OSCO/OSCI  
- 天线：U3，型号 ANT3216080A5T  
- LED：D1，绿色（GREEN），对应网络 GREEN_LED  
- 电源/退耦电容：C1 105 VDDIO、C2 VBAT  
- 其他：L1 10pF、L2 TBD、L3 TBD、L4 0R  
- Flash：SIP 2MBit Flash，说明中写有“内置2MBit Flash”  
- 电源网络：VUSB、VBAT、VDDIO、GND  

**主要接口：**

- Update 升级接口：使用 Xlink 升级工具连接接口，涉及网络 PB3_uPdate  
- POWER 电源接口  
- LED 指示接口  
- 晶振接口：OSCI、OSCO  
- 天线接口  
- VUSB 供电范围 4.5–5.5V，VBAT 2.3–4.5V，VDDIO 2.3–3.6V [1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\audio\mic_eq_drc.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK\app\modules\audio\mic_eq_drc.c`
