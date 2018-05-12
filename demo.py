# coding=utf-8
import datetime
import logging

import requests

import settings


class User(object):
    def __init__(self, api_key, name, mobile):
        self.api_key = api_key
        self.name = name
        self.mobile = mobile


class RescueTime(object):

    MAX_ROWS = 10

    def __init__(self, user, webhook):
        self.user = user
        self.webhook = webhook

    def send_message(self):
        result = requests.post(
            self.webhook,
            json=dict(
                msgtype="markdown",
                markdown=dict(
                    title=self.user.name,
                    text=self.message,
                ),
                at=dict(
                    atMobiles=[
                        self.user.mobile,
                    ],
                    isAtAll=False,
                ),
            ),
        )

    @property
    def message(self):
        data = self.data
        rows = data['rows']

        message = "#### {} @{}\n\n".format(self.user.name, self.user.mobile)

        rows = list(filter(lambda row: row[5] > 0, rows))

        for row in rows[:self.MAX_ROWS]:
            rank, time_spent, _, activity, category, productivity = row
            message += "- {} {:.2f}小时\n".format(activity, time_spent / 3600.0)

        return message

    @property
    def interval(self):
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        return yesterday, today

    @property
    def data(self):
        begin, end = self.interval
        result = requests.get(
            "https://www.rescuetime.com/anapi/data?key={api_key}&format=json&restrict_begin={begin}&restrict_end={end}".format(
                api_key=self.user.api_key,
                begin=begin.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
            )
        )
        return result.json()


def main():
    for _, user_info in settings.USER_DICT.items():
        user = User(user_info['api_key'], user_info['name'], user_info["mobile"])
        rescue_time = RescueTime(user, settings.WEB_HOOK)
        try:
            rescue_time.send_message()
        except:
            logging.exception('Got exception on main')


if __name__ == "__main__":
    main()
