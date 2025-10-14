# 尝试导入pytubefix，如果不可用则尝试pytube
try:
    import pytubefix as pytube

    print("使用pytubefix库")
except ImportError:
    try:
        import pytube

        print("使用pytube库")
    except ImportError:
        print(
            "错误: 未找到pytube或pytubefix库，请运行 'pip install -r requirements.txt' 安装依赖"
        )
        import sys

        sys.exit(1)

import os
import re
import ssl
import sys

# 处理SSL证书验证问题
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    print("警告: 无法设置SSL上下文，可能会影响下载")


def sanitize_filename(filename):
    """移除文件名中不允许的字符"""
    # Windows不允许的字符
    invalid_chars = '<>"/:|?*'
    # 替换这些字符为下划线
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    # 移除多余的空格和点号
    filename = re.sub(r"[\s.]+", "_", filename).strip("_")
    return filename


def on_progress(stream, chunk, bytes_remaining):
    """显示下载进度条"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    bar_length = 50
    filled_length = int(bar_length * bytes_downloaded // total_size)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    print(f"\r下载进度: |{bar}| {percentage_of_completion:.2f}% ", end="")


def download_youtube_video(url, output_path="."):
    """
    下载YouTube视频并重命名为日期+名称格式

    参数:
    url: YouTube视频链接
    output_path: 输出文件夹路径
    """
    try:
        # 创建YouTube对象并设置进度回调
        # 尝试不同的方法创建YouTube对象，以兼容不同版本的库
        try:
            yt = pytube.YouTube(url, on_progress_callback=on_progress)
        except TypeError:
            # 某些版本的pytubefix可能不支持相同的回调参数格式
            yt = pytube.YouTube(url)
            yt.register_on_progress_callback(on_progress)

        print(f"正在获取视频信息: {yt.title}")

        # 获取最高分辨率的视频流
        try:
            stream = yt.streams.get_highest_resolution()
        except Exception:
            stream = None

        if not stream:
            print("无法找到合适的视频流，尝试获取第一个可用的视频流")
            try:
                stream = yt.streams.filter(
                    progressive=True, file_extension="mp4"
                ).first()
            except Exception:
                stream = None

            if not stream:
                print("无法找到可用的视频流")
                return None

        # 获取当前日期
        current_date = yt.publish_date.strftime("%Y年%m月%d日")

        # 清理原始标题
        sanitized_title = sanitize_filename(yt.title)

        # 构建新的文件名
        new_filename = f"{current_date} {sanitized_title}.{stream.subtype}"

        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)

        # 下载视频
        print(
            f"开始下载视频 (大小: {stream.filesize / (1024 * 1024):.2f} MB) 到: {os.path.join(output_path, new_filename)}"
        )
        stream.download(output_path=output_path, filename=new_filename)
        print()  # 换行
        print(f"视频下载完成: {new_filename}")
        return new_filename

    except pytube.exceptions.RegexMatchError:
        print("错误: YouTube URL格式不正确，请检查链接")
        return None
    except pytube.exceptions.VideoUnavailable:
        print("错误: 该视频不可用或已被删除")
        return None
    except pytube.exceptions.AgeRestrictedError:
        print("错误: 该视频有年龄限制，无法直接下载")
        return None
    except Exception as e:
        print(f"下载视频时出错: {str(e)}")
        print("建议: 请检查网络连接，确保URL正确，或者尝试使用其他视频链接")
        return None


if __name__ == "__main__":
    print("YouTube视频下载器")
    print("================")

    while True:
        video_url = input("请输入YouTube视频链接 (输入'q'退出): ")

        if video_url.lower() == "q":
            print("程序已退出。")
            break

        if not video_url.startswith("http"):
            print("请输入有效的YouTube视频链接。")
            continue

        # 调用下载函数
        download_youtube_video(video_url)
