# 测试 client 部分

'''
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-09-01 17:39:41
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-09-03 11:43:22
FilePath: /llmada/tests/test_asr.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import requests
import os
from llmada.client import OpenAIClient
import pytest
import asyncio
from llmada.log import Log
logger = Log.logger


def test_client_request():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
    response = client.request(params = params)
    print(response)


async def test_client_arequest():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))
    params = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
    response = await client.arequest(params = params)
    print(response)

async def test_client_arequest_retry_function():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))
    text = """
{
    "system_prompt": "你是一个专业的传记作家和结构规划师AI。你的核心任务是根据用户提供的'人物素材'，创作一个具有深刻人物洞察和叙事张力的'传记大纲'。该大纲需严格遵循用户指定的'三起三伏'叙事节奏，并以人物生命中的'重要时刻'为主要驱动力进行章节规划。**硬性要求：根据提供的素材密度和丰富性，生成一个包含30-50章的章节划分。** 所有输出必须严格符合JSON格式要求，且不可包含任何额外的解释性文本或非JSON内容。",
    "input_material_guidance": {
        "material_nature": "用户提供的素材是关于一个普通人的生平信息，通常以访谈记录、经历片段、关键信息、新增细节等形式呈现。这些素材包含了人物的成长背景、重大事件、个人思想、人际关系、以及特定的哲学思考等。",
        "processing_instructions": [
            "Comprehensive Scan: 全面分析素材，识别所有提及的事件、人物、时间点、思想观点和情感。",
            "Identify Key Moments: 从事件罗列中，提炼出对人物性格、命运、思想产生决定性影响的'重要时刻'。这些时刻可以是外部事件（如学业、职业、创业、合作、危机），也可以是内部觉醒（如思想转变、哲学形成、情感领悟）。",
            "Extract Personality & Philosophy: 挖掘人物独有的性格特征（如'叛逆'、'突破性'、'童心'）和人生哲学（如'没有低谷期'、'解除人类基因锁'），并理解这些特质如何贯穿其生平。",
            "Connect Events to Inner World: 将外部事件与人物的内心成长、思维模式、价值观演变紧密关联起来。每个事件应揭示人物的某个侧面，或推动其成长。",
            "Synthesize & Interpret: 结合不同素材片段，进行综合理解和适当解读，以构建连贯、深入的叙事线索。",
            "**Chapter Allocation based on Material Density:** 根据每个重要事件、经历或思想片段的素材量和重要性，合理分配章节。素材越丰富、越关键，可拆分成更多章节；反之则可合并。确保总章节数在30-50章之间。"
        ]
    },
    "task_parameters": {
        "output_format": {
            "type": "JSON Object",
            "structure_details": {
                "top_level_keys_are_sections": "每个顶级键（Key）代表一个大的'部'（Section），例如 '第一部 童年与性格底色'。部名应简洁且概括该部核心内容。",
                "section_value_is_array_of_chapters": "每个'部'（Key）对应的值（Value）是一个JSON数组，该数组内包含该部所有'章'（Chapter）的JSON对象。",
                "chapter_object_structure": {
                    "chapter_number": "string, e.g., '第一章', '第二章'，确保连续性。",
                    "title": "string, 章节标题，简洁明了，概括本章核心内容。",
                    "topic": "string, 章节核心内容概述。长度适中，包含以下要素：\n  - **叙述视角明确：** 明确标示 '第一人称' 或 '第三人称'。\n  - **内容提炼：** 精炼概括本章将叙述的主要事件或思想片段。\n  - **意义揭示：** 强调该事件/思想对人物性格塑造、观念形成、人生转折的重要性，或其在'三起三伏'节奏中的作用（如 '第一起的核心'、'重要铺垫'、'低谷中的沉淀'）。\n  - **融入人物特色：** 尽可能体现人物的独特语言风格或哲学思考。"
                }
            },
            "strict_compliance": "REQUIRED. No exceptions. No additional prose before or after JSON."
        },
        "narrative_structure": {
            "overall_length_target": "Approx. 80,000 words for the full biography.",
            "chapter_length_target": "Each chapter ~2000 words. 大纲规划需确保此篇幅可实现。",
            "rhythm_model": "Three-Acts-Three-Folds (三起三伏):\n  - **识别'起'：** 指人物事业、思想、影响力达到高峰或实现重大突破的阶段。\n  - **识别'伏'：** 指人物遭遇挑战、经历沉淀、进行内省、或为下一阶段蓄力的时期，并非单纯的失败或低谷，而是带有转机或成长的意味。\n  - 大纲需清晰体现这些'起'和'伏'的交错与递进。",
            "narrative_drivers": [
                "Life-defining 'Important Moments' (关键时刻): 围绕这些时刻展开叙述，并使其他事件为其铺垫或结果。",
                "Character-driven narrative: 故事通过人物的性格、选择和心路历程来推动。",
                "Perspective allocation: Predominantly '第一人称' for internal reflections, philosophical insights, and personal experiences. Sparsely use '第三人称' for external analysis (e.g., from critics, media, or specific collaborators), objective events, or insights into how others perceive the character."
            ],
            "character_emphasis": [
                "Personality bedrock and its evolution (e.g., '叛逆', '突破性', '童心').",
                "Philosophical underpinnings and worldviews (e.g., '没有低谷期', '解除人类基因锁').",
                "Internal conflicts, dilemmas, and their resolutions.",
                "Growth, adaptation, and transformation across different life stages."
            ]
        },
        "response_constraints": [
            "Generate ONLY the requested JSON object. No conversational preambles, explanations, or conclusions.",
            "Ensure precise naming for '部' as JSON keys, e.g., '第一部 童年与性格底色'.",
            "Ensure precise naming for '章' within 'chapter_number' field, e.g., '第一章'."
        ]
    }
}

user:
我想你将章节数量控制在8-12个左右

-----input----

    
### **张三 自传素材整理 (精修版 - 按人物刻画与时间主线梳理)**

**核心人物：张三**
*   **姓名：** 张三
*   **性别：** 男
*   **出生日期：** 1980年
*   **出生地：** 北京 (根据简历，但记忆卡片提及出生于东北辽宁葫芦岛，此处将以记忆卡片为准，简历信息可能为户籍地或后期定居地)
*   **职业：** 某AI公司首席科学家
*   **当前城市：** 未知
*   **人物标签：** 探索者、自然爱好者、求知者、哲思者
*   **核心愿景：** 探索世界本质，追求知识，感受自然之美。

---

### **主要人物刻画与关系网**

*(根据提供的记忆卡片，目前没有具体提及除张三本人之外的其他人物。此部分将留空或在未来有更多信息时补充。)*

---

### **张三 时间主线与探索轨迹**

**人生主线：** 从东北乡村的自然童年到对物理世界的早期探索，张三的人生轨迹展现了对知识和世界本质的持续好奇与追求。

*   **童年时期：乡村的自然与星空 ([1980年代末 - 1990年代初], 辽宁葫芦岛小村庄)**
    *   **背景：** 出生于东北辽宁葫芦岛的一个小村庄。那里的生活简单、规律，人们日出而作，日落而息。自然环境优美，是“山里的野孩子”的乐园。
    *   **塑造/关键事件：**
        *   **自由的童年：** 在山里尽情疯跑，体验无拘无束的乡村生活，培养了对自然的亲近感。
        *   **星空下的启蒙：** 对夜晚的漫天繁星记忆深刻，这份经历可能激发了他对宇宙和未知世界的早期好奇心，为后来对天文物理的兴趣埋下伏笔。

*   **青少年时期：物理世界的初步探索 ([约1995年左右], 县城高中)**
    *   **背景：** 在县城高中读书，学习资源相对有限，重心主要放在学科学习上。
    *   **塑造/关键事件：**
        *   **兴趣萌芽：** 在高中时期，对天文物理和理论物理产生了浓厚的兴趣。尽管资源不足，但这份兴趣显示出他超越日常学习的求知欲和对深层科学原理的向往。

---

**张三 的“觉醒与探索”线索**

*   **自然启蒙：** 乡村的童年生活，尤其是夜晚的星空，是张三最早的觉醒点，激发了他对自然和宇宙的原始好奇心。
*   **知识求索：** 高中时期对天文物理和理论物理的兴趣，标志着他从感性的自然体验转向理性的科学探索，开始主动寻求对世界本质的理解。这份探索精神贯穿其后来的学习和职业生涯。
*   **从具象到抽象：** 从对漫天繁星的直观感受，到对天文物理和理论物理的抽象思考，展现了张三思维深度和广度的发展。

---

### **金句与细节描绘**

#### **🌟 金句摘录**

*   “当时我们都是山里的野孩子，没有什么特别的兴趣爱好，就在山里各种疯跑。”
*   “我小时候特别喜欢晚上看星星，那时的夜晚星星非常多，真的是那种突然就能看到漫天繁星的感觉。”
*   “在我高中的时候，我对天文物理和理论物理就非常感兴趣。”

#### **🎨 优美细节描绘**

*   “我出生在东北辽宁葫芦岛下面的一个小村庄. 小时候，那里的生活比较简单，人们日出而作，日落而息，生活节奏非常有规律，也非常美好。”
*   “那时的夜晚星星非常多，真的是那种突然就能看到漫天繁星的感觉。”    

assistant:
```json
{
    "第一部 童年与自然启蒙": [
        {
            "chapter_number": "第一章",
            "title": "葫芦岛的星光童年",
            "topic": "第三人称。本章将追溯张三在1980年代末至1990年代初，出生于辽宁葫芦岛小村庄的童年岁月。重点描绘乡村的淳朴生活、日出而作日落而息的节奏，以及他作为“山里的野孩子”与自然亲密接触的自由时光。这是张三生命中“第一起”的萌芽，奠定了他与自然连接的性格底色。"
        },
        {
            "chapter_number": "第二章",
            "title": "漫天繁星的召唤",
            "topic": "第一人称。深入探究张三童年时期对夜晚星空的深刻记忆和感受。描述漫天繁星如何在他幼小的心灵中种下对宇宙和未知世界的好奇种子，成为他最早的“觉醒点”，预示其未来对知识的无尽求索。这是他“第一起”中重要的情感与思想铺垫。"
        }
    ],
    "第二部 知识的初步求索": [
        {
            "chapter_number": "第三章",
            "title": "县城高中：物理之门的开启",
            "topic": "第三人称。本章将叙述张三青少年时期在县城高中的学习经历。尽管学习资源相对有限，但张三对天文物理和理论物理产生了浓厚兴趣。这标志着他从感性的自然体验转向理性的科学探索，是其求知欲的进一步展现。这是他“第一起”中知识探索的关键一步。"
        },
        {
            "chapter_number": "第四章",
            "title": "从繁星到理论：思维的跃迁",
            "topic": "第一人称。探讨张三从童年对具象星空的直观感受，到高中时期对抽象天文物理和理论物理的兴趣转变。本章将揭示他思维深度和广度的发展，以及这种从感性到理性的过渡如何塑造了他理解世界的方式。这是他“第一起”中思维方式形成的重要节点。"
        }
    ]
}
```

### 张三 自传素材整理 (精修版 - 按人物刻画与时间主线梳理)

**核心人物：张三**
*   **姓名：** 张三
*   **性别：** 男
*   **出生日期：** 1980年
*   **出生地：** 辽宁葫芦岛小村庄 (根据记忆卡片，修正简历中“北京”为户籍地或后期迁居地，待核实)
*   **职业：** 某AI公司首席科学家
*   **当前城市：** (未提供)
*   **人物标签：** 自然探索者、求知者、哲思者、理论物理爱好者、实践者、**徒步爱好者**
*   **核心愿景：** 探索世界本质，追求知识，从自然中获取灵感，活出规律而美好的生活，**并通过实践拓展人生体验。**

---

### 主要人物刻画与关系网

*(记忆卡片中未提及具体人物，此部分暂无内容。)*

---

### 张三 时间主线与探索轨迹

**人生主线：** 从东北小村庄的自由童年启蒙，到高中时期对深奥物理学的热情探索，再到成年后对徒步等实践活动的投入，张三的人生轨迹贯穿着对自然的好奇、对知识的渴望以及持续的自我发现和体验拓展。

*   **童年与自然启蒙 (约1980年代 - 1995年前，辽宁葫芦岛小村庄)**
    *   **背景：** 出生于东北辽宁葫芦岛的一个小村庄，生活节奏简单、规律而美好，充满田园气息。
    *   **塑造/关键事件：**
        *   作为“山里的野孩子”，在自然中自由奔跑，体验无拘无束的童年，培养了对自然的亲近感。
        *   夜晚仰望“漫天繁星”的经历，是其早期对宇宙、对未知世界产生强烈好奇心和探索欲的萌芽，为其后来的科学兴趣奠定基础。
        *   简单的生活环境塑造了其对规律、美好和本真生活的初步认知。

*   **高中时期与知识探索 (约1995年左右，县城高中)**
    *   **背景：** 在资源相对有限的县城高中就读，学习重心主要集中在学科知识的掌握上。
    *   **塑造/关键事件：**
        *   在有限的学习条件下，对天文物理和理论物理产生了浓厚的兴趣，这显示出其强烈的内在驱动力和超越常规学习范围的求知欲。
        *   尽管环境可能不鼓励多元发展，但其对特定科学领域的专注，预示了其未来在深度探索上的潜力。

*   **成年后的实践与新爱好 (约2005年，云南虎跳峡)**
    *   **背景：** 在某个时间点，张三开始尝试新的实践活动，徒步成为其中一项。
    *   **塑造/关键事件：**
        *   **虎跳峡徒步初体验（2005年）：** 第一次徒步经历，在虎跳峡挑战陡峭的台阶。为了赶车，与朋友一起“猛爬，使劲地爬”，在身体极度疲惫的情况下仍坚持完成。
        *   这次经历不仅考验了其体能和毅力，更重要的是“开启了一个新的项目”，标志着其从纯粹的知识探索向身体力行的实践探索的延伸，丰富了其探索世界的方式。这次经历也展现了其在面对挑战时，目标导向和坚韧不拔的特质。

---

**张三 的“觉醒与探索”线索**

*   **自然作为第一启蒙：** 童年时期在山林间的自由奔跑和对星空的仰望，构成了其最初的“觉醒”，激发了对世界的好奇和探索的欲望。
*   **从感性到理性的飞跃：** 从对自然景象（漫天繁星）的直接感受，到高中时期对抽象的“天文物理和理论物理”的浓厚兴趣，展现了其思维从具象观察向理性、系统性思考的过渡。
*   **内在驱动的求知精神：** 即使在资源受限的高中阶段，其对物理学的热情依然强烈，表明其探索和学习的动力主要源于内在的兴趣和对知识本身的追求。
*   **对生活本质的思考：** 对童年“简单、规律、美好”生活的描述，暗示了其可能在追求高深科学的同时，也在追寻一种与自然和谐共处的生命状态。
*   **实践拓展与毅力展现：** 成年后的虎跳峡徒步，标志着其探索方式的拓展，从书本和理论走向了身体力行的实践。在极度疲惫下依然坚持完成目标，体现了其坚韧不拔的意志力，也揭示了其通过亲身体验来“开启新项目”的探索精神。

---

### 金句与细节描绘

#### 🌟 金句摘录

*   “当时我们都是山里的野孩子，没有什么特别的兴趣爱好，就在山里各种疯跑。”
*   “我小时候特别喜欢晚上看星星，那时的夜晚星星非常多，真的是那种突然就能看到漫天繁星的感觉。”
*   “我们所有的精力都放在学科的学习上。”
*   **“这次徒步对我来说，最大的收获就是开启了一个新的项目。”**

#### 🎨 优美细节描绘

*   “我出生在东北辽宁葫芦岛下面的一个小村庄. 小时候，那里的生活比较简单，人们日出而作，日落而息，生活节奏非常有规律，也非常美好。”
*   “那时的夜晚星星非常多，真的是那种突然就能看到漫天繁星的感觉。”
*   **“下去要一个小时，上来要一个多小时，而且都是很陡的台阶，非常累。”**
*   **“我和我的朋友为了赶上那趟车，就猛爬，使劲地爬。当时我们已经很累了，因为爬楼梯、爬那种台阶很累，但是为了赶上那趟车，我们还是一直在坚持跑。”**

---

### 图片素材备用

*   **出生东北_1:** http://39.96.146.47:8000/11.jpg
*   **高中的时候_1:** http://39.96.146.47:8000/11.jpg
*   **虎跳峡徒步_1:** (待补充，如果后续有图片链接)
"""
    params = {
            "model": "gemini-2.5-pro-preview-06-05",
            "messages": [{"role": "user", "content": text}],
            "temperature": 0.3,
        }
    response = await client.arequest(params = params)
    print(response)

asyncio.run(test_client_arequest_retry_function())

def test_client_request_tts():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "tts-1",
            "input": "你好 世界",
            "voice": "alloy",
            "file_path": 'tests/resources/speech2.mp3',
        }
    response = client.request_tts(data)
    print(response)

async def test_client_arequest_tts():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            "model": "tts-1",
            "input": "你好 世界 天气不错",
            "voice": "alloy",
            "file_path": 'tests/resources/speech.mp3',
        }
    response = await client.arequest_tts(params = params)
    print(response)

def test_client_request_asr():
    # 未通过
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))
    params = {
            "model": "whisper-1",
            "file_path": 'tests/resources/speech2.mp3',
        }
    response = client.request_asr(params = params)
    print(response)



def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
            "stream": True,
        }
    response = client.request_stream(data)
    for i in response:
        print(i)

async def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
            "stream": True,
        }
    response = client.arequest_stream(data)
    async for i in response:
        print(i)


def test_client_request_stream():
    client = OpenAIClient(api_key=os.getenv("BIANXIE_API_KEY"))

    params = {
            'model': 'gemini-2.5-flash-image-preview',
            'messages': [{'role': 'user', 'content': '绘制两个小孩的照片'}],
            "temperature": 0.7,
            'stream': True
        }
    response = client.request_image_stream(params,filename_prefix ="tests/resources/gemini_output" )
    for i in response:
        print(i)

def test_request_modal():
    pass
