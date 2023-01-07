from datetime import date

from thetadata import ThetaClient, OptionRight, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    client.connect_stream(callback)  # You can stop streaming by calling client.close_stream
    client.req_full_trade_stream_opt()  # Subscribes to every option trade.


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    if msg.type == StreamMsgType.DISCONNECTED or msg.type == StreamMsgType.RECONNECTED:
        print(msg.type.__str__())  # Handle disconnect / reconnect.


if __name__ == "__main__":
    streaming()
