import requests
from asgiref.sync import sync_to_async

from config.settings import CHECK_TOKEN, CHECK_LOGGER as log


class ProverkachekaInterface:
    token = CHECK_TOKEN

    def __get_filtered_data(self, data):
        """
        Получает из данных только name, quantity и operationType
        """
        res = {
            'name': '',
            'quantity': 0,
            'operationType': 0,
            'qr_raw': 0,
        }
        try:
            res['name'] = data.get('data').get('json').get('items')[0].get('name').lower()
        except Exception as err:
            log.error(err)
        try:
            res['quantity'] = data.get('data').get('json').get('items')[0].get('quantity')
        except Exception as err:
            log.error(err)
        try:
            res['operationType'] = data.get('data').get('json').get('operationType')
        except Exception as err:
            log.error(err)
        try:
            res['qr_raw'] = data.get('request').get('qrraw')
        except Exception as err:
            log.error(err)
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
        log.info('Отправка запроса в API')
        try:
            response = requests.post(url, data=data)
            res = self.__get_filtered_data(response.json())
            return res
        except Exception as err:
            log.error(err)

    @sync_to_async
    def get_qr_by_photo(self, binary_photo):
        url = 'https://proverkacheka.com/api/v1/check/get'
        data = {'token': self.token}
        files = {'qrfile': binary_photo}
        response = requests.post(url, data=data, files=files)
        response = response.json()
        res = self.__get_filtered_data(response)
        try:
            code = response.get('code')
            return res, code
        except Exception as err:
            log.error(err)
            return res, 0

#
# test = ProverkachekaInterface()
# print(test.send_raw_data('t=20230703T1143&s=650.00&fn=7284440500054890&i=917&fp=28742411&n=1'))
