from thetadata import ThetaClient, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    client.connect_stream(callback)  # You can stop streaming by calling client.close_stream
    client.req_full_trade_stream_opt()  # requests every option trade


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    msg.type = msg.type

    if msg.type == StreamMsgType.TRADE:
        print('---------------------------------------------------------------------------')
        print('con:                         ' + msg.contract.to_string())
        print('trade:                       ' + msg.trade.to_string())
        print('last quote at time of trade: ' + msg.quote.to_string())


if __name__ == "__main__":
    streaming()
