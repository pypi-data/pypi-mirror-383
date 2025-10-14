from dataclasses import dataclass
import json
import re
from typing import Any

from bilibili_api import HEADERS, Credential, request_settings, select_client
from bilibili_api.video import Video
from nonebot import logger

from ..config import plugin_config_dir, rconfig
from ..cookie import ck2dict
from ..exception import ParseException


@dataclass
class BilibiliVideoInfo:
    """Bilibili 视频信息"""

    title: str
    display_info: str
    cover_url: str
    video_duration: int
    video_url: str
    audio_url: str | None
    ai_summary: str


class BilibiliParser:
    def __init__(self):
        self.headers = HEADERS.copy()
        self._credential: Credential | None = None
        self._cookies_file = plugin_config_dir / "bilibili_cookies.json"
        # 选择客户端
        select_client("curl_cffi")
        # 模仿浏览器
        request_settings.set("impersonate", "chrome131")
        # 第二参数数值参考 curl_cffi 文档
        # https://curl-cffi.readthedocs.io/en/latest/impersonate.html

    async def _init_credential(self) -> Credential | None:
        """初始化 bilibili api"""

        if not rconfig.r_bili_ck:
            logger.warning("未配置 r_bili_ck, 无法使用哔哩哔哩 AI 总结, 可能无法解析 720p 以上画质视频")
            return None

        credential = Credential.from_cookies(ck2dict(rconfig.r_bili_ck))
        if not await credential.check_valid() and self._cookies_file.exists():
            logger.info(f"r_bili_ck 已过期, 尝试从 {self._cookies_file} 加载")
            credential = Credential.from_cookies(json.loads(self._cookies_file.read_text()))
        else:
            logger.info(f"r_bili_ck 有效, 保存到 {self._cookies_file}")
            self._cookies_file.write_text(json.dumps(credential.get_cookies()))

        return credential

    @property
    async def credential(self) -> Credential | None:
        """获取哔哩哔哩登录凭证"""

        if self._credential is None:
            self._credential = await self._init_credential()
            if self._credential is None:
                return None

        if not await self._credential.check_valid():
            logger.warning("哔哩哔哩 cookies 已过期, 请重新配置 r_bili_ck")
            return self._credential

        if await self._credential.check_refresh():
            logger.info("哔哩哔哩 cookies 需要刷新")
            if self._credential.has_ac_time_value() and self._credential.has_bili_jct():
                await self._credential.refresh()
                logger.info(f"哔哩哔哩 cookies 刷新成功, 保存到 {self._cookies_file}")
                self._cookies_file.write_text(json.dumps(self._credential.get_cookies()))
            else:
                logger.warning("哔哩哔哩 cookies 刷新需要包含 SESSDATA, ac_time_value, bili_jct")

        return self._credential

    async def parse_opus(self, opus_id: int) -> tuple[list[str], str]:
        """解析动态信息

        Args:
            opus_id (int): 动态 id

        Returns:
            tuple[list[str], str]: 图片 url 列表和动态信息
        """
        from bilibili_api.opus import Opus

        opus = Opus(opus_id, await self.credential)
        opus_info = await opus.get_info()
        if not isinstance(opus_info, dict):
            raise ParseException("获取动态信息失败")

        # 获取图片信息
        urls = await opus.get_images_raw_info()
        urls = [url["url"] for url in urls]

        dynamic = opus.turn_to_dynamic()
        dynamic_info: dict[str, Any] = await dynamic.get_info()
        orig_text = (
            dynamic_info.get("item", {})
            .get("modules", {})
            .get("module_dynamic", {})
            .get("major", {})
            .get("opus", {})
            .get("summary", {})
            .get("rich_text_nodes", [{}])[0]
            .get("orig_text", "")
        )
        return urls, orig_text

    async def parse_live(self, room_id: int) -> tuple[str, str, str]:
        """解析直播信息

        Args:
            room_id (int): 直播 id

        Returns:
            tuple[str, str, str]: 标题、封面、关键帧
        """
        from bilibili_api.live import LiveRoom

        room = LiveRoom(room_display_id=room_id, credential=await self.credential)
        room_info: dict[str, Any] = (await room.get_room_info())["room_info"]
        title, cover, keyframe = (
            room_info["title"],
            room_info["cover"],
            room_info["keyframe"],
        )
        return (title, cover, keyframe)

    async def parse_read(self, read_id: int) -> tuple[list[str], list[str]]:
        """专栏解析

        Args:
            read_id (int): 专栏 id

        Returns:
            list[str]: img url or text
        """
        from bilibili_api.article import Article

        ar = Article(read_id)

        # 加载内容
        await ar.fetch_content()
        data = ar.json()

        def accumulate_text(node: dict):
            text = ""
            if "children" in node:
                for child in node["children"]:
                    text += accumulate_text(child) + " "
            if _text := node.get("text"):
                text += _text if isinstance(_text, str) else str(_text) + node["url"]
            return text

        urls: list[str] = []
        texts: list[str] = []
        for node in data.get("children", []):
            node_type = node.get("type")
            if node_type == "ImageNode":
                if img_url := node.get("url", "").strip():
                    urls.append(img_url)
                    # 补空串占位符
                    texts.append("")
            elif node_type == "ParagraphNode":
                if text := accumulate_text(node).strip():
                    texts.append(text)
            elif node_type == "TextNode":
                if text := node.get("text", "").strip():
                    texts.append(text)
        return texts, urls

    async def parse_favlist(self, fav_id: int) -> tuple[list[str], list[str]]:
        """解析收藏夹信息

        Args:
            fav_id (int): 收藏夹 id

        Returns:
            tuple[list[str], list[str]]: 标题、封面、简介、链接
        """
        from bilibili_api.favorite_list import get_video_favorite_list_content

        fav_list: dict[str, Any] = await get_video_favorite_list_content(fav_id)
        if fav_list["medias"] is None:
            raise ParseException("收藏夹内容为空, 或被风控")
        # 取前 50 个
        medias_50: list[dict[str, Any]] = fav_list["medias"][:50]
        texts: list[str] = []
        urls: list[str] = []
        for fav in medias_50:
            title, cover, intro, link = (
                fav["title"],
                fav["cover"],
                fav["intro"],
                fav["link"],
            )
            matched = re.search(r"\d+", link)
            if not matched:
                continue
            avid = matched.group(0) if matched else ""
            urls.append(cover)
            texts.append(f"🧉 标题：{title}\n📝 简介：{intro}\n🔗 链接：{link}\nhttps://bilibili.com/video/av{avid}")
        return texts, urls

    async def parse_video(self, *, bvid: str | None = None, avid: int | None = None) -> Video:
        """解析视频信息

        Args:
            bvid (str | None): bvid
            avid (int | None): avid
        """
        if avid:
            return Video(aid=avid, credential=await self.credential)
        elif bvid:
            return Video(bvid=bvid, credential=await self.credential)
        else:
            raise ParseException("avid 和 bvid 至少指定一项")

    async def parse_video_info(
        self,
        *,
        bvid: str | None = None,
        avid: int | None = None,
        page_num: int = 1,
    ) -> BilibiliVideoInfo:
        """解析视频信息

        Args:
            bvid (str | None): bvid
            avid (int | None): avid
            page_num (int): 页码
        """

        video = await self.parse_video(bvid=bvid, avid=avid)
        video_info: dict[str, Any] = await video.get_info()

        video_duration: int = int(video_info["duration"])

        cover_url: str | None = None
        title: str = video_info["title"]
        # 处理分 p
        page_idx = page_num - 1
        if (pages := video_info.get("pages")) and len(pages) > 1:
            assert isinstance(pages, list)
            # 取模防止数组越界
            page_idx = page_idx % len(pages)
            p_video = pages[page_idx]
            # 获取分集时长
            video_duration = int(p_video.get("duration", video_duration))
            # 获取分集标题
            if p_name := p_video.get("part").strip():
                title += f"\n分集: {p_name}"
            # 获取分集封面
            if first_frame_url := p_video.get("first_frame"):
                cover_url = first_frame_url
        else:
            page_idx = 0

        # 获取下载链接
        video_url, audio_url = await self.parse_video_download_url(video=video, page_index=page_idx)
        # 获取在线观看人数
        online = await video.get_online()

        display_info = (
            f"{self._extra_bili_info(video_info)}\n"
            f"📝 简介：{video_info['desc']}\n"
            f"🏄‍♂️ {online['total']} 人正在观看，{online['count']} 人在网页端观看"
        )
        ai_summary: str = "哔哩哔哩 cookie 未配置或失效, 无法使用 AI 总结"
        # 获取 AI 总结
        if self._credential:
            cid = await video.get_cid(page_idx)
            ai_conclusion = await video.get_ai_conclusion(cid)
            ai_summary = ai_conclusion.get("model_result", {"summary": ""}).get("summary", "").strip()
            ai_summary = f"AI总结: {ai_summary}" if ai_summary else "该视频暂不支持AI总结"

        return BilibiliVideoInfo(
            title=title,
            display_info=display_info,
            cover_url=cover_url if cover_url else video_info["pic"],
            video_url=video_url,
            audio_url=audio_url,
            video_duration=video_duration,
            ai_summary=ai_summary,
        )

    async def parse_video_download_url(
        self,
        *,
        video: Video | None = None,
        bvid: str | None = None,
        avid: int | None = None,
        page_index: int = 0,
    ) -> tuple[str, str | None]:
        """解析视频下载链接

        Args:
            bvid (str | None): bvid
            avid (int | None): avid
            page_index (int): 页索引 = 页码 - 1
        """

        from bilibili_api.video import (
            AudioStreamDownloadURL,
            VideoDownloadURLDataDetecter,
            VideoQuality,
            VideoStreamDownloadURL,
        )

        if video is None:
            video = await self.parse_video(bvid=bvid, avid=avid)
        # 获取下载数据
        download_url_data = await video.get_download_url(page_index=page_index)
        detecter = VideoDownloadURLDataDetecter(download_url_data)
        streams = detecter.detect_best_streams(
            video_max_quality=VideoQuality._1080P,
            codecs=rconfig.r_bili_video_codes,
            no_dolby_video=True,
            no_hdr=True,
        )
        video_stream = streams[0]
        if not isinstance(video_stream, VideoStreamDownloadURL):
            raise ParseException("未找到可下载的视频流")
        logger.debug(f"视频流质量: {video_stream.video_quality.name}, 编码: {video_stream.video_codecs}")
        audio_stream = streams[1]
        if not isinstance(audio_stream, AudioStreamDownloadURL):
            return video_stream.url, None
        logger.debug(f"音频流质量: {audio_stream.audio_quality.name}")
        return video_stream.url, audio_stream.url

    def _extra_bili_info(self, video_info: dict[str, Any]) -> str:
        """
        格式化视频信息
        """
        # 获取视频统计数据
        video_state: dict[str, Any] = video_info["stat"]

        # 定义需要展示的数据及其显示名称
        stats_mapping = [
            ("👍", "like"),
            ("🪙", "coin"),
            ("⭐", "favorite"),
            ("↩️", "share"),
            ("💬", "reply"),
            ("👀", "view"),
            ("💭", "danmaku"),
        ]

        # 构建结果字符串
        result_parts = []
        for display_name, stat_key in stats_mapping:
            value = video_state[stat_key]
            # 数值超过10000时转换为万为单位
            formatted_value = f"{value / 10000:.1f}万" if value > 10000 else str(value)
            result_parts.append(f"{display_name} {formatted_value}")

        return " ".join(result_parts)
