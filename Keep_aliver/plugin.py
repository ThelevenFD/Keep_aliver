import asyncio
from httpx import AsyncClient
from src.common.logger import get_logger
from src.plugin_system import register_plugin
from src.plugin_system.base.base_plugin import BasePlugin
from src.plugin_system.base.config_types import ConfigField

@register_plugin
class Plugin(BasePlugin):
    plugin_name = "keep_alive"
    enable_plugin = True
    dependencies = []
    python_dependencies = []
    config_file_name = "config.toml"
    config_schema: dict = {
        "plugin": {
            "name": ConfigField(type=str, default="keep_alive", description="插件名称"),
            "config_version": ConfigField(type=str, default="1.0.0", description="配置版本(不要修改 除非你知道自己在干什么)"),
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "keep_alive_url": ConfigField(type=str, default="http://127.0.0.1:8080/keep_alive", description="保活地址"),
            "timeout": ConfigField(type=int, default=10, description="超时时间(s)"),
            "interval": ConfigField(type=int, default=10, description="保活间隔(s)"),
    }
}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        global keep_alive_url, timeout, logger, interval
        logger = get_logger(self.plugin_name)
        keep_alive_url = self.get_config("plugin.keep_alive_url")
        timeout = self.get_config("plugin.timeout")
        interval = self.get_config("plugin.interval")

        if self.get_config("plugin.enabled"):
            asyncio.create_task(self.keep_alive())

    def get_plugin_components(self):
        return [
        ]

    async def keep_alive(self):
        """bot保活"""
        async with AsyncClient() as client:
            while True:
                try:
                    response = await client.get(keep_alive_url, timeout=timeout)
                    if response.status_code == 200:
                        logger.info("Keep Alive!!")
                    else:
                        logger.warning(f"Keep alive request failed with status: {response.status_code}")
                except TimeoutError as e:
                    logger.error(f"Keep alive request timeout: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(interval)