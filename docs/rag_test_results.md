# RAG 真实检索测试结果

> 自动生成，模型：deepseek-v4-pro-0813 + 本地 BGE。

### [芯片规格] AB5766C 的 CPU 是什么架构，主频多少？

根据资料 [1]，AB5766C 的 CPU 为 **32 位 RISC-V 处理器核心**，主频为 **140 MHz** [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6

### [芯片规格] AB5766C 的 Flash 和 RAM 容量分别是多少？

根据资料，AB5766C 的 Flash 容量为 **2Mbit**，RAM 容量为 **64KB + 8K Cache**（总计 72KB）[2][3][1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.12
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6

### [芯片规格] AB5766C 的 2.4G 射频最大发射功率和接收灵敏度是多少？

AB5766C 的 2.4G 射频最大发射功率为 **+11 dBm**，接收灵敏度为 **-92.5 dBm** [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5

### [芯片规格] AB5766C 的供电电压范围、封装尺寸和工作温度？

根据资料：

- **供电电压范围**：芯片整体供电电压为 **2.9~5V** [3][4]。原理图说明中进一步列出各电源域范围：**VUSB 4.5-5.5V，VBAT 2.3-4.5V，VDDIO 2.3-3.6V** [1][2]。
- **封装尺寸**：**QFN20 3*3** [3]，原理图标题也显示为 QFN20 3*3 封装 [1][2]。
- **工作温度**：**-40~+85°C** [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1
- [2] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3 领夹MIC_Transmitter V1.0.pdf` p.1
- [3] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.5
- [4] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.6

### [外设] AB5766C 有哪些 UART 串口？

根据资料 [1]，AB5766C 支持 **2 组普通串口** 和 **1 组高速串口（HUART）**，并且所有串口均支持单线通信能力（时分复用）。其中：

- **UART0**：作为芯片调试串口使用，波特率 1.5M；
- **UART1**：用户可使用；
- **HUART**：高速串口，用户可使用，建议条件允许时优先使用 [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.42

### [外设] AB5766C 的 SAR ADC 分辨率是多少？有几个？触摸按键有几个？

根据资料[1]，AB5766C 的 SAR ADC 分辨率为 **10-bit**，共有 **7 个**；硬件触摸按键（Cap-sense Touch Key）有 **3 个** [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.4

### [驱动API] 如何初始化 AB5766C 的 GPIO？用哪个函数和结构体？

根据提供的资料，初始化 GPIO 应使用 `gpio_init` 函数，并配合 `gpio_init_typedef` 结构体进行配置 [1][2]。

- **函数原型**：`void gpio_init(gpio_typedef *gpiox, gpio_init_typedef *gpio_init_struct);` [1]
  - `gpiox`：选择 GPIO 外设，可以为 A 或 B [1]。
  - `gpio_init_struct`：指向 `gpio_init_typedef` 结构体的指针，包含 GPIO 的配置信息 [1]。

- **结构体 `gpio_init_typedef`** 包含以下成员 [2]：
  - `uint32_t gpio_pin`
  - `GPIO_DIR_TYPEDEF gpio_dir`
  - `GPIO_PUPD_TYPEDEF gpio_pupd`
  - `GPIO_MODE_TYPEDEF gpio_mode`
  - `GPIO_FEN_TYPEDEF gpio_fen`
  - `GPIO_FDIR_TYPEDEF gpio_fdir`
  - `GPIO_DRV_TYPEDEF gpio_drv`

使用时需要先填充 `gpio_init_typedef` 结构体，然后调用 `gpio_init` 完成初始化 [1][2]。资料中未提供完整的初始化示例代码，也未明确提及 AB5766C 型号的差异。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.h`

### [驱动API] GPIO 的 CrossBar 功能映射用什么函数配置？

GPIO 的 CrossBar 功能映射使用 `gpio_func_mapping_config` 函数配置 [1][2]。

例如在 UART 调试初始化中调用：
```c
gpio_func_mapping_config(UART_DEBUG_PORT_SEL, UART_DEBUG_PIN_SEL, GPIO_CROSSBAR_IN_UART0RX);
gpio_func_mapping_config(UART_DEBUG_PORT_SEL, UART_DEBUG_PIN_SEL, GPIO_CROSSBAR_OUT_UART0TX);
```
[2]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK代码\app\driver\driver_gpio.c`
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp_uart_debug.c`

### [驱动API] GPIO 上拉/下拉电阻有哪些可选阻值？

根据提供的资料，GPIO 内部上拉/下拉电阻的可选阻值（典型值）为 **0.3 KΩ、10 KΩ、200 KΩ**，精度为 **±20%** [1][2]。

具体对应关系如下：

- **0.3 KΩ**：内部上拉/下拉电阻 1（RPUP1/RPDN1），实际范围 0.24 ~ 0.36 KΩ [2]。
- **10 KΩ**：内部上拉/下拉电阻 0（RPUP0/RPDN0），实际范围 8 ~ 12 KΩ [2]。
- **200 KΩ**：内部上拉/下拉电阻 2（RPUP2/RPDN2），实际范围 160 ~ 240 KΩ [2]。

另外，对于部分 GPIO（如 PB9、PA0~PA1），其内部上拉/下拉电阻固定为 **10 KΩ** [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.11
- [2] `D:\Code\AI\RAG_Test\5766\datasheet\ab5766c_datasheet_v0.0.4.pdf` p.10

### [BSP] BSP 层包含哪些模块？

根据资料，BSP 层/目录的相关信息如下：

- SDK 目录结构中，`bsp` 目录“主要是存放公共调用的模块，如系统各个模块的初始化，记忆模块等”[1]。
- 从 `bsp.h` 中包含的头文件来看，BSP 层涉及/包含：`bsp_param`、`bsp_sys`、`bsp_uart_debug`、`bsp_saradc`、`bsp_saradc_vbat`、`bsp_key`、`bsp_charge`、`bsp_led`、`bsp_sdadc`、`bsp_sddac`、`bsp_huart`、`bsp_le_dut`，另外还包含 `func.h`、`msg.h` [2]。
- BSP 代码目录下还有 `bsp_iis.h`，提供 `bsp_iis_init`、`bsp_iis_proc` 接口，说明 IIS 相关接口也位于 BSP 层代码中 [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.7
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK代码\app\bsp\bsp_iis.h`

### [音频] SDK 里支持哪些音频解码格式？

根据提供的资料，SDK 中涉及的音频解码格式包括：

- **LC3**：无线麦使用 48K 采样率，采用 LC3 编解码算法，接收端音频链路中有 MIC_DEC（解码）环节 [1]。
- **WAV（PCM/ADPCM）**：`wav_dec.c` 中支持 WAV 解码，`WAV_PACKED_FORMAT` 可配置为 0（PCM）或 1（ADPCM）[2]。
- **SBC**：`api_codec.h` 中定义了 SBC 的采样频率、块大小、子带数、声道模式等枚举，表明 SDK 提供 SBC 编解码相关接口 [3]。

因此，资料中可确认支持的音频解码格式为 LC3、WAV（PCM/ADPCM）和 SBC。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.47
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\modules\audio\dec\wav_dec.c`
- [3] `D:\Code\AI\RAG_Test\5766\SDK代码\app\libs\cpu\api_codec.h`

### [无线] 无线麦克风 wireless mic 相关的处理模块有哪些？

在 SDK 的 modules 目录中，无线麦克风（wireless mic）相关的处理模块包括：

- **wireless**：无线麦 2.4G 连接、组包、私有命令等相关模块 [1]
- **voice**：降噪、echo、magic 等调用模块 [1]
- **effect**：EQ/DRC 的算法接口模块 [1]
- **codec**：编解码的基础模式配置 [1]
- **audio**：DAC 等相关调用接口模块 [1]
- **device**：设备识别防抖的模块 [1]

此外，配置文件中还包含无线 mic 功能选择配置，如编解码选择、传输机制版本、工作频段、组队绑定、RSSI 阈值、连接 ID、配对模式等 [2][4]。无线麦产品形态分为发射端和接收端两个角色，分别涉及 ADC 采集、编码发射和接收解码、DAC/USB 输出等处理 [3]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5706a_le_mic.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.46
- [4] `D:\Code\AI\RAG_Test\5766\SDK代码\app\projects\microphone\config_ab5700_kbox.h`

### [原理图] 领夹MIC 接收端(Receiver)原理图包含哪些主要器件和接口？

根据接收端原理图 [1]，AB5766C 领夹MIC Receiver 的主要器件和接口包括：

- **主控芯片**：AB5766C QFN20 3×3 封装 [1]
- **晶振**：24MHz 晶振 Y1，规格为 24M_9pF 或 7.5pF 负载、±10ppm [1]
- **天线**：U3 ANT3216080A5T，及相关电感/电阻 L3、L4（0R）等 [1]
- **Flash**：标注 SIP 2MBit Flash；说明中也写明内置 2MBit Flash [1]
- **LED 指示**：D1 GREEN、GREEN_LED [1]
- **电源接口/电源网络**：VUSB、VBAT、VDDIO，及退耦电容 C1、C2 等 [1]
- **升级/调试接口**：Xlink 升级工具连接接口，PB3_uPdate [1]
- **其他无源器件**：L1 10pF、L2 TBD、OSCO/OSCI 晶振接口等 [1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\sch\AB5766C+AB5766C_领夹MIC Schematic V1.0\AB5766C QFN20_3x3  领夹MIC_Receiver V1.0.pdf` p.1

### [开发指南] AB5766X SDK 主要支持哪两种产品？

根据资料片段[1]，AB5766X SDK 主要支持两种产品：**领夹麦**和**无线话筒**。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.5

### [开发指南] AB5766X SDK 使用什么操作系统？

AB5766X SDK 使用 **RT-Thread 操作系统**，负责分配系统资源、根据系统实时要求协调任务调度等 [1]。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6

### [开发指南] 编译环境需要哪些工具和版本？

根据资料 [1]，编译环境需要以下工具和版本：

- **downloader**：downloader_v3.5.1 以上  
- **编译器**：codeblock 20.0 版本  
- **编译链**：rv32-toolchain_v1.5.3 版本以上，需要使用 RISCV32-V3 编译 [1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6

### [开发指南] SDK 的 modules 目录下有哪些子模块？

根据资料 [1]，SDK 的 `modules` 目录下包含以下子模块：

- `audio`：存放 dac 等相关调用接口模块
- `codec`：编解码的基础模式配置
- `device`：设备识别防抖的模块
- `effect`：存放 eq/drc 的算法接口模块
- `tool`：工具相关的模块
- `voice`：存放降噪、echo、magic 等调用模块
- `wireless`：无线麦 2.4G 连接、组包、私有命令等相关模块 [1]

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.8

### [开发指南] SDK 支持的音频编解码格式是什么？

SDK 支持的音频编解码格式如下：

- **主要音频编解码格式为 LC3/LC3S**：  
  功能模块层的编解码模块“主要是音频格式编解码相关，主要是 LC3S 格式”[1]；无线麦方案“采样率是 48K，采用 LC3 编解码算法”[3]。

- **代码中还涉及 WAV 与 SBC 相关接口/定义**：  
  `api_codec.h` 中声明了 `wav_res_analize`，并定义了 SBC 的采样率、块、子带、声道模式等枚举[2]；`wav_dec.c` 中支持 WAV 解码，可处理 PCM 或 ADPCM 格式（由 `WAV_PACKED_FORMAT` 配置）[4]。

因此，从提供的资料来看，SDK 主要音频编解码格式为 **LC3/LC3S**，同时代码中也包含 **WAV、SBC** 相关编解码支持。

**引用来源：**
- [1] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.6
- [2] `D:\Code\AI\RAG_Test\5766\SDK代码\app\libs\cpu\api_codec.h`
- [3] `D:\Code\AI\RAG_Test\5766\SDK开发指南\ab5766xSDK开发指南_v1.0.0.pdf` p.47
- [4] `D:\Code\AI\RAG_Test\5766\SDK代码\app\modules\audio\dec\wav_dec.c`
