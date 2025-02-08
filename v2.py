# 1. 首先安装必要的依赖
!pip install edge-tts moviepy rembg opencv-contrib-python onnxruntime
!pip install librosa==0.9.1
!pip install face-alignment==1.3.5

# 2. 克隆 Wav2Lip 仓库并下载模型
!git clone https://github.com/Rudrabha/Wav2Lip.git
%cd /content/Wav2Lip
!mkdir -p checkpoints
!wget "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA" -O checkpoints/wav2lip.pth

# 3. 导入所需库
import os
import sys
import numpy as np
import cv2
from datetime import datetime
import edge_tts
import asyncio
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import io
from PIL import Image, ImageFilter
import numpy as np

texts = [
    "家人们谁懂啊！130多年了，轰动世界的悬案《开膛手杰克》的真凶身份终于有线索了！",
    
    "在犯罪史上，'开膛手杰克'的名号那可是让人听了就害怕。",
    
    "这位19世纪末的连环杀手，在伦敦干了一系列血腥残忍的案子。他到底是谁，这谜团困扰了大家130多年。",
    
    "好在现在随着DNA技术的突飞猛进，案件侦破终于有了大进展。",
    
    "1888年8月7日，伦敦东区白教堂附近发生了第一起案件。一名底层女子身中39刀，现场惨不忍睹。",
    
    "8月31日凌晨，又一名女子的尸体被发现。她颈部遭切割，腹部被剖开，场景令人毛骨悚然。",
    
    "9月8日清晨，第三名女子遇害。她的喉咙被割开，部分器官被割走，周围墙壁溅满了血迹。",
    
    "9月27日，通讯社收到一封用红墨水写的挑衅信。凶手自称'杰克'，扬言要继续作案，'开膛手杰克'的恶名就此传开。",
    
    "9月30日凌晨短短一小时内，两名女子接连遇害。隔天，通讯社又收到开膛手杰克的信，不仅预告了这两起案件，还嘲讽警方。",
    
    "10月15日更骇人的是，通讯社收到了遇害者的半颗肾脏，包裹上还有着诡异的字迹。",
    
    "11月9日，最后一位受害者被发现。此后，开膛手杰克销声匿迹，警方始终未能抓到凶手。",
    
    "2007年，研究员拉塞尔在拍卖会上购得一条血迹斑斑的披肩，据称是在受害者凯瑟琳的尸体上发现的。",
    
    "研究人员将披肩上的DNA与受害者后人进行匹配，结果显示匹配率高达99.2%。",
    
    "更重要的是，披肩上还发现了疑似凶手的DNA，与一名叫柯斯米斯基的男子的后代相匹配。",
    
    "柯斯米斯基1865年出生在波兰的一个犹太家庭，1881年因躲避迫害，一家人移民到了伦敦东区。",
    
    "在伦敦，柯斯米斯基跟着父亲学习裁缝手艺。但长期压抑的工作环境，让他的精神状态逐渐恶化。",
    
    "从1885年开始，他就有精神病症状，多次被送入精神病院。他常常独自在街头游荡，行为怪异。",
    
    "1891年，他的病情急剧恶化，再次被送入精神病院。最终在1919年在医院去世。",
    
    "除了DNA证据，他的笔记与杰克写给媒体的信件字迹也极其相似。",
    
    "目前，受害者和嫌疑人的后代都支持重启调查。但要正式立案，还需要获得司法大臣的许可。",
    
    "这个困扰了一个多世纪的悬案，终于有了突破。我们或许能见证'开膛手杰克'这个世纪谜案的最终告破。"
]

