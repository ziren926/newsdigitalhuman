# 1. 首先安装必要的依赖
!pip install edge-tts moviepy rembg opencv-contrib-python onnxruntime
!pip install librosa==0.9.1
!pip install face-alignment==1.3.5

# 2. 克隆 Wav2Lip 仓库并下载模型
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
import subprocess

texts = [
    "惊悚对撞！华盛顿上空的致命悲剧",

    "你能想象吗？在繁华都市的上空，两架飞行器竟以一种惨烈的方式相遇，瞬间打破了所有的平静与安宁。美东时间1月29日晚，这样的噩梦在美国真实上演。",

    "当晚，美国太平洋西南航空的庞巴迪CRJ700支线喷气式客机AA5342航班，从堪萨斯州威奇托起飞，机上载着64名乘客和机组人员，正朝着华盛顿里根国家机场飞去，满心期待着平安抵达目的地。",

    "里根机场共有3条跑道，其中1/19跑道压力最大，承担着超90%的起降任务 。起初，空管确认AA5342航班可降落在最长的1/19跑道，但3分钟后却要求改为降落15/33跑道。机组考虑到飞机当时由东南向西北飞行，有条件修改跑道，便同意了这一变更。",

    "与此同时，一架隶属于美国陆军第12航空营的“黑鹰”直升机，正载着三名经验丰富、配备夜视镜的军人执行“政府连续计划”任务训练。这架直升机从西北方向而来，向东南方向飞行，当时正处于机场附近空域。",

    "约晚上8点47分，空管人员察觉到了潜在的危险，他一边指挥着客机降落，一边询问“黑鹰”直升机（代号PAT - 25）机组能否目视到AA5342航班。",

    "直升机机组回复可以看到，空管便要求直升机从航班的“后方通过”，意思大概率是让直升机从右侧绕行，避开航班轨迹。可仅仅25秒后，悲剧毫无征兆地发生了。",

    "据美国国家运输安全委员会（NTSB）调查，碰撞发生时，“黑鹰”直升机位于300英尺（约91米）高处，而客机高度约为325英尺（约99米）。",

    "但诡异的是，当时空管员看到雷达显示直升机高度仅为200英尺（约61米）。从ADS - B Exchange网站记录的飞行轨迹图像来看，航班完全处于正常降落状态，高度变化也符合规定，只是在相撞前很短一段时间内，有一个疑似抬升机头的动作，似乎是机组发现了危险。",

    "初步调查排除了航班防撞系统（TCAS）因检测到异常物体进入危险距离而报警的可能性，因为TCAS系统在飞机低于700英尺（213米）时基本不再起作用，这个高度下飞行物太多，容易误报警。",

    "从社交媒体传播的视频中可以看到，客机在降落过程中，直升机从后方撞上客机，两机瞬间在夜空中爆炸成巨大火球，随后坠入冰冷的波托马克河。",

    "飞机坠河后，水中的残骸显示，客机机腹朝上，断成了三截。",

    "事故发生后，整个美国都被震惊了。总统特朗普次日在新闻发布会上沉痛宣布，这场事故无人生还。",

    "救援人员迅速展开行动，争分夺秒地在冰冷的河水中搜寻幸存者和遇难者遗体。",

    "当地时间2月4日，67名遇难者的遗体全部被找到，两天后，所有遇难者身份确认完毕，其中包括2名中国公民以及俄罗斯花样滑冰世界冠军夫妇叶夫根尼娅·希什科娃、瓦季姆·瑙莫夫 ，让这场悲剧的影响扩散到了世界各地。",

    "调查工作也在紧锣密鼓地进行。2月1日，客机的两个黑匣子数据成功下载，“黑鹰”直升机的黑匣子随后也被找到。",

    "随着调查的深入，越来越多的细节浮出水面。4日，美国国家运输安全委员会透露，空中交通管制显示屏数据显示，碰撞时“黑鹰”直升机位于300英尺（约91米）高处，客机高度约为325英尺（约99米），而当时空管员看到雷达显示直升机高度仅为200英尺（约61米），这一数据差异令人费解。",

    "6日，又有惊人消息传出，美国参议院商务、科学和运输委员会主席克鲁兹表示，事故发生前，“黑鹰”直升机在训练任务期间关闭了广播式自动相关监视（ADS - B）关键追踪技术，这无疑让事故的原因更加扑朔迷离。",

    "8日，美国国家运输安全委员会宣布，失事客机和直升机的所有主要残骸都已找到，后续将进行更细致的检查，试图揭开这场悲剧背后的真相。",

    "事故发生后，美国联邦航空局立即对华盛顿里根国家机场附近直升机飞行实施无限期限制，除警用和医疗直升机外，大多数直升机禁止飞越机场附近指定区域。",

    "美国航空公司也取消了原AA5342航班编号，当晚从威奇托飞往华盛顿特区的航班恢复运营，新航班编号变更为AA5677，但这一切都无法挽回那67条鲜活的生命。",

    "这场华盛顿上空的致命悲剧，给无数家庭带来了沉重的打击，也为全球航空安全敲响了警钟，人们都在等待着最终的调查结果，希望能给逝者一个交代，给生者一个答案。"
]

