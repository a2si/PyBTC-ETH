from coins import Bitcoin, Ethereum
from japronto import Application
from simplejson.errors import JSONDecodeError


crypto = {
    'btc': Bitcoin(),
    'eth': Ethereum()
}


app = Application()
r = app.router


def start_page(request):
    return request.Response(
        text="/balance - for check address balance. Open for more detalis\n" +
        "/generate - for generate address. Open for more detalis\n" +
        "/validate - for validate address. Open for more detalis"
    )


def balance_info(request):
    return request.Response(
        text="/balance/%SYSTEM%/%ADDRESS%\n" +
        "%SYSTEM% - btc or eth\n" +
        "%ADDRESS% - crypto-address of selected system"
    )


def generate_info(request):
    return request.Response(
        text="/generate/%SYSTEM%\n" +
        r"%SYSTEM% - btc or eth"
    )


def validate_info(request):
    return request.Response(
        text="/validate/%SYSTEM%/%ADDRESS%\n" +
        "%SYSTEM% - btc or eth\n" +
        "%ADDRESS% - crypto-address of selected system"
    )


def balance(request):
    sys = request.match_dict['system']
    addr = request.match_dict['address']

    if sys not in crypto:
        return balance_info(request)

    try:
        resp = crypto[sys].balance(addr)

        return request.Response(json={
            'balance': resp
        })
    except (JSONDecodeError, TypeError):
        return request.Response(
            text="Invalid address"
        )


def generator(request):
    sys = request.match_dict['system']

    if sys not in crypto:
        return generate_info(request)

    resp = crypto[sys].gen()

    return request.Response(json={
        'address': resp[0],
        'privkey': resp[1]
    })


def valid(request):
    sys = request.match_dict['system']
    addr = request.match_dict['address']

    if sys not in crypto:
        return validate_info(request)

    return request.Response(json={
        'valid': crypto[sys].valid(addr)
    })


r.add_route('/', start_page, 'GET')
r.add_route('/generate', generate_info, 'GET')
r.add_route('/validate', validate_info, 'GET')
r.add_route('/balance', balance_info, 'GET')
r.add_route('/generate/{system}', generator, 'GET')
r.add_route('/balance/{system}/{address}', balance, 'GET')
r.add_route('/validate/{system}/{address}', valid, 'GET')


if __name__ == "__main__":
    app.run()