async def create_digital_human_video_simple(face_path, texts, output_path):
    """创建简单的数字人视频，视频大小根据输入人物图片大小自适应"""
    clips_to_close = []
    try:
        # 设置工作目录和路径
        project_path = os.path.dirname(output_path)
        os.makedirs(project_path, exist_ok=True)

        # 首先读取输入图片的尺寸
        print("正在分析输入图片...")
        input_image = Image.open(face_path)
        original_width, original_height = input_image.size
        print(f"输入图片尺寸: {original_width}x{original_height}")

        # 计算视频尺寸（保持原始宽高比）
        # 如果图片太大或太小，我们设置一个合理的范围
        MIN_HEIGHT = 480
        MAX_HEIGHT = 1080

        if original_height < MIN_HEIGHT:
            scale = MIN_HEIGHT / original_height
        elif original_height > MAX_HEIGHT:
            scale = MAX_HEIGHT / original_height
        else:
            scale = 1.0

        target_height = int(original_height * scale)
        target_width = int(original_width * scale)

        # 为字幕预留空间
        canvas_height = int(target_height * 1.2)  # 增加20%的高度用于字幕
        canvas_width = target_width

        print(f"最终视频尺寸: {canvas_width}x{canvas_height}")

        # 定义所需的路径
        audio_path = os.path.join(project_path, "output_audio.wav")
        lip_sync_path = os.path.join(project_path, "lip_sync_output.mp4")

        # 1. 生成音频
        print("\nStep 1: 生成音频")
        combined_text = " ".join(texts)
        if not await generate_audio(combined_text, audio_path):
            raise Exception("音频生成失败")

        # 2. 进行口型同步
        print("\nStep 2: 进行口型同步")
        if not run_wav2lip(face_path, audio_path, lip_sync_path):
            raise Exception("口型同步失败")

        # 3. 添加字幕
        print("\nStep 3: 添加字幕")
        try:
            # 加载口型同步视频
            print("正在加载视频...")
            video_clip = VideoFileClip(lip_sync_path)
            clips_to_close.append(video_clip)

            # 调整视频大小
            print("正在调整视频大小...")
            video_clip = video_clip.resize(width=target_width, height=target_height)

            # 设置视频位置（垂直居中）
            video_y_position = (canvas_height - target_height) // 2
            video_clip = video_clip.set_position(('center', video_y_position))

            # 创建字幕（自适应大小）
            print("正在创建字幕...")
            subtitle_clips = []
            duration_per_text = video_clip.duration / len(texts)

            # 计算适合的字体大小（基于视频宽度）
            font_size = int(canvas_width * 0.045)  # 字体大小为视频宽度的4.5%
            print(f"字体大小: {font_size}")

            def create_adaptive_text_frame(text, size=(canvas_width, canvas_height),
                                        font_path='/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'):
                """创建自适应大小的字幕帧"""
                img = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)

                # 分割文本行
                lines = text.split('\n')
                if len(lines) > 2:
                    lines = lines[:2]

                # 使用计算好的字体大小
                font = ImageFont.truetype(font_path, font_size)

                # 计算字幕位置（底部，留出一定边距）
                bottom_margin = int(canvas_height * 0.05)  # 底部留5%的边距
                y_position = canvas_height - bottom_margin - (len(lines) * font_size * 1.5)

                # 绘制每行文本
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (size[0] - text_width) // 2

                    # 绘制描边
                    outline_color = 'black'
                    outline_width = max(1, int(font_size * 0.05))  # 描边宽度与字体大小成比例
                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            draw.text((x + dx, y_position + dy), line, font=font, fill=outline_color)

                    # 绘制主文本
                    draw.text((x, y_position), line, font=font, fill='white')
                    y_position += int(font_size * 1.5)  # 行间距为字体大小的1.5倍

                return np.array(img)

            for i, text in enumerate(texts):
                frame = create_adaptive_text_frame(text)
                clip = ImageClip(frame, transparent=True).set_duration(duration_per_text)
                clip = clip.set_start(i * duration_per_text)
                subtitle_clips.append(clip)
                clips_to_close.append(clip)

            # 合成视频
            print("正在合成视频...")
            final_video = CompositeVideoClip(
                [video_clip] + subtitle_clips,
                size=(canvas_width, canvas_height)
            )
            clips_to_close.append(final_video)

            # 添加音频
            print("正在添加音频...")
            audio_clip = AudioFileClip(audio_path)
            clips_to_close.append(audio_clip)
            final_video = final_video.set_audio(audio_clip)

            # 导出视频
            print("正在导出视频...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            print("\n视频生成完成！")

            return True

        except Exception as e:
            print(f"视频处理过程中出错：{str(e)}")
            import traceback
            print("详细错误信息：")
            print(traceback.format_exc())
            return False

    except Exception as e:
        print(f"生成视频时出错：{str(e)}")
        import traceback
        print("详细错误信息：")
        print(traceback.format_exc())
        return False

    finally:
        # 清理资源
        print("正在清理资源...")
        for clip in clips_to_close:
            try:
                clip.close()
            except:
                pass
async def test_pipeline_simple():
    project_path = '/content/drive/MyDrive/digital_human_project'
    os.makedirs(project_path, exist_ok=True)
    
    face_path = os.path.join(project_path, "11.jpg")
    output_path = os.path.join(project_path, "final_video.mp4")
    
    print(f"开始测试 - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"使用的文件路径：")
    print(f"人物图片：{face_path}")
    print(f"输出视频：{output_path}")
    
    # 检查输入文件
    if not os.path.exists(face_path):
        print(f"错误：找不到人物图片 {face_path}")
        return
    
    result = await create_digital_human_video_simple(face_path, texts, output_path)
    
    if result:
        print("视频生成成功！")
        from IPython.display import HTML
        from base64 import b64encode
        
        video_file = open(output_path, "rb").read()
        video_url = f"data:video/mp4;base64,{b64encode(video_file).decode()}"
        display(HTML(f"""
        <video width="640" height="360" controls>
            <source src="{video_url}" type="video/mp4">
        </video>
        """))
    else:
        print("视频生成失败！")

# 运行测试
await test_pipeline_simple() 