def get_current_info():
    """获取当前时间和用户信息"""
    current_time = datetime.utcnow()
    time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    user = os.getenv('USERNAME', 'ziren926')
    return time_str, user, current_time

async def generate_audio(text, project_path, voice="zh-CN-YunxiNeural"):
    try:
        os.makedirs(project_path, exist_ok=True)
        mp3_path = os.path.abspath(os.path.join(project_path, "output.mp3"))
        wav_path = os.path.abspath(os.path.join(project_path, "output_audio.wav"))

        time_str, user, _ = get_current_info()
        print(f"Current Date and Time (UTC): {time_str}")
        print(f"Current User's Login: {user}")
        print(f"正在使用 {voice} 生成音频...")
        print(f"MP3输出路径: {mp3_path}")
        print(f"WAV输出路径: {wav_path}")

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(mp3_path)
        print("MP3文件生成成功")

        audio = AudioFileClip(mp3_path)
        audio.write_audiofile(wav_path, codec='pcm_s16le')
        print("已转换为WAV格式")

        return True
    except Exception as e:
        print(f"音频生成失败：{str(e)}")
        print(f"当前工作目录: {os.getcwd()}")
        return False

def generate_subtitles(texts, duration_per_text):
    subtitles = []
    start_time = 0
    for text in texts:
        end_time = start_time + duration_per_text
        subtitles.append(((start_time, end_time), text))
        start_time = end_time
    return subtitles

def generate_face_video(image_path, audio_duration, output_path="face_video.mp4", fps=24):
    print(f"Generating face video for duration: {audio_duration} seconds")
    image_clip = ImageClip(image_path, duration=audio_duration)
    image_clip = image_clip.set_fps(fps)
    image_clip.write_videofile(output_path, fps=fps, codec="libx264")

def run_wav2lip(face_path, audio_path, output_path):
    """运行 Wav2Lip 进行口型同步"""
    try:
        print("开始进行口型同步...")
        
        # 下载 Wav2Lip 模型（如果尚未下载）
        model_path = '/content/drive/MyDrive/digital_human_project/checkpoints/wav2lip.pth'
        if not os.path.exists(model_path):
            print("正在下载 Wav2Lip 模型...")
            os.system("wget -O {model_path} https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth")
        
        # 克隆 Wav2Lip 仓库（如果尚未克隆）
        if not os.path.exists('/content/Wav2Lip'):
            os.system("git clone https://github.com/Rudrabha/Wav2Lip.git /content/Wav2Lip")
        
        # 运行 Wav2Lip
        cmd = f"""cd /content/Wav2Lip && python inference.py \
            --checkpoint_path {model_path} \
            --face {face_path} \
            --audio {audio_path} \
            --outfile {output_path} \
            --nosmooth"""
        
        os.system(cmd)
        
        if os.path.exists(output_path):
            print("口型同步完成！")
            return True
        else:
            print("口型同步失败：未生成输出文件")
            return False
            
    except Exception as e:
        print(f"口型同步时出错：{str(e)}")
        return False

