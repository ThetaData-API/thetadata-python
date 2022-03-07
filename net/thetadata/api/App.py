from net.thetadata.api.io.tclient import ThetaClient
from net.thetadata.api.types.ReqType import ReqType

if __name__ == "__main__":
    client = ThetaClient()
    client.connect()

    #reqId = client.req_hist_opts(ReqType.QUOTE, "AMD", "20220520", 150, "C", 5, 900)
    #data = client.get(reqId)
    #for i in range(20):
    #    print("test: " + str(data[i]))
    print(client.req_get_last_opt_quote("AAPL", "20220318", 165, 'C'))
