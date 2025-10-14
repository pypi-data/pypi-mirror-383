import os
import subprocess
from typing import Optional


def mp3_to_wav(
    input_path: str,
    output_path: str,
    channels: int = 1,        # 声道数（1=单声道，2=立体声）
    sample_rate: int = 44100, # 采样率（Hz）
    bit_depth: int = 16       # 位深（16位=PCM_S16LE）
) -> None:
    """
    使用ffmpeg将MP3转换为WAV格式（底层调用ffmpeg命令）
    
    :param input_path: MP3输入文件路径（如 "sound1.mp3"）
    :param output_path: WAV输出文件路径（如 "output.wav"）
    :param channels: 输出声道数（1=单声道，2=立体声）
    :param sample_rate: 输出采样率（如 44100、16000）
    :param bit_depth: 位深（仅支持16位，对应PCM_S16LE）
    :raises FileNotFoundError: 输入文件不存在或ffmpeg未安装
    :raises RuntimeError: ffmpeg转换失败
    """
    # 校验输入文件
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    if not input_path.lower().endswith(".mp3"):
        raise ValueError(f"输入文件必须是MP3格式: {input_path}")
    
    # 校验ffmpeg是否安装
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except FileNotFoundError:
        raise FileNotFoundError("未找到ffmpeg，请先安装（https://ffmpeg.org/download.html）")
    
    # 校验位深（目前只支持16位，对应PCM_S16LE）
    if bit_depth != 16:
        raise ValueError("当前仅支持16位深（PCM_S16LE）")
    
    # 构建ffmpeg命令（对应你提供的命令逻辑）
    # 命令示例：ffmpeg -i input.mp3 -vn -acodec pcm_s16le -ac 1 -ar 44100 output.wav
    cmd = [
        "ffmpeg",
        "-i", input_path,          # 输入文件
        "-vn",                     # 不处理视频流（纯音频）
        "-acodec", "pcm_s16le",    # 音频编码（16位PCM）
        "-ac", str(channels),      # 声道数
        "-ar", str(sample_rate),   # 采样率
        output_path                # 输出文件
    ]
    
    # 执行命令
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(f"转换成功: {input_path} -> {output_path}")
    except subprocess.CalledProcessError as e:
        # 捕获ffmpeg错误信息
        raise RuntimeError(f"转换失败: {e.stderr}") from e