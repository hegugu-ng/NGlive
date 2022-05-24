"""
转码模块

>> 对指定文件进行压制
>> 监控 ffmpeg 输出信息
>> 发送相应事件
>> TODO 可以定义参数

"""
from eventManager import Event
from taskslist import TRANSCODE
from resquest_test import TtranscodeOut
import re,math,subprocess
from log import logger

class transcode:
    """
    转码模块
    -------

    用于对指定媒体文件进行转码：

    """
    def __init__(self,eventManager):
        self.__eventManager = eventManager
        self.pros = 0
        self.__active = True

    def sendEvent(self,msg,**dt):
        """
        事件发送器
        ---------

        封装一个常用的事件发送方法

        """
        event = Event(type_=msg)
        event.dict["artical"] = TtranscodeOut(**dt)
        self.__eventManager.SendEvent(event)

    def get_seconds(self,time):
        """
        返回日志切片器
        -------------

        用于对ffmpeg 的输出日志进行相关切片操作
        """
        h = int(time[:2])
        m = int(time[3:5])
        s = int(time[6:8])
        ms = int(time[9:12])
        return (h * 60 * 60) + (m * 60) + s + (ms / 1000)

    def compute_progress_and_send_progress(self,process,tasksid):
        """
        日志解析器
        ---------

        通过正则匹配进行日志解析，获取相关数据
        """
        duration = None
        while process.poll() is None:
            if line := process.stderr.readline().strip():
                duration_res = re.search(r'Duration: (?P<duration>\S+)', line)
                if duration_res is not None:
                    duration = duration_res.groupdict()['duration']
                    duration = re.sub(r',', '', duration)

                result = re.search(r'time=(?P<time>\S+)', line)

                if result is not None and duration is not None:
                    elapsed_time = result.groupdict()['time']

                    currentTime =  self.get_seconds(elapsed_time)
                    allTime = self.get_seconds(duration)

                    progress = currentTime * 100/allTime
                    progress = math.ceil(progress)
                    progress = min(progress, 100)
                    if progress != self.pros:
                        self.sendEvent("IsTranscode",tasksid = tasksid,progress = progress)
                    self.pros = progress
                    # print(f"当前压制进度：{progress}%")

    def do_ffmpeg_transcode(self,cmd,tasksid):
        """
        ffmpeg 核心
        ----------

        用于驱动FFmpeg 同时触发部分事件

        """
        try:
            process=subprocess.Popen(cmd,stderr=subprocess.PIPE,bufsize=0,universal_newlines=True,shell=True,encoding="ISO-8859-1")
            self.compute_progress_and_send_progress(process,tasksid)
            if process.returncode == 0:
                self.sendEvent("TranscodeEnded",tasksid = tasksid)
                return "success" ,process
            else:
                self.sendEvent("TranscodeError",tasksid = tasksid)
                return "error" ,process
        except:
            self.sendEvent("TranscodeError",tasksid = tasksid)


    def cmd_command(self,Origin,OutPut):
        """
        生成cmd命令
        """
        from configparser import ConfigParser
        config = ConfigParser()
        config.read('config.ini',encoding='utf-8')
        transcode_config = config['TRANSCODE']
        model = transcode_config['model']
        encoder = transcode_config['encoder']
        crf = transcode_config['crf']
        cq = transcode_config['cq']
        Bitrate = transcode_config['Bitrate']
        bufsize = transcode_config['bufsize']
        preset = transcode_config['preset']
        # 选择编码器
        if encoder == "X264":
            encoder = "libx264"
        else:
            logger.error("不支持的编码器")
            raise TypeError("不支持的编码器")
        bz = ""
        if model == "CRF":
            model = f"-crf {crf}"
        elif model == "CQ":
            model = f"-qp {cq}"
        elif model == "B":
            model = f"-b {Bitrate}k"
        elif model == "VBR":
            model = ""
            bz = f"-bufsize {bufsize}k"
        elif model == "ABR":
            model = f"-b:v {Bitrate}k"
            bz = f"-bufsize {bufsize}k"

        return f"ffmpeg -y -i {Origin} -vcodec {encoder} -preset {preset} {model} {bz} {OutPut}"


    def transcode_manege(self,task):
        """
        转码管理模块
        -----------

        管理转码，从任务队列中获取任务
        进行基本数据解析

        """
        self.sendEvent("TranscodeStarted",tasksid = task.TaskId)
        cmd  = self.cmd_command(task.Origin,task.OutPut)
        logger.debug(f"生成转码命令：{cmd}")
        self.do_ffmpeg_transcode(cmd,task.TaskId)

