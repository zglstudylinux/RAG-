# RAG 真实检索测试结果

> 自动生成，模型：deepseek-v4-pro-0813 + 本地 BGE。

### [芯片规格] AB5766C 的 CPU 是什么架构，主频多少？

AB5766C 的 CPU 为 32 位 RISC-V 处理器核心，主频为 140 MHz [2]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.52
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.13

### [芯片规格] AB5766C 的 Flash 和 RAM 容量分别是多少？

根据资料，AB5766C 的 Flash 容量为 **2Mbit**；RAM 容量为 **64KB + 8K Cache**（合计 72KB RAM）[2][4][1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.12
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.15
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.14
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.15

### [芯片规格] AB5766C 的 2.4G 射频最大发射功率和接收灵敏度是多少？

AB5766C 的 2.4G 射频最大发射功率为 **+11 dBm**，接收灵敏度为 **-92.5 dBm**[1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.5
- [5] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.48

### [芯片规格] AB5766C 的供电电压范围、封装尺寸和工作温度？

根据资料：

- **供电电压范围**：关键参数表给出芯片供电电压为 **2.9~5V** [3]；原理图说明中进一步给出各电源域范围：VUSB 4.5-5.5V，VBAT 2.3-4.5V，VDDIO 2.3-3.6V [1][2]。
- **封装尺寸**：**QFN20 3*3** [3]。
- **工作温度**：**-40~+85°C** [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.15
- [6] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1

### [外设] AB5766C 有哪些 UART 串口？

AB5766C 支持 **2 组普通串口** 和 **1 组高速串口（HUART）**，具体包括：

- **UART0**：作为芯片调试串口使用，波特率为 1.5M [1]
- **UART1**：普通串口，可供用户使用 [1]
- **HUART**：高速串口，建议条件允许时优先使用 [1]

所有串口均支持单线通信能力（时分复用）[1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.42
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [4] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5766_le_mic.h`
- [6] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1

### [外设] AB5766C 的 SAR ADC 分辨率是多少？有几个？触摸按键有几个？

根据资料 [6]，AB5766C 的 SAR ADC 分辨率为 **10-bit**，数量为 **7 个**；硬件电容触摸按键（Touch Key）为 **3 个**。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.25
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.23
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.9
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.22
- [6] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.4

### [驱动API] 如何初始化 AB5766C 的 GPIO？用哪个函数和结构体？

资料中未找到“AB5766C”型号的相关内容；资料针对的是 **AB5766X** SDK。

根据提供的代码资料，GPIO 初始化使用的是函数 **`gpio_init`**，配置结构体为 **`gpio_init_typedef`** [1][3]。

函数原型如下：

```c
void gpio_init(gpio_typedef *gpiox, gpio_init_typedef *gpio_init_struct);
```

调用时需要传入 GPIO 外设（`gpiox`，如 A/B）和配置结构体指针 [1]。

`gpio_init_typedef` 结构体包含以下成员 [3]：

```c
typedef struct {
    uint32_t              gpio_pin;
    GPIO_DIR_TYPEDEF      gpio_dir;
    GPIO_PUPD_TYPEDEF     gpio_pupd;
    GPIO_MODE_TYPEDEF     gpio_mode;
    GPIO_FEN_TYPEDEF      gpio_fen;
    GPIO_FDIR_TYPEDEF     gpio_fdir;
    GPIO_DRV_TYPEDEF      gpio_drv;
} gpio_init_typedef;
```

因此，在 AB5766X SDK 中初始化 GPIO 的基本方式是：填充 `gpio_init_typedef` 结构体，然后调用 `gpio_init()` [1][3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [3] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.15
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.16
- [6] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`

### [驱动API] GPIO 的 CrossBar 功能映射用什么函数配置？

GPIO 的 CrossBar 功能映射使用 `gpio_func_mapping_config` 函数配置 [1][3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.c`
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp_uart_debug.c`
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.40
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.c`
- [6] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`

### [驱动API] GPIO 上拉/下拉电阻有哪些可选阻值？

根据资料，GPIO 内部上拉/下拉电阻的可选阻值典型值为 **0.3KΩ、10KΩ、200KΩ**，精度为 **±20%** [1]。

具体对应关系如下：
- 内部上拉电阻 0 / 内部下拉电阻 0：典型 10KΩ [4]
- 内部上拉电阻 1 / 内部下拉电阻 1：典型 0.3KΩ [4]
- 内部上拉电阻 2 / 内部下拉电阻 2：典型 200KΩ [4]

此外，资料还说明所有 I/O 默认处于高阻状态，内部上拉/下拉电阻精度为 ±20% [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.11
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.22
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.42
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.10
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\libs\cpu\api_smoke.h`
- [6] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.10

### [BSP] BSP 层包含哪些模块？

根据现有资料，BSP 层主要用于存放公共调用的模块，如系统各模块初始化、记忆模块等 [2]。

从代码中的 `bsp.h` 可以看到，BSP 层包含或引用的模块头文件包括：`bsp_param`、`bsp_sys`、`bsp_uart_debug`、`bsp_saradc`、`bsp_saradc_vbat`、`bsp_key`、`bsp_charge`、`bsp_led`、`bsp_sdadc`、`bsp_sddac`、`bsp_huart`、`bsp_le_dut`，以及 `func`、`msg` [4]。

此外，BSP 目录下还存在 `bsp_iis` 模块，提供 `bsp_iis_init`、`bsp_iis_proc` 接口 [5]。

资料中未提供完整的官方 BSP 模块清单，以上是从现有代码和说明中可见的模块。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [4] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp.h`
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp_iis.h`
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.17

### [音频] SDK 里支持哪些音频解码格式？

根据提供的资料，SDK 中涉及的音频解码格式包括：

1. **LC3 编解码**：无线麦方案采用 48K 采样率，使用 LC3 编解码算法 [1]。
2. **WAV 解码**：WAV 解码代码中支持 **PCM** 和 **ADPCM** 两种格式（通过 `WAV_PACKED_FORMAT` 宏配置）[2]。
3. **SBC 编解码**：`api_codec.h` 中定义了 SBC 的采样频率、块、子带、通道模式等枚举，表明涉及 SBC 格式 [5]。

资料中未提及其他音频解码格式。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.47
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\modules\audio\dec\wav_dec.c`
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.11
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\libs\cpu\api_codec.h`
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.58

### [无线] 无线麦克风 wireless mic 相关的处理模块有哪些？

根据资料，SDK modules 目录中与无线麦直接相关的模块是 **`wireless`** 模块，负责“无线麦 2.4G 连接、组包、私有命令等相关模块”[1]。

结合无线麦的产品流程，发射端涉及 ADC 采集、算法处理、编码后发射；接收端涉及接收、解码、算法处理后输出到 DAC 或 USB 上行[4]。这些处理在 modules 目录中可对应以下模块[1]：

- `audio`：存放 DAC 等相关调用接口模块
- `codec`：编解码的基础模式配置
- `voice`：存放降噪、echo、magic 等调用模块

因此，若仅按资料中明确标注为“无线麦相关”的模块，则主要是 **`wireless`** 模块[1]；从无线麦音频处理流程看，还涉及 `audio`、`codec`、`voice` 等模块[1][4]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.26
- [3] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5706a_le_mic.h`
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.46
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5700_kbox.h`
- [6] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5766_le_mic.h`

### [原理图] 领夹MIC 接收端(Receiver)原理图包含哪些主要器件和接口？

根据资料[1]，AB5766C QFN20_3x3 领夹MIC 接收端（Receiver）原理图主要器件和接口包括：

- 主控芯片：AB5766C（QFN20_3x3 封装），说明中提到内置 2MBit Flash [1]
- 晶振：Y1，24MHz，规格为 24M_9pF 或 7.5pF 负载、±10ppm [1]
- LED 指示：绿色 LED（D1 / GREEN_LED）[1]
- 天线：U3，型号 ANT3216080A5T [1]
- 阻容感等外围：C1（105，VDDIO 退耦）、C2、L1（10pF）、L2（TBD）、L3（TBD）、L4（0R）等 [1]
- 升级接口：Xlink 升级工具连接接口，涉及 PB3_uPdate [1]
- 电源/供电接口：VUSB、VBAT、VDDIO [1]
- 晶振接口：OSCO、OSCI [1]

主要接口包括电源、升级、LED 和天线等。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.57
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.55
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5706a_le_mic.h`
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6

### [开发指南] AB5766X SDK 主要支持哪两种产品？

AB5766X SDK 主要支持**领夹麦**和**无线话筒**两种产品 [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.5
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.58
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.67
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2

### [开发指南] AB5766X SDK 使用什么操作系统？

根据资料，AB5766X SDK 使用 **RT-Thread 操作系统**，负责分配系统资源、根据系统实时要求协调任务调度等 [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.12
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.5
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.52
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2

### [开发指南] 编译环境需要哪些工具和版本？

根据资料[1]，编译环境需要以下工具和版本：

- **downloader**：版本需为 downloader_v3.5.1 以上  
- **编译器**：使用 CodeBlock 20.0 版本  
- **编译链**：rv32-toolchain_v1.5.3 版本以上，需要使用 RISCV32-V3 编译  

[1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.11
- [5] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_extra.h`
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.58

### [开发指南] SDK 的 modules 目录下有哪些子模块？

根据资料[2]，SDK 的 `modules` 目录下包含以下子模块：

- **audio**：存放 DAC 等相关调用接口模块
- **codec**：编解码的基础模式配置
- **device**：设备识别防抖的模块
- **effect**：存放 EQ/DRC 的算法接口模块
- **tool**：工具相关的模块
- **voice**：存放降噪、echo、magic 等调用模块
- **wireless**：无线麦 2.4G 连接、组包、私有命令等相关模块

另外，资料[1]提到 `modules` 目录存放的是通用公共模块。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [2] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2
- [4] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.9
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.60
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.2

### [开发指南] SDK 支持的音频编解码格式是什么？

根据提供的资料，SDK 支持的音频编解码格式主要包括：

- **LC3 / LC3S**：资料说明编解码模块“主要是 LC3S 格式”[1]；无线麦方案“采用 LC3 编解码算法”[3]。
- **SBC**：代码中定义了 SBC 的采样率、块、子带、声道模式等参数[2]。
- **WAV（PCM / ADPCM）**：存在 WAV 解码模块，支持 PCM 与 IMA-ADPCM 格式[4]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\libs\cpu\api_codec.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.47
- [4] `D:\Code\AI\RAG_Test\5766\SDK代码\app\modules\audio\dec\wav_dec.c`
- [5] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.58
- [6] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8
