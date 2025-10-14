import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from ..config import store
from ..constants import DISABLED_GROUPS


def load_or_initialize_set() -> set[int]:
    """加载或初始化关闭解析的名单"""
    data_file = store.get_plugin_data_file(DISABLED_GROUPS)
    # 判断是否存在
    if not data_file.exists():
        data_file.write_text(json.dumps([]))
    return set(json.loads(data_file.read_text()))


def save_disabled_groups():
    """保存关闭解析的名单"""
    data_file = store.get_plugin_data_file(DISABLED_GROUPS)
    data_file.write_text(json.dumps(list(disabled_group_set)))


# 内存中关闭解析的名单，第一次先进行初始化
disabled_group_set: set[int] = load_or_initialize_set()


# Rule
def is_not_in_disabled_groups(event: MessageEvent) -> bool:
    return event.group_id not in disabled_group_set if isinstance(event, GroupMessageEvent) else True


@on_command("开启所有解析", permission=SUPERUSER, block=True).handle()
async def _(matcher: Matcher, event: PrivateMessageEvent):
    """开启所有解析"""
    disabled_group_set.clear()
    save_disabled_groups()
    await matcher.finish("所有解析已开启")


@on_command("关闭所有解析", permission=SUPERUSER, block=True).handle()
async def _(matcher: Matcher, bot: Bot, event: PrivateMessageEvent):
    """关闭所有解析"""
    gid_list: list[int] = [g["group_id"] for g in await bot.get_group_list()]
    disabled_group_set.update(gid_list)
    save_disabled_groups()
    await matcher.finish("所有解析已关闭")


@on_command(
    "开启解析",
    rule=to_me(),
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    block=True,
).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    """开启解析"""
    gid = event.group_id
    if gid in disabled_group_set:
        disabled_group_set.remove(gid)
        save_disabled_groups()
        await matcher.finish("解析已开启")
    else:
        await matcher.finish("解析已开启，无需重复开启")


@on_command(
    "关闭解析",
    rule=to_me(),
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    block=True,
).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    """关闭解析"""
    gid = event.group_id
    if gid not in disabled_group_set:
        disabled_group_set.add(gid)
        save_disabled_groups()
        await matcher.finish("解析已关闭")
    else:
        await matcher.finish("解析已关闭，无需重复关闭")


@on_command("查看关闭解析", permission=SUPERUSER, block=True).handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    """查看关闭解析"""
    disable_groups = [
        str(item) + "--" + (await bot.get_group_info(group_id=item))["group_name"] for item in disabled_group_set
    ]
    disable_groups = "\n".join(disable_groups)
    if isinstance(event, GroupMessageEvent):
        await matcher.send("已经发送到私信了~")
    message = f"解析关闭的群聊如下：\n{disable_groups} \n🌟 温馨提示：如果想开关解析需要在群聊@我然后输入[开启/关闭解析], 另外还可以私信我发送[开启/关闭所有解析]"  # noqa: E501
    await bot.send_private_msg(user_id=event.user_id, message=message)
