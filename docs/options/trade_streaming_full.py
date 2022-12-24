from datetime import date
from thetadata import ThetaClient, OptionRight, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    with client.connect_stream(callback):
        # requests every option trade
        client.req_full_trade_stream_opt()


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    msg.type = msg.type

    if msg.type == StreamMsgType.TRADE:
        print('con:' + msg.contract.to_string())
        print('trade: ' + msg.trade.to_string())


if __name__ == "__main__":
    streaming()
