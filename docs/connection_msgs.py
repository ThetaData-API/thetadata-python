from datetime import date

from thetadata import ThetaClient, OptionRight, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    client.connect_stream(callback)  # You can stop streaming by calling client.close_stream
    client.req_full_trade_stream_opt()  # Subscribes to every option trade.


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    if msg.type == StreamMsgType.DISCONNECTED:
        print('Lost connection to Theta Data servers')
    if msg.type == StreamMsgType.STREAM_DEAD:
        print('Lost connection to Theta Terminal, which is likely due the terminal being forcibly closed')
    if msg.type == StreamMsgType.RECONNECTED:
        print('The terminal has reconnected to Theta Data. You need to resubscribe to all streams.')


if __name__ == "__main__":
    streaming()
