from net.thetadata.api.io.tclient import ThetaClient
from net.thetadata.api.types.ReqType import ReqType

if __name__ == "__main__":
    client = ThetaClient()
    client.connect()

    sym = 'SPCE'
    exp = '20220318'
    strike = 90
    interval = 60
    dur = 3

    ohlc = client.req_get_hist_opts(ReqType.OHLC, sym, exp, strike, 'C', interval, dur)
    quote = client.req_get_hist_opts(ReqType.QUOTE, sym, exp, strike, 'C', interval, dur)
    vol = client.req_get_hist_opts(ReqType.VOLUME, sym, exp, strike, 'C', interval, dur)
    # iv = client.req_get_hist_opts(ReqType.IMPLIED_VOLATILITY, sym, exp, strike, 'C', interval, dur)

    print(ohlc)
    print(quote)
    print(vol)
    # print(iv)

