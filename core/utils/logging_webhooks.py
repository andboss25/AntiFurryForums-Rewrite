"""Discord Webhook util"""

import requests

try:
    from core.utils import config
except ModuleNotFoundError:
    import config

config_loader = config.ConfigSet()


class WebhookSet:
    """A class to utilize discord webhooks"""

    api_config_file_path = config_loader.api_config_file_path
    main_config_file_path = config_loader.main_config_file_path

    webhooks_enabled = config_loader.get_value(
        main_config_file_path, "external-apis.webhooks"
    )


class Webhook:
    """A discord webhook"""

    def __init__(self, webhook_type):
        if not WebhookSet.webhooks_enabled:
            return
        self.url = config_loader.get_value(
            config_loader.api_config_file_path, f"webhooks.{webhook_type}"
        )

        if self.url is None:
            raise Exception(f"No such webhook {webhook_type}")

    def log_action(self, message: str):
        """Send a message using the webhook"""
        if not WebhookSet.webhooks_enabled:
            return

        inital_request = requests.get(self.url)

        if inital_request.status_code != 200:
            raise Exception("Invalid webhook url provided!")

        message_request = requests.post(self.url, data={"content": message})

        if not str(message_request.status_code).startswith("2"):
            raise Exception("Webhook did not send the message!")


available_webhooks = {
    "general": Webhook("general"),
    "testing": Webhook("testing"),
    "security": Webhook("security"),
}

if __name__ == "__main__":
    print("Testing all webhooks...")

    if WebhookSet.webhooks_enabled:
        for webhook in available_webhooks:
            print(f"Testing '{webhook}' webhook...")
            available_webhooks[webhook].log_action(
                "## This is a test!\n"
                "### If you are seeing this then the webhook is configured!"
            )
            print(f" - '{webhook}' works!")
    else:
        print("Webhooks are disabled!")
