import os
import shutil
import time
from datetime import datetime, timedelta
from threading import Thread

import cv2
import numpy as np
from PIL import ImageGrab, ImageFont, ImageDraw, Image
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from pynput.mouse import Listener

from utils.file_utils import get_subdirectories
from utils.time_utils import get_utc_date_str, TimeFormat

mouse = MouseController()


class ScreenRecording(Thread):

    def __init__(self, fps=20, size=(2560, 1440), video_name="temp.mp4", keep_data=7, duration=600, save_path=None):
        super(ScreenRecording, self).__init__()
        self.fps = fps
        self.size = size
        self.flag = True
        self.max_during = duration
        # 查看录屏文件存储位置是否存在，不存在就生成
        save_current_path = os.path.join(save_path, get_utc_date_str())
        if not os.path.exists(save_current_path):
            os.makedirs(save_current_path)
        # 获取保留天数前的数据，并将其删除
        previous_dirs = get_subdirectories(save_current_path)
        base_data = (datetime.now() - timedelta(days=keep_data)).strftime(TimeFormat.YYYYMMDD.value)
        for old_dir in previous_dirs:
            if os.path.basename(old_dir) < base_data:
                shutil.rmtree(old_dir, ignore_errors=True)

        self.file_name = os.path.join(save_current_path, video_name)
        self.finished = True
        self.glow = 0

        self.resolution = ImageGrab.grab().size
        self.cc_height = 20
        self.font = ImageFont.load_default()
        self.current_step = ''
        self.current_step_color = 'white'

    def set_setup(self, step, success=None):
        self.current_step = step
        if success is None:
            self.current_step_color = (255, 255, 200)
        elif success:
            self.current_step_color = "green"
        else:
            self.current_step_color = "red"

    def click(self, x, y, b, p):
        """按下左键时，发光效果增强"""
        if p and b == Button.left:
            self.glow += 4

    def run(self):
        interval = 1 / self.fps  # 每帧间隔时长
        total_time = 0
        start_time = time.time()
        radius = 15  # 鼠标圆圈半径
        step = 50  # 颜色变化步长

        listener = Listener(on_click=self.click)  # 启动鼠标监听事件
        listener.start()
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 设置视频编码格式
        video = cv2.VideoWriter(self.file_name, fourcc, self.fps, self.size)  # 创建视频写入器
        # 录制的主循环
        while self.flag:
            try:
                im = ImageGrab.grab()  # 截取屏幕
            except OSError:
                time.sleep(0.01)
                continue
            m_position = mouse.position  # 获取鼠标位置
            draw = ImageDraw.Draw(im)
            # 绘制蓝色圆圈表示鼠标位置
            draw.ellipse((m_position[0] - radius, m_position[1] - radius, m_position[0] + radius, m_position[1] + radius), outline="blue", width=6)
            # 点击发光效果
            if self.glow > 0:
                r2 = radius + (4 - self.glow) * 10  # 计算发光半径
                try:
                    # 绘制绿色发光圆圈
                    draw.ellipse((m_position[0] - r2, m_position[1] - r2, m_position[0] + r2, m_position[1] + r2), outline="green", width=6)
                except:
                    pass
                self.glow -= 1  # 减少发光强度

            # 状态蓝颜色动画
            if isinstance(self.current_step_color, tuple):
                b = self.current_step_color[2]
                if b > 200:
                    step -= 50
                elif b < 0:
                    step = 50
                self.current_step_color = (self.current_step_color[0], self.current_step_color[1], b + step)
            # 在视频顶部显示状态蓝显示时间戳和当前步骤
            im_log = Image.new("RGB", (self.resolution[0], self.cc_height), self.current_step_color)
            log = "{} {}".format(datetime.now().strftime(TimeFormat.YYYY_MM_DD_HH_MM_SS.value), self.current_step)
            ImageDraw.Draw(im_log).text((10, 5), log, font=self.font, fill="black")

            # 视频帧合成和写入
            frame = cv2.cvtColor(np.concatenate((np.array(im_log), np.array(im)), axis=0), cv2.COLOR_RGB2BGR)
            video.write(cv2.resize(frame, self.size))

            # 时间控制器
            total_time += interval
            t_sleep = total_time - (time.time() - start_time)
            if t_sleep > 0:
                time.sleep(total_time)  # 控制帧率
            if total_time > self.max_during:
                break  # 达到最长时间退出
        video.release()
        listener.stop()
        self.finished = True

    def stop(self):
        self.flag = False
        for _ in range(100):
            time.sleep(0.1)
            if self.finished:
                break
        return self.file_name
