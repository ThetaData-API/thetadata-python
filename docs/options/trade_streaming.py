from datetime import date
from thetadata import ThetaClient, OptionRight, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    with client.connect_stream(callback):
        client.req_trade_stream_opt("NVDA", date(2022, 12, 23), 150, OptionRight.CALL)
        client.req_trade_stream_opt("NVDA", date(2022, 12, 23), 150, OptionRight.PUT)
        client.req_trade_stream_opt("NVDA", date(2022, 12, 23), 145, OptionRight.CALL)
        client.req_trade_stream_opt("NVDA", date(2022, 12, 23), 145, OptionRight.PUT)


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    msg.type = msg.type

    if msg.type == StreamMsgType.TRADE:
        print('con:' + msg.contract.to_string())
        print('trade: ' + msg.trade.to_string())


if __name__ == "__main__":
    streaming()
