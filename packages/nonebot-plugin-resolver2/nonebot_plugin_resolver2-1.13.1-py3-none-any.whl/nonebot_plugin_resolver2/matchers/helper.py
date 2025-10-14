from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from nonebot.adapters.onebot.utils import f2s
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent, MessageSegment
from nonebot.internal.matcher import current_bot, current_event

from ..config import NEED_FORWARD, NICKNAME, USE_BASE64


class obhelper:
    @staticmethod
    def construct_nodes(user_id: int, segments: Sequence[Message | MessageSegment | str]) -> Message:
        """构造节点

        Args:
            segments (Sequence[Message | MessageSegment | str]): 消息段

        Returns:
            Message: 消息
        """

        def node(content):
            return MessageSegment.node_custom(user_id=user_id, nickname=NICKNAME, content=content)

        return Message([node(seg) for seg in segments])

    @classmethod
    async def send_segments(cls, segments: Sequence[Message | MessageSegment | str]) -> None:
        """发送消息段

        Args:
            segments (Sequence[Message | MessageSegment | str]): 消息段
        """
        bot = current_bot.get()
        event: MessageEvent = cast(MessageEvent, current_event.get())

        if NEED_FORWARD or len(segments) > 4:
            message = cls.construct_nodes(int(bot.self_id), segments)
            kwargs: dict[str, Any] = {"messages": message}
            if isinstance(event, GroupMessageEvent):
                kwargs["group_id"] = event.group_id
                api = "send_group_forward_msg"
            else:
                kwargs["user_id"] = event.user_id
                api = "send_private_forward_msg"
            await bot.call_api(api, **kwargs)

        else:
            segments = list(segments)
            segments[:-1] = [seg + "\n" if isinstance(seg, str) else seg for seg in segments[:-1]]
            message = sum(segments, Message())
            await bot.send(event, message=message)

    @staticmethod
    def img_seg(img_path: Path) -> MessageSegment:
        """获取图片 Seg

        Args:
            img_path (Path): 图片路径

        Returns:
            MessageSegment: 图片 Seg
        """
        file = img_path.read_bytes() if USE_BASE64 else img_path
        return MessageSegment.image(file)

    @staticmethod
    def record_seg(audio_path: Path) -> MessageSegment:
        """获取语音 Seg

        Args:
            audio_path (Path): 语音路径

        Returns:
            MessageSegment: 语音 Seg
        """
        file = audio_path.read_bytes() if USE_BASE64 else audio_path
        return MessageSegment.record(file)

    @classmethod
    def video_seg(cls, video_path: Path) -> MessageSegment:
        """获取视频 Seg

        Returns:
            MessageSegment: 视频 Seg
        """
        seg: MessageSegment
        # 检测文件大小
        file_size_byte_count = int(video_path.stat().st_size)
        file = video_path.read_bytes() if USE_BASE64 else video_path
        if file_size_byte_count == 0:
            seg = MessageSegment.text("视频文件大小为 0")
        elif file_size_byte_count > 100 * 1024 * 1024:
            # 转为文件 Seg
            seg = cls.file_seg(file, display_name=video_path.name)
        else:
            seg = MessageSegment.video(file)
        return seg

    @staticmethod
    def file_seg(file: Path | bytes, display_name: str = "") -> MessageSegment:
        """获取文件 Seg

        Args:
            file (Path | bytes): 文件路径
            display_name (str, optional): 显示名称. Defaults to file.name.

        Returns:
            MessageSegment: 文件 Seg
        """
        if not display_name and isinstance(file, Path):
            display_name = file.name
        if not display_name:
            raise ValueError("文件名不能为空")
        if USE_BASE64:
            file = file.read_bytes() if isinstance(file, Path) else file
        return MessageSegment(
            "file",
            data={
                "name": display_name,
                "file": f2s(file),
            },
        )
