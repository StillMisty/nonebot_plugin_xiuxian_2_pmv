from nonebot import on_command, require, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GROUP,
    Message,
    GroupMessageEvent,
    MessageSegment,
    ActionFailed
)
from ..xiuxian_utils.lay_out import assign_bot, Cooldown
from ..xiuxian_utils.data_source import jsondata
from nonebot.log import logger
from ..xiuxian_utils.utils import check_user, get_msg_pic, send_msg_handler
from .impart_pk_uitls import impart_pk_check
from .xu_world import xu_world
from .impart_pk import impart_pk
from ..xiuxian_config import XiuConfig
from ..xiuxian_utils.xiuxian2_handle import XiuxianDateManage, OtherSet, UserBuffDate, XIUXIAN_IMPART_BUFF
from .. import NICKNAME

xiuxian_impart = XIUXIAN_IMPART_BUFF()
sql_message = XiuxianDateManage()  # sql类

impart_re = require("nonebot_plugin_apscheduler").scheduler

impart_pk_project = on_fullmatch("投影虚神界", priority=6, permission=GROUP, block=True)
impart_pk_now = on_command("虚神界对决", priority=15, permission=GROUP, block=True)
impart_pk_list = on_fullmatch("虚神界列表", priority=7, permission=GROUP, block=True)
impart_pk_exp = on_command("虚神界修炼", priority=8, permission=GROUP, block=True)


# 每日0点重置用虚神界次数
@impart_re.scheduled_job("cron", hour=0, minute=0)
async def impart_re_():
    impart_pk.re_data()
    xu_world.re_data()
    logger.opt(colors=True).info("<green>已重置虚神界次数</green>")


@impart_pk_project.handle(parameterless=[Cooldown(at_sender=False)])
async def impart_pk_project_(bot: Bot, event: GroupMessageEvent):
    """投影虚神界"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_project.finish()
    user_id = user_info['user_id']
    impart_data_draw = await impart_pk_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_project.finish()
    # 加入虚神界
    if impart_pk.find_user_data(user_id)["pk_num"] <= 0:
        msg = "道友今日次数已用尽，无法在加入虚神界！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_project.finish()
    msg = xu_world.add_xu_world(user_id)
    if XiuConfig().img:
        pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=msg)
    await impart_pk_project.finish()


@impart_pk_list.handle(parameterless=[Cooldown(at_sender=False)])
async def impart_pk_list_(bot: Bot, event: GroupMessageEvent):
    """虚神界列表"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_list.finish()
    user_id = user_info['user_id']
    impart_data_draw = await impart_pk_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_list.finish()
    xu_list = xu_world.all_xu_world_user()
    if len(xu_list) == 0:
        msg = "虚神界里还没有投影呢，快来输入【投影虚神界】加入分身吧！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_list.finish()
    list_msg = []
    win_num = "win_num"
    pk_num = "pk_num"
    for x in range(len(xu_list)):
        user_data = impart_pk.find_user_data(xu_list[x])
        if user_data:
            name = sql_message.get_user_info_with_id(xu_list[x])['user_name']
            msg = ""
            msg += f"编号：{user_data['number']}\n"
            msg += f"道友：{name}\n"
            msg += f"胜场：{user_data[win_num]}\n"
            msg += f"剩余决斗次数：{user_data[pk_num]}"
            list_msg.append(
                {"type": "node", "data": {"name": f"编号 {x}", "uin": bot.self_id,
                                          "content": msg}})
    try:
        await send_msg_handler(bot, event, list_msg)
    except ActionFailed:
        msg = "未知原因，查看失败!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_list.finish()
    await impart_pk_list.finish()


