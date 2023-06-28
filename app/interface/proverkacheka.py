import asyncio

import requests
from asgiref.sync import sync_to_async

from config.settings import CHECK_TOKEN


class ProverkachekaInterface:
    token = CHECK_TOKEN

    def __get_filtered_data(self, data):
        """
        Получает из данных только name, quantity и operationType
        """
        res = {}
        res['name'] = data.get('data').get('json').get('items')[0].get('name')
        res['quantity'] = data.get('data').get('json').get('items')[0].get('quantity')
        res['operationType'] = data.get('data').get('json').get('operationType')
        return res

    @sync_to_async
    def send_raw_data(self, qr_code):
        """
        Отправляет сырые данные
        :param qr_code: пример t=20220318T1850&s=1000.00&fn=9961440300195301&i=871&fp=1470707772&n=1
        :return:
        """
        url = f"https://proverkacheka.com/api/v1/check/get"
        data = {
            'qrraw': qr_code,
            'token': self.token
        }
        response = requests.post(url, data=data)
        res = self.__get_filtered_data(response.json())
        return res
