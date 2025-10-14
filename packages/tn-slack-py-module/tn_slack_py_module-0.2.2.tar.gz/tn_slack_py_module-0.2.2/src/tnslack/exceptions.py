import logging
import re

from . import constants as slack_consts

logger = logging.getLogger("slack_app")


class TokenExpired(Exception):
    def __init__(self, message="Token Expired"):
        self.message = message
        super().__init__(self.message)


class ApiRateLimitExceeded(Exception):
    def __init__(self, message="Api Rate Limited"):
        self.message = message
        super().__init__(self.message)


class InvalidBlocksException(Exception):
    def __init__(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class InvalidBlocksFormatException(Exception):
    def __init__(self, message="Invalid Blocks Sent"):
        self.message = message
        super().__init__(self.message)


class UnHandeledBlocksException(Exception):
    def __init__(self, message="Error Generating Slack Modal"):
        self.message = message
        super().__init__(self.message)


class InvalidArgumentsException(Exception):
    def __init__(self, message="Error Generating Slack Modal"):
        self.message = message
        super().__init__(self.message)


class InvalidAccessToken(Exception):
    def __init__(self, message="Slack Token Invalid"):
        self.message = message
        super().__init__(self.message)


class InvalidUser(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class SlackAppException:
    def __init__(self, e, fn_name=None, retries=0, blocks=[]):
        self.error = e
        self.error_class_name = e.__class__.__name__
        self.code = e.args[0]["error_code"]
        self.param = e.args[0]["error_param"]
        self.message = e.args[0]["error_message"]
        self.blocks = blocks
        self.fn_name = fn_name
        self.retry_attempts = 0
        self.raise_error()

    def raise_error(self):
        # if an invalid Basic auth is sent the response is still a 200 success
        # instead we check data.json() which will return a JSONDecodeError
        if self.error_class_name == "JSONDecodeError":

            logger.error(f"{slack_consts.SLACK_ERROR} ---An error occured with a slack integration, {self.fn_name}")
            raise ValueError
        elif self.code == 401:
            raise TokenExpired()
        elif self.code == 403:
            raise ApiRateLimitExceeded()
        elif self.code == 200 and self.param == "invalid_blocks":
            # find the block_indexes
            blocks = [self._extract_block(error) for error in self.message]
            message = f"Invalid Blocks {'------'.join(blocks)}"
            logger.error(f"{slack_consts.SLACK_ERROR} ---An error occured building blocks {message}")
            raise InvalidBlocksException(message)
        elif self.code == 200 and self.param == "invalid_auth":
            logger.error(
                f"{slack_consts.SLACK_ERROR} ---An error occured with the access token this access token is org level {self.message}"
            )
            raise InvalidAccessToken(self.message)
        elif self.code == 200 and self.param == "invalid_blocks_format":
            logger.error(f"{slack_consts.SLACK_ERROR} An error occured building blocks because of an invalid format")
            raise InvalidBlocksFormatException(self.message)
        elif self.code == 200 and self.param == "invalid_arguments":

            logger.error(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
            raise InvalidArgumentsException(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
        elif self.code == 200 and self.param == "invalid_auth":

            logger.error(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
            raise InvalidAccessToken(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
        elif self.code == 200 and self.param == "user_not_found":

            logger.error(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
            raise InvalidUser(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
        else:
            # we may not have come accross this error yet
            logger.error(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")
            raise UnHandeledBlocksException(f"{slack_consts.SLACK_ERROR} ---{self.param}-{self.message}")

    def _extract_block(self, error):
        # regex to get [json-pointer:/blocks/0/text]
        matches = re.search(r"json-pointer:", error)
        if matches:
            block_index = int(error[matches.end() + 8])
            return f"{error[:matches.start()]} on block {self.blocks[block_index]}"
        return [error]
