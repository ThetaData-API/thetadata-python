from thetadata import ThetaClient, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    client.connect_stream(callback)  # You can stop streaming by calling client.close_stream
    client.req_full_open_interest_stream()  # requests every option open interest update


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    msg.type = msg.type

    if msg.type == StreamMsgType.OPEN_INTEREST:
        print('con:' + msg.contract.to_string() + ' open_interest: ' + msg.open_interest.to_string())


if __name__ == "__main__":
    streaming()