def remove_background(image_path, output_path):
    try:
        print(f"Removing background for image: {image_path}")
        with open(image_path, "rb") as input_file:
            input_data = input_file.read()
        output_data = remove(input_data)
        with open(output_path, "wb") as output_file:
            output_file.write(output_data)
        print(f"背景移除完成，输出路径: {output_path}")
        return True
    except Exception as e:
        print(f"背景移除失败：{str(e)}")
        return False

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
        if not await generate_audio(combined_text, project_path):
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

            # 创建字幕
            print("正在创建字幕...")
            subtitle_clips = []
            duration_per_text = video_clip.duration / len(texts)

            # 计算适合的字体大小（基于视频宽度）
            font_size = int(canvas_width * 0.045)  # 字体大小为视频宽度的4.5%
            print(f"字体大小: {font_size}")

            def setup_font():
                """设置和安装字体"""
                try:
                    # 首先检查系统中是否已经安装了字体
                    possible_font_paths = [
                        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'
                    ]

                    for path in possible_font_paths:
                        if os.path.exists(path):
                            return path

                    # 如果没有找到字体，安装字体
                    print("正在安装字体...")
                    os.system('apt-get update -qq && apt-get install -qq -y fonts-noto-cjk')

                    # 再次检查字体是否安装成功
                    for path in possible_font_paths:
                        if os.path.exists(path):
                            return path

                    # 如果还是没有找到，下载并使用临时字体
                    print("正在下载临时字体...")
                    from urllib.request import urlretrieve
                    import tempfile

                    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
                    temp_dir = tempfile.gettempdir()
                    temp_font_path = os.path.join(temp_dir, "NotoSansSC-Regular.otf")

                    if not os.path.exists(temp_font_path):
                        urlretrieve(font_url, temp_font_path)

                    return temp_font_path

                except Exception as e:
                    print(f"字体设置失败: {str(e)}")
                    return None

            def create_adaptive_text_frame(text):
              """创建自适应大小的字幕帧，自动分行"""
              img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
              draw = ImageDraw.Draw(img)

              try:
                  # 获取字体路径
                  font_path = setup_font()
                  if font_path:
                      font = ImageFont.truetype(font_path, font_size)
                  else:
                      font = ImageFont.load_default()
                      print("使用默认字体")

                  # 自动分行处理
                  def split_text_into_lines(text, max_width):
                      """将文本自动分成合适宽度的多行"""
                      words = text.replace('，', '，\n').replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
                      lines = []
                      current_line = ''

                      for word in words:
                          # 测试当前行加上新词的宽度
                          test_line = current_line + word
                          bbox = draw.textbbox((0, 0), test_line, font=font)
                          test_width = bbox[2] - bbox[0]

                          if test_width <= max_width:
                              current_line = test_line
                          else:
                              # 如果当前行不为空，添加到行列表
                              if current_line:
                                  lines.append(current_line)
                              # 开始新的一行
                              current_line = word

                      # 添加最后一行
                      if current_line:
                          lines.append(current_line)

                      # 只返回最多两行
                      return lines[:3]

                  # 计算最大行宽（视频宽度的80%）
                  max_line_width = int(canvas_width * 0.7)

                  # 分行处理
                  lines = split_text_into_lines(text, max_line_width)

                  # 计算字幕位置（底部）
                  bottom_margin = int(canvas_height * 0.05)  # 底部留5%的边距
                  y_position = canvas_height - bottom_margin - (len(lines) * font_size * 1.5)

                  # 绘制每行文本
                  for line in lines:
                      bbox = draw.textbbox((0, 0), line, font=font)
                      text_width = bbox[2] - bbox[0]
                      x = (canvas_width - text_width) // 2

                      # 绘制描边
                      outline_color = 'black'
                      outline_width = max(1, int(font_size * 0.05))
                      for dx in range(-outline_width, outline_width + 1):
                          for dy in range(-outline_width, outline_width + 1):
                              draw.text((x + dx, y_position + dy), line, font=font, fill=outline_color)

                      # 绘制主文本
                      draw.text((x, y_position), line, font=font, fill='white')
                      y_position += int(font_size * 1.5)

              except Exception as e:
                  print(f"创建字幕帧时出错: {str(e)}")
                  draw.text((10, 10), "字幕渲染错误", font=ImageFont.load_default(), fill='white')

              return np.array(img)

            # 创建字幕片段
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

    face_path = os.path.join(project_path, "10.jpg")
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
