# CH03 笔记卡 - vincentzhou

**作者**：vincentzhou  
**提交时间**：2025-11-05 20:16:31

## 非文本如何转换到文本

**非文本转换到文本（Non-text to Text Conversion）**，一般指，非结构化或半结构化的非文本数据（如图像、手写稿、扫描件、音频、视频等）转换为机器可读的文本格式。

但是转换不是目的，更重要的是**理解、提取、组织和利用文档中的信息和知识**。

因此，我们讨论非文本转换时，背后的需求还是文档智能（Document Intelligence, DI），如何自动化处理和理解各种类型的文档（合同、发票、表格、报告、邮件等），从中提取出有价值的数据和洞察。

**常见的文档转换方法整理**

| 格式 (Format) | 文件编码结构 (File Encoding Structure) | 转换核心技术 (Core Conversion Technology) | 方法原理 (Methodology/Principle) | 常见工具 (Common Tools) | 代码工具 (Code/Library Tools) | 处理难点 (Challenges/Difficulties) |
|---|---|---|---|---|---|---|
| **图片 (Image)** | 像素矩阵（位图）。通过编码（如 JPEG 压缩）存储颜色和亮度信息，不含文本编码。 | **OCR** (Optical Character Recognition) + **Layout Analysis** + **智能文档处理 (IDP/文档AI)** | 图像预处理（去噪/增强）→ **版面分析（文本/表格/图像区域分割，基于LayoutLM等模型）** → 字符识别（OCR核心）→ **语言模型后处理（纠错/标点）** → **结构化提取（键值对/表格/实体识别，如Donut模型）**。 | ABBYY FineReader, 夸克扫描王, **Google Document AI**, **Azure AI Document Intelligence**, **Amazon Textract**, 微信/QQ 截图识别 (集成AI增强) | Tesseract (`pytesseract`), **PaddleOCR**, EasyOCR, **LayoutLM (Microsoft)** / **Donut (NAVER)** (深度学习文档理解), 云服务 API (百度/腾讯/阿里/Google Vision + 结构化提取接口) | 低分辨率/复杂背景/艺术字体，**复杂表格（跨页/合并单元格）**，**多语言混排**，手写体/印刷体混用，**印章/水印干扰下的信息提取**，**非标准表单的字段对齐**（如自由格式合同条款）。 |
| **声音 (Audio)** | 数字化的声波采样数据。通过脉冲编码调制 (PCM) 或压缩算法（如 MP3）记录振幅随时间的变化。 | **ASR** (Automatic Speech Recognition) + **说话人分离 (Speaker Diarization)** + **实时转写 (Real-time ASR)** | 声学特征提取（MFCC/Mel频谱）→ 声学模型（如Transformer-based CTC/Attention）→ 语言模型解码（N-gram/Transformer）→ **说话人分离（Diarization，区分多说话人）** → 后处理（标点/分段/口语转书面语）。 | 科大讯飞听见, 飞书妙记, **Google Cloud Speech-to-Text** (带diarization), **Azure Speech Service** (实时转写), 剪映（字幕生成） | **OpenAI Whisper** (多语言/方言支持), Hugging Face Transformers (Wav2Vec2.0/Conformer), `pyannote.audio` (说话人分离), 云服务 API (百度/腾讯/阿里语音识别 + 说话人分离接口) | 背景噪音/口音方言，**多人对话的说话人分离准确性**，**实时转写的低延迟要求**，口语化表达（如"嗯/啊"）清洗，专业术语（如医疗/法律）的领域适配。 |
| **视频 (Video)** | 容器格式，包含视频轨道（编码的图像帧序列）和音频轨道（编码的声波数据）。 | **ASR + OCR + 多模态视频分析 (Multimodal Video Understanding)** | **音频部分:** 分离音频轨道 → ASR转写 + 说话人分离； **视频部分:** 关键帧提取 → OCR识别画面文字 + **视觉理解（物体/场景/行为识别，如YOLO/ViT）**； **整合:** 多模态信息（音频文本+视觉文本+视觉标签）按时间戳对齐 → 生成结构化描述/摘要。 | 网易见外工作台, 剪映/Arctime（字幕）, **AWS Rekognition Video** (视觉+文本融合), **Google Video AI** (多模态分析), YouTube/Bilibili（自动字幕+内容标签） | `FFmpeg` (音视频分离/帧提取) + **OpenAI Whisper** (ASR) + **PaddleOCR** (OCR) + `YOLOv8`/`CLIP` (视觉理解), 云服务 API (百度/腾讯视频内容分析接口) | 音视频同步偏差，**动态文字（滚动/淡入淡出）**，**多模态信息融合一致性**（如语音说"红色"与画面红色物体匹配），**长视频的时序逻辑连贯性**（如会议纪要的议程梳理）。 |
| **PDF (扫描件)** | 本质是图片容器。将扫描页面作为位图或矢量图嵌入，不含可直接提取的文本编码。 | **OCR** + **智能版面恢复 (Intelligent Layout Recovery)** + **表格结构提取 (Table Extraction)** | 图像预处理（去噪/纠偏）→ **版面分析（多栏/图文混排检测，基于空间坐标与语义）** → 字符识别（OCR）→ **表格结构重建（单元格定位/行列关系推断，如TableNet）** → 语言模型后处理（文本纠错/格式还原）。 | Adobe Acrobat Pro, ABBYY FineReader, **Google Document AI** (表格/键值对提取), **Azure AI Document Intelligence** (表单识别), 在线工具 (ilovepdf + AI增强) | Tesseract (`pytesseract`), **PaddleOCR** (表格识别专项模型), **Amazon Textract** (API，表格提取), **LayoutLMv3** (复杂版面理解), `camelot-py`/`tabula-py` (辅助表格提取) | 低分辨率/光照不均，**复杂版面（多栏混排/嵌套表格）**，**手写签名与印刷文字区分**，**跨页表格的连续性识别**，印章/水印覆盖文字的恢复。 |
| **PPT (PowerPoint)** | **PPTX:** 基于 XML 的开放格式（OPC），本质是 ZIP 压缩包。 **PPT:** 二进制私有格式。 | **XML解析/OLE解析 + OCR (图片文字) + 语义层级提取 (Semantic Hierarchy Extraction)** | **文本部分:** 解析XML/OLE结构 → 提取幻灯片标题/正文/备注（保留层级关系，如标题1/标题2/正文）； **非文本部分:** 图片OCR提取文字 + **SmartArt/图表解析（如python-pptx读取图表数据）**； **增强:** NLP实体识别（提取演讲关键词/要点）。 | PowerPoint（另存为大纲）, WPS AI（内容摘要）, **Google Slides** (AI辅助提取), 在线工具 (EaseConvert + 语义提取) | **`python-pptx`** (PPTX文本/图表提取), `Apache POI` (Java), **PaddleOCR** (图片文字), `spaCy`/`HanLP` (NLP实体识别) | 提取备注/演讲者注释的完整性，**SmartArt/流程图的文本结构化**（如层级关系转为列表），**嵌入对象（如Excel表格）的深层数据提取**，保留动画/过渡效果对应的时序信息（如"下一步"提示）。 |
| **Word (DOC/DOCX)** | **DOCX:** 基于 XML 的开放格式（OPC），ZIP 压缩包。 **DOC:** 二进制私有格式。 | **XML解析/OLE解析 + 结构化语义提取 (Structured Semantic Extraction)** | 解析文件结构 → 遍历段落/表格/页眉页脚/文本框 → 提取文本及格式（字体/颜色/加粗，用于区分标题/正文）→ **NLP后处理（实体识别/关系提取/摘要生成，如BERT/LLaMA）**。 | Word/WPS（另存为TXT）, Google Docs（智能摘要）, **Adobe Acrobat** (PDF转换+语义提取), 在线工具 (SmallPDF + AI内容分析) | **`python-docx`** (DOCX文本提取), `textract` (通用解析), `Apache POI` (Java), **`spaCy`/`LangChain`** (NLP语义处理), `pandoc` (格式转换+结构化输出) | 文本框/脚注/尾注的完整提取，**复杂表格的行列关联保留**（如跨页表格的表头重复处理），**修订模式下的原文/修订文区分**，**公式/代码块的格式还原**（如Markdown转换）。 |
| **Excel (XLS/XLSX)** | **XLSX:** 基于 XML 的开放格式（OPC），ZIP 压缩包。 **XLS:** 二进制私有格式。 | **XML解析/OLE解析 + 数据类型推断 (Data Type Inference) + 异常检测 (Anomaly Detection)** | 解析文件结构 → 定位工作表/单元格 → 读取单元格值及公式（区分显示值与计算值）→ **数据类型推断（日期/数字/文本分类）** → **异常检测（如错误值/离群值标记，基于规则或ML模型）**。 | Excel/WPS（另存为CSV）, Google Sheets（数据清洗）, **Power Query** (Excel内置，数据提取+转换), 在线工具 (Convertio + 数据校验) | **`pandas`** (数据读取/清洗), **`openpyxl`** (XLSX读写), `xlrd` (XLS读取), `PyOD` (异常检测), `great_expectations` (数据校验规则) | **合并单元格的展开逻辑**（如多行合并的表头对应关系），**隐藏行列的数据完整性**（提取时是否包含隐藏内容），**公式依赖链的追溯**（如提取"=A1+B1"的实际计算逻辑），**大数据量文件的内存效率**（如100万行表格的分块处理）。 |

