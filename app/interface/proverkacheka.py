from typing import Tuple

import requests
from asgiref.sync import sync_to_async

from applications.tokens.models import Token
from config.settings import CHECK_LOGGER as log


class ProverkachekaInterface:
    def __get_filtered_data(self, data) -> Tuple[str, int, list]:
        """
        Получает из данных только name, quantity и operationType
        """
        product_list = []
        qr_raw = None
        operation_type = None
        try:
            items = data.get('data').get('json').get('items')
        except Exception as err:
            log.warning(err)
            items = []
        try:
            operation_type = int(data.get('data').get('json').get('operationType'))
        except Exception as err:
            log.warning(err)
        try:
            qr_raw = data.get('request').get('qrraw')
        except Exception as err:
            log.warning(err)
        for product in items:
            try:
                try:
                    gtin = product.get('productCodeNew').get('kmk').get('gtin')
                except Exception as err:
                    log.warning(err)
                    gtin = None
                product_list.append({
                    'name': product.get('name').lower(),
                    'quantity': int(product.get('quantity')),
                    'price': float(product.get('price')),
                    'gtin': gtin,
                })
            except Exception as err:
                log.warning(err)
        return qr_raw, operation_type, product_list

    @sync_to_async
    def send_raw_data(self, qr_code):
        """
        Отправляет сырые данные
        :param qr_code: пример t=20220318T1850&s=1000.00&fn=9961440300195301&i=871&fp=1470707772&n=1
        :return:
        """
        url = f"https://proverkacheka.com/api/v1/check/get"
        token = Token.objects.all().order_by('-created_at')[0]
        data = {
            'qrraw': qr_code,
            'token': token
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
        token = Token.objects.all().order_by('-created_at')[0]
        data = {'token': token}
        files = {'qrfile': binary_photo}
        response = requests.post(url, data=data, files=files)
        response = response.json()
        qr_raw, operation_type, product_list = self.__get_filtered_data(response)
        try:
            code = response.get('code')
            return qr_raw, operation_type, product_list, code
        except Exception as err:
            log.error(err)
            return qr_raw, operation_type, product_list, 0


#
# test = ProverkachekaInterface()
# print(test.send_raw_data('t=20230629t1821&s=2000.00&fn=7284440500054890&i=882&fp=4112580178&n=1'))
