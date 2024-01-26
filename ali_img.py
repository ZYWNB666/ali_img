import datetime

import dashscope
import json
import re

import requests

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *



@plugins.register(
    name="ali_img",
    desire_priority=98,
    hidden=True,
    desc="阿里云作图插件",
    version="0.2",
    author="lanvent",
)
class ali_img(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[chajian] inited")
        self.config = super().load_config()

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        reply = None
        query = e_context["context"].content.strip()
        # print(query + '111111111111111111111')
        if query.startswith("画"):
            if os.path.exists('config.json'):
                config_path = os.path.join(os.path.dirname(__file__), "config.json")
                with open(config_path, 'r') as file:
                    config_data = json.load(file)
                apikey = config_data['apikey']
                # print(apikey)
            else:
                text = "请先配置config.json文件，apikey需要从阿里云的通义平台获取"
                reply = Reply(ReplyType.ERROR, text)
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            if query:
                api_key = apikey
                if api_key:
                    dashscope.api_key = api_key
                    sizes = {
                        '横版': '1280*720',
                        '竖版': '720*1280',
                        '正方形': '1024*1024'
                    } 
                    chosen_size = '1024*1024'
                    pattern = re.compile(r'[:：](.*)$')
                    match = pattern.search(query)
                    if match:
                        size_word = match.group(1).strip()  # 从匹配的字符串中提取词
                        if size_word in sizes:
                            chosen_size = sizes[size_word]
                            # 从query中删除尺寸
                            query = query.replace(':'+size_word, '')
                            query = query.replace('：'+size_word, '')
                    rsp = dashscope.ImageSynthesis.call(model=dashscope.ImageSynthesis.Models.wanx_v1,
                                                        prompt=query,
                                                        n=1,
                                                        size=chosen_size)
                    img_url = rsp.output['results'][0]['url']
                    pic_res = requests.get(img_url, stream=True)
                    if pic_res.status_code != 200:
                        text = (f"请求失败，状态码：{pic_res.status_code}!")
                        print(text)
                        reply = Reply(ReplyType.ERROR, text)
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS
                    reply = Reply(ReplyType.IMAGE_URL, img_url)
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
    def get_help_text(self, **kwargs):
        help_text = "使用方法:\n识别以画开头的语句,比如:\n画一只小猫的素描画\n使用时请把系统配置文件中识别画的那条配置去掉，否则本插件失效"
        return help_text
