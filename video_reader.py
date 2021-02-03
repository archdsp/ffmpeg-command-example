# -*- coding:utf-8 -*-
import logging

# Standard Package
import math

# Community Package
import av
import numpy


__author__ = "smartx"
__copyright__ = "Copyright 2020, Mindslab"
__credits__ = ["smartx"]
__license__ = "Mindslab"
__version__ = "0.1.0"
__maintainer__ = ["Choi, jisu"]
__email__ = ["jisu.choi@mindslab.ai"]
__status__ = "Development"  # Development / Test / Release.


class VideoReader:
    r"""
    RTSP, Video FILE 등 동영상을 인코딩하여 numpy.ndarray 또는 PIL 이미지로 사용하게 해주는 클래스 입니다.
    """
    def __init__(self, path: str = ""):
        r"""
        :param str path: Path for open video. Ex. "/dev/video0", "rtsp://<ip>/:8554", "./video/some_video.mp4"
        """
        self.url = path

        self.containerOptions = {
            "buffer_size": "256000",
            "stimeout": "20000000",
            "max_delay": "3000000",
            "discard_corrupt": "DISCARD_CORRUPT",
            "gen_pts": "GENPTS",
            "non_block": "NONBLOCK",
            "stimeout": "20000000",
            "max_delay": "3000000"
        }

        if "rtsp" in path:
            self.containerOptions["rtsp_transport"] = "udp"

        self.container = None
        self._frameNumber = -1

        self.open(self.url)

    def __del__(self):
        try:
            if self.container is not None:
                self.container.close()
        except Exception as e:
            logging.exception(e)

    @property
    def frameNumber(self):
        return self._frameNumber

    @frameNumber.setter
    def frameNumber(self, value):
        # TODO: Diffrent value assign whether real time stream or file
        self._frameNumber = value

    def isOpened(self) -> bool:
        r"""
        Check whether stream is alive or dead.
        :return: Return true if stream is accesible
        """
        # TODO: Not implemented yet
        if self.container is None:
            return False
        return True

    def open(self, path: str) -> bool:
        r"""
        Open vidoe using given path. Ex. "/dev/video0", "rtsp://<ip>/:8554", "./video/some_video.mp4"
        :param path:
        :return:
        """
        ret = False
        try:
            self.container = av.open(path, container_options=self.containerOptions, timeout=(1.0, 0.1), format=None)
            ret = True
        except av.FileNotFoundError as e:
            logging.exception(e)
        except av.ConnectionRefusedError as e:
            logging.exception(e)
        except Exception as e:
            logging.exception(e)
        finally:
            return ret

    def read(self) -> (bool, numpy.ndarray):
        r"""
        Return True and image when read suceess,
        Return True and None if end of stream or file
        Return False and None if error occur (Ex. Stream connection closed)
        :return (bool, numpy.ndarray):
        """
        packet = next(self.container.demux())
        if packet.stream.type == "video" and packet.pts is not None:
            try:
                videoFrames = packet.decode()
                for videoFrame in videoFrames:
                    self.frameNumber = int(math.ceil(packet.stream.guessed_rate * float(videoFrame.pts * videoFrame.time_base)))
                    img = videoFrame.to_ndarray(format="bgr24")
                    return True, img

            except av.EOFError as e:
                return True, None
            except Exception as e:
                logging.exception(e)
                return False, None

        # Out of if, it means this packet is for audio or another source.
        # # No neccesary to handle this but at future might be needed. So, Leave a room for this
        return True, None