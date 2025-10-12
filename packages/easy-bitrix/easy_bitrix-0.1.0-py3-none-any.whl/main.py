import asyncio

from .bitrix import Bitrix24
from .options import RequestOptions
from .bitrix_objects import Deal, Contact
from .operations import FilterOperation, OrderOperations
from .oauth import OAuth

site_name = 'bitrix_portal'
user_id = '1'
webhook = 'webhook'
client_id = 'app.zzz'
client_secret = 'LJSl0lNB76B5YY6u0YVQ3AW0DrVADcRTwVr4y99PXU1BWQybWK'
code = 'avmocpghblyi01m3h42bljvqtyd19sw1'


def main():
    options = RequestOptions(user_id=user_id, webhook_url=webhook, high_level_domain='ru')
    bitrix = Bitrix24(bitrix_address=site_name)
    response = bitrix.request(param=Deal.get_list(
        select=[Deal.ID, Deal.TITLE, Deal.DATE_CREATE],
        filter=[FilterOperation.END_LIKE(Deal.SET_TITLE('_like'))],
        order=[OrderOperations.DESCENDING_ORDER(Deal.DATE_CREATE)],
        ), options=options)
    print(f'Status is: {response.code}\n\n\nResponse is: {response.data}')


main()
