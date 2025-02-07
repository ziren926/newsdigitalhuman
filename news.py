import os
import asyncio
import edge_tts
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import resize
from moviepy.video.VideoClip import ColorClip
from rembg import remove
from datetime import datetime
import subprocess

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
        wav_path = os.path.abspath(os.path.join(project_path, "input_audio.wav"))

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

def generate_subtitle_clips(subtitles, font="C:/Windows/Fonts/msyh.ttc", fontsize=70, color="white"):
    generator = lambda txt: TextClip(txt, font=font, fontsize=fontsize, color=color, method='caption', align="center", size=(1920, 1080))
    return SubtitlesClip(subtitles, generator)

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

def run_wav2lip(project_path):
    try:
        checkpoint_path = os.path.join(project_path, "checkpoints/wav2lip.pth")
        face_path = os.path.join(project_path, "face_video.mp4")
        audio_path = os.path.join(project_path, "input_audio.wav")

        time_str, user, _ = get_current_info()
        print(f"Current Date and Time (UTC): {time_str}")
        print(f"Current User's Login: {user}")
        print("开始处理视频...")

        command = f"python inference.py --checkpoint_path {checkpoint_path} --face {face_path} --audio {audio_path}"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        print("视频处理完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"视频处理失败：{str(e)}")
        print(f"错误输出：{e.stderr if hasattr(e, 'stderr') else '无错误输出'}")
        return False
    except Exception as e:
        print(f"发生错误：{str(e)}")
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

def combine_videos(background_video_path, face_video_path, audio_path, output_path="final_video.mp4"):
    print(f"Combining videos: background ({background_video_path}) and face ({face_video_path}) with audio ({audio_path})")
    background_clip = VideoFileClip(background_video_path)
    face_clip = VideoFileClip(face_video_path).resize(height=background_clip.h // 2)
    face_clip = face_clip.set_position(("right", "bottom"))

    final_clip = CompositeVideoClip([background_clip, face_clip])
    final_clip = final_clip.set_audio(AudioFileClip(audio_path))
    final_clip.write_videofile(output_path, codec="libx264")

async def main():
    project_path = os.getcwd()  # 使用当前目录

    start_time = datetime.utcnow()
    time_str, user, _ = get_current_info()
    print(f"Starting process...")
    print(f"Current Date and Time (UTC): {time_str}")
    print(f"Current User's Login: {user}")

    texts = [
        "TikTok在美国的运营状况",
        "由于美国政府的禁令，TikTok于2025年1月19日起在美国暂停服务，应用程序已从苹果和谷歌应用商店下架。",
        "此前，美国最高法院裁定支持TikTok的禁令，要求其母公司字节跳动在2025年1月19日前将TikTok出售给非中国企业，否则将被禁止在美国运营。",
        "美国当选总统特朗普表示，可能会在上任后给予TikTok 90天的宽限期，以寻求解决方案。",
        "TikTok Shop扩展至墨西哥市场",
        "TikTok Shop宣布将于2025年1月13日正式上线墨西哥市场，并开放首批店铺入驻权限。",
        "2月6日，TikTok Shop的达人带货功能正式上线，创作者可以通过视频直接推广产品并赚取佣金。",
        "2月13日，墨西哥商城将正式开放，消费者将能够直接在平台上购物，享受更便捷的购物体验。"
    ]

    text = " ".join(texts)  # 合并文本生成音频

    if not await generate_audio(text, project_path):
        return

    audio_clip = AudioFileClip(os.path.join(project_path, "input_audio.wav"))
    audio_duration = audio_clip.duration

    duration_per_text = audio_duration / len(texts)
    subtitles = generate_subtitles(texts, duration_per_text)
    subtitle_clip = generate_subtitle_clips(subtitles)

    # 创建一个空的视频剪辑，与字幕剪辑组合
    empty_video = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=audio_duration)
    video_with_subtitles = CompositeVideoClip([empty_video, subtitle_clip.set_pos('center')])

    # 生成背景视频
    background_video_path = os.path.join(project_path, "background_video.mp4")
    video_with_subtitles.write_videofile(background_video_path, fps=24, codec="libx264")

    face_image_path = os.path.join(project_path, "input_face.jpg")  # 确保这个路径指向你的脸部图片
    face_image_no_bg_path = os.path.join(project_path, "face_image_no_bg.png")
    if not remove_background(face_image_path, face_image_no_bg_path):
        return

    generate_face_video(face_image_no_bg_path, audio_duration, os.path.join(project_path, "face_video.mp4"))

    if not run_wav2lip(project_path):
        return

    combine_videos(background_video_path, os.path.join(project_path, "temp/result.avi"), os.path.join(project_path, "input_audio.wav"))

    end_time = datetime.utcnow()
    processing_time = end_time - start_time
    print(f"\n处理完成！")
    print(f"总处理时间: {processing_time.total_seconds():.2f} 秒")
    print(f"最终输出文件位置: {os.path.join(project_path, 'final_video.mp4')}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
