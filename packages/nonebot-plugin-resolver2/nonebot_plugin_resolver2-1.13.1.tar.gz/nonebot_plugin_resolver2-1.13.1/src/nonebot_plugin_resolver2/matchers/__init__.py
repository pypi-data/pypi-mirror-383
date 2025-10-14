from nonebot.matcher import Matcher

from .acfun import acfun
from .bilibili import bilibili
from .douyin import douyin
from .kuaishou import kuaishou
from .tiktok import tiktok
from .twitter import twitter
from .weibo import weibo
from .xiaohongshu import xiaohongshu
from .ytb import ytb

resolvers: dict[str, type[Matcher]] = {
    "bilibili": bilibili,
    "acfun": acfun,
    "douyin": douyin,
    "kuaishou": kuaishou,
    "ytb": ytb,
    "twitter": twitter,
    "tiktok": tiktok,
    "weibo": weibo,
    "xiaohongshu": xiaohongshu,
}
