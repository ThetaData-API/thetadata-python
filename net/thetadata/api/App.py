from net.thetadata.api.io.tclient import ThetaClient
from net.thetadata.api.types.ReqArg import ReqArg
from net.thetadata.api.types.ReqType import ReqType

if __name__ == "__main__":
    client = ThetaClient()
    client.connect()

    # print(client.req(MessageType.HIST, "req=101&sec=EQUITY&root=AAPL&interval=1&dur=1"))
    test = client.req_get_hist_opts(ReqType.GREEKS, "AAPL", "20220211", 162.5, "C", 1, 0)

    for i in range(20):
        print("test: " + str(test[i]))