@impart_pk_now.handle(parameterless=[Cooldown(cd_time=3, at_sender=False)])
async def impart_pk_now_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """虚神界对决"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()
    user_id = user_info['user_id']
    sql_message.update_last_check_info_time(user_id)  # 更新查看修仙信息时间
    impart_data_draw = await impart_pk_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()

    num = args.extract_plain_text().strip()
    user_data = impart_pk.find_user_data(user_info['user_id'])

    if user_data["pk_num"] <= 0:
        msg = "道友今日次数耗尽，每天再来吧！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()

    player_1_stones = 0
    player_2_stones = 0
    combined_msg = ""
    duel_count = 0

    if not num:
        while user_data["pk_num"] > 0:
            duel_count += 1
            msg, win = await impart_pk_uitls.impart_pk_now_msg_to_bot(user_info['user_name'], NICKNAME)
            if win == 1:
                msg += f"战报：道友{user_info['user_name']}获胜,获得思恋结晶10颗\n"
                impart_pk.update_user_data(user_info['user_id'], True)
                xiuxian_impart.update_stone_num(10, user_id, 1)
                player_1_stones += 10
            elif win == 2:
                msg += f"战报：道友{user_info['user_name']}败了,消耗一次次数,获得思恋结晶5颗\n"
                impart_pk.update_user_data(user_info['user_id'], False)
                xiuxian_impart.update_stone_num(5, user_id, 1)
                player_1_stones += 5
                if impart_pk.find_user_data(user_id)["pk_num"] <= 0 and xu_world.check_xu_world_user_id(user_id) is True:
                    msg += "检测到道友次数已用尽，已帮助道友退出虚神界！"
                    xu_world.del_xu_world(user_id)
            else:
                msg = f"挑战失败"
                combined_msg += f"{msg}\n"
                break

            combined_msg += f"☆------------第{duel_count}次------------☆\n{msg}\n"
            user_data = impart_pk.find_user_data(user_info['user_id'])

        combined_msg += f"总计：道友{user_info['user_name']}获得思恋结晶{player_1_stones}颗\n"

        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + combined_msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=combined_msg)
        await impart_pk_now.finish()

    if not num.isdigit():
        msg = "编号解析异常，应全为数字!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()

    num = int(num) - 1
    xu_world_list = xu_world.all_xu_world_user()

    if num + 1 > len(xu_world_list) or num < 0:
        msg = "编号解析异常，虚神界没有此编号道友!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()

    player_1 = user_info['user_id']
    player_2 = xu_world_list[num]
    if str(player_1) == str(player_2):
        msg = "道友不能挑战自己的投影!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_now.finish()

    player_1_name = user_info['user_name']
    player_2_name = sql_message.get_user_info_with_id(player_2)['user_name']

    while user_data["pk_num"] > 0:
        duel_count += 1
        msg_list, win = await impart_pk_uitls.impart_pk_now_msg(player_1, player_1_name, player_2, player_2_name)
        if win is None:
            msg = f"挑战失败"
            combined_msg += f"{msg}\n"
            break

        if win == 1:  # 1号玩家胜利 发起者
            impart_pk.update_user_data(player_1, True)
            impart_pk.update_user_data(player_2, False)
            xiuxian_impart.update_stone_num(10, player_1, 1)
            xiuxian_impart.update_stone_num(5, player_2, 1)
            player_1_stones += 10
            player_2_stones += 5
            msg_list.append(
                {"type": "node", "data": {"name": f"虚神界战报", "uin": bot.self_id,
                                          "content": f"道友{player_1_name}获得了胜利,获得了思恋结晶10!\n"
                                                     f"道友{player_2_name}获得败了,消耗一次次数,获得了思恋结晶5颗!"}})
            if impart_pk.find_user_data(player_2)["pk_num"] <= 0:
                msg_list.append(
                    {"type": "node", "data": {"name": f"虚神界变更", "uin": bot.self_id,
                                              "content": f"道友{player_2_name}次数耗尽，离开了虚神界！"}})
                xu_world.del_xu_world(player_2)
                combined_msg += "\n".join([node['data']['content'] for node in msg_list])
                break
        elif win == 2:  # 2号玩家胜利 被挑战者
            impart_pk.update_user_data(player_2, True)
            impart_pk.update_user_data(player_1, False)
            xiuxian_impart.update_stone_num(10, player_2, 1)
            xiuxian_impart.update_stone_num(5, player_1, 1)
            player_2_stones += 10
            player_1_stones += 5
            msg_list.append(
                {"type": "node", "data": {"name": f"虚神界战报", "uin": bot.self_id,
                                          "content": f"道友{player_2_name}获得了胜利,获得了思恋结晶10颗!\n"
                                                     f"道友{player_1_name}获得败了,消耗一次次数,获得了思恋结晶5颗!"}})
            if impart_pk.find_user_data(player_1)["pk_num"] <= 0:
                msg_list.append(
                    {"type": "node", "data": {"name": f"虚神界变更", "uin": bot.self_id,
                                              "content": f"道友{player_1_name}次数耗尽，离开了虚神界！"}})
                xu_world.del_xu_world(player_1)
                combined_msg += "\n".join([node['data']['content'] for node in msg_list])
                break

        combined_msg += f"☆------------第{duel_count}次------------☆\n" + "\n".join([node['data']['content'] for node in msg_list]) + "\n"

        try:
            await send_msg_handler(bot, event, msg_list)
        except ActionFailed:
            msg = "未知原因，对决显示失败!"
            combined_msg += f"{msg}\n"
            break

        user_data = impart_pk.find_user_data(user_info['user_id'])

    combined_msg += f"总计：道友{player_1_name}获得思恋结晶{player_1_stones}颗, 道友{player_2_name}获得思恋结晶{player_2_stones}颗\n"

    if XiuConfig().img:
        pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + combined_msg)
        await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
    else:
        await bot.send_group_msg(group_id=int(send_group_id), message=combined_msg)

    await impart_pk_now.finish()


@impart_pk_exp.handle(parameterless=[Cooldown(at_sender=False)])
async def impart_pk_exp_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """虚神界修炼"""
    bot, send_group_id = await assign_bot(bot=bot, event=event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
    user_id = user_info['user_id']
    impart_data_draw = await impart_pk_check(user_id)
    if impart_data_draw is None:
        msg = "发生未知错误，多次尝试无果请找晓楠！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
    level = user_info['level']
    hp_speed = 25
    mp_speed = 50

    impaer_exp_time = args.extract_plain_text().strip()
    if not impaer_exp_time.isdigit():
        msg = "输入解析异常，应全为数字!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
    if int(impaer_exp_time) > int(impart_data_draw['exp_day']):
        msg = "累计时间不足，修炼失败!"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
    # 闭关时长计算(分钟)
    level_rate = sql_message.get_root_rate(user_info['root_type'])  # 灵根倍率
    realm_rate = jsondata.level_data()[level]["spend"]  # 境界倍率
    user_buff_data = UserBuffDate(user_id)
    mainbuffdata = user_buff_data.get_user_main_buff_data()
    mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata is not None else 0  # 功法修炼倍率
    mainbuffcloexp = mainbuffdata['clo_exp'] if mainbuffdata != None else 0  # 功法闭关经验
    mainbuffclors = mainbuffdata['clo_rs'] if mainbuffdata != None else 0  # 功法闭关回复
    exp = int((int(impaer_exp_time) * XiuConfig().closing_exp) * ((level_rate * realm_rate * (1 + mainbuffratebuff) * (1 + mainbuffcloexp))))  # 本次闭关获取的修为
    max_exp = int((int(OtherSet().set_closing_type(user_info['level'])) * XiuConfig().closing_exp_upper_limit))  # 获取下个境界需要的修为 * 1.5为闭关上限
    if 0 < int(user_info['exp'] + exp) < max_exp:
        xiuxian_impart.use_impart_exp_day(impaer_exp_time, user_id)
        sql_message.update_exp(user_id, exp)
        sql_message.update_power2(user_id)  # 更新战力
        result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed * (1 + mainbuffclors)), int(exp * mp_speed))
        sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1], int(result_hp_mp[2] / 10))
        msg = "虚神界修炼结束，共修炼{}分钟，本次闭关增加修为：{}{}{}".format(impaer_exp_time, exp, result_msg[0],
                                                       result_msg[1])
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
    else:
        msg = "修炼时长过长导致超出上限，此次修炼失败！"
        if XiuConfig().img:
            pic = await get_msg_pic("@{}\n".format(event.sender.nickname) + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await impart_pk_exp.finish()
 
        
