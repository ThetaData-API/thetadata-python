from thetadata import ThetaClient, StreamMsg, StreamMsgType


def streaming():
    # Credentials now required because get_last is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    with client.connect_stream(callback):
        # requests every option open interest update
        client.req_full_open_interest_stream()


# User generated method that gets called each time a message from the stream arrives.
def callback(msg: StreamMsg):
    msg.type = msg.type

    if msg.type == StreamMsgType.OPEN_INTEREST:
        print('con:' + msg.contract.to_string() + ' open_interest: ' + msg.open_interest.to_string())


if __name__ == "__main__":
    streaming()
