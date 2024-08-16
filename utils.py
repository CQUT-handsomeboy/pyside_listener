import os
import json


class ConfigLoader:
    def __init__(
        self,
        configs_filename: str = "configs.json",
        configs_items: tuple = (),
    ):
        self.configs_items = configs_items
        self.configs_filename = configs_filename

        self.load_configs()

    def load_configs(self):
        with open(self.configs_filename, "r", encoding="utf-8") as f:
            self.__configs = json.load(f)

        for item in self.configs_items:
            assert item in self.__configs, f"配置文件缺少必要项{item}"

        for key, value in self.__configs.items():
            setattr(self, key, value)


if __name__ == "__main__":
    configs = ConfigLoader()
    print(configs.sample_video_path)
