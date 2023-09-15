from thetadata import ThetaClient, StreamMsg, StreamMsgType, StreamResponseType


def streaming():
    # Credentials now required because streaming is only available to ThetaData Standard & Pro subscribers.
    client = ThetaClient(username="MyThetaDataEmail", passwd="MyThetaDataPassword")

    client.connect_stream(callback)  # You can stop streaming by calling client.close_stream
    req_id = client.req_full_trade_stream_opt()  # Requests every option trade (async).

    # Verify that the request to stream was successful.
    response = client.verify(req_id)
    if response == StreamResponseType.SUBSCRIBED:
        print('Request to stream full trades successful.')
    elif response == StreamResponseType.INVALID_PERMS:
        print('Invalid permissions to stream full trades. Theta Data Options Pro account required.')
    else:
        print('Unexpected stream response: ' + str(response))


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
