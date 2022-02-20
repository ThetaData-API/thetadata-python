import decimal
import json
import socket
import threading
import time
from json import JSONDecoder

from net.thetadata.api.types.MessageType import MessageType
from net.thetadata.api.types.ReqArg import ReqArg
from net.thetadata.api.types.ReqType import ReqType
from net.thetadata.api.types.RequestException import RequestException


class ThetaClient(threading.Thread):
    """
    A Python Implementation of the Theta Data Socket API. This class
    provides a means for easily accessing market data. There are two
    types of methods for accessing / requesting data:

    Blocking - Sends a request and blocks for a specified period of time
    or until a response is received. All blocking method names begin
    with "reqGet" such as ThetaClient#reqGetHistOpts(...).

    Non-Blocking - Sends a request without waiting for a response.
    All non-blocking method names begin with "req" such as
    ThetaClient#reqHistOpts(...). The response can be retrieved
    from the internal data cache by calling the corresponding
    method that's name explicitly begins with "get"
    such as ThetaClient#getHistBars(...).

    The internal data cache does not clear itself automatically. Calling
    ThetaClient#clear() will clear the cache completely. This is
    especially important for a production setting where the API may not
    be restarted and the cache size will grow indefinitely. There is no
    limit to the cache size aside from the JVM memory allocation.

    Retrieving data after making a non-blocking request is as simple as
    calling the corresponding "get" method with the request id that was
    returned by the "req" method.

    :author: Bailey Danseglio
    :version: 2.0.2
    :since: 1/15/2022
    """

    req_id = 0
    ping_msg = (ReqArg.ID.name + "=-1&" + ReqArg.MSG_CODE.name +
                "=" + str(MessageType.PING.code) + "\n").encode("utf-8")
    server: socket
    data = dict()

    def connect(self, port=11000):
        """
        :param port: The port number specified in the Theta Terminal config.
        :raises ConnectionError: If there was a failure in establishing the connection.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect(("localhost", port))
        self.start()

    # Internal Processing

    def run(self):
        while True:
            try:
                self.process_message(self.read())
            except ConnectionError:
                print("The connection to the Theta Terminal has been closed.")
                return
            except Exception as e:
                print(e.__cause__)
                print("ERROR: " + e.with_traceback())

    def read(self):
        data = [self.server.recv(1).decode("utf-8")]
        brackets = 1
        while brackets > 0:
            t = self.server.recv(1).decode("utf-8")
            if t.__eq__("{"):
                brackets = brackets + 1
            elif t.__eq__("}"):
                brackets = brackets - 1
            data.append(t)
        return json.JSONDecoder.decode(JSONDecoder(), ''.join(data))

    def ping(self):
        self.server.send(self.ping_msg)

    def process_message(self, cb: json):
        req = int(cb[ReqArg.ID.name])
        msg = MessageType(int(cb[ReqArg.MSG_CODE.name]))

        if msg == MessageType.PING:
            self.ping()
        elif msg == MessageType.ALL_STRIKES:
            values = msg["payload"].split(",")
            strikes = []

            for s in values:
                strikes.append(decimal.Decimal(s))

            self.data[req] = strikes
        elif msg == MessageType.ALL_EXPIRATIONS:
            self.data[req] = msg["payload"].split(",")
        elif msg == MessageType.ERROR:
            self.data[req] = RequestException(cb["payload"])
            self.on_err(req, RequestException(cb["payload"]))
        elif msg == MessageType.HIST:
            self.data[req] = cb["payload"]
            self.on_historical_bars(req, cb["payload"])
        elif msg == MessageType.DISCONNECTED:
            self.on_disconnect()
        elif msg == MessageType.RECONNECTED:
            self.on_reconnect()

    # BLOCKING HISTORICAL DATA

    def req_get_hist_opts(self, req: ReqType, root: str, exp: str, strike: decimal, right: chr, interval: int,
                          dur: int = None, start: str = None, end: str = None):
        """
        Sends a historical option data request and blocks for 2000 ms
        or until a response is received. The start date for the request
        is calculated by subtracting the duration from the current date.
        A 10-day duration request's start date will be 20220105 if the
        current date is 20220115. Only providing a duration will use the
        current date as the start date.

        :param req:      The request type.
        :param root:     The root symbol.
        :param exp:      The expiration date formatted as YYYYMMDD.
        :param strike:   The strike.
        :param right:    'C' for call; 'P' for put.
        :param interval: Interval size in minutes.
        :param dur:      The duration in days.
        :param start:    The start date formatted as YYYYMMDD.
        :param end:      The end date formatted as YYYYMMDD.
        :return: The requested data; None if the request timed out.
        :raises RequestException: If an error occurred while processing the request.
        """

        out = [ReqArg.REQ.name + "=" + str(req.code) + "&", ReqArg.SEC_TYPE.name + "=OPTION&",
               ReqArg.ROOT.name + "=" + root + "&", ReqArg.EXPIRATION.name + "=" + exp + "&",
               ReqArg.STRIKE.name + "=" + str(strike) + "&", ReqArg.RIGHT.name + "=" + right + "&",
               ReqArg.INTERVAL_SIZE.name + "=" + str(interval)]

        if dur is not None:
            out.append("&" + ReqArg.DURATION.name + "=" + str(dur))
        if start is not None:
            out.append("&" + ReqArg.START_DATE.name + "=" + start)
        if end is not None:
            out.append("&" + ReqArg.END_DATE.name + "=" + dur)
        print(''.join(out))
        return self.get(self.req(MessageType.HIST, ''.join(out)))

    # NON-BLOCKING HISTORICAL DATA

    def req_hist_opts(self, req: ReqType, root: str, exp: str, strike: decimal, right: chr, interval: int,
                      dur: int = None, start: str = None, end: str = None):
        """
        Sends a historical option data request. The start date for the request
        is calculated by subtracting the duration from the current date.
        A 10-day duration request's start date will be 20220105 if the
        current date is 20220115. Only providing a duration will use the
        current date as the start date.

        :param req:      The request type.
        :param root:     The root symbol.
        :param exp:      The expiration date formatted as YYYYMMDD.
        :param strike:   The strike.
        :param right:    'C' for call; 'P' for put.
        :param interval: Interval size in minutes.
        :param dur:      The duration in days.
        :param start:    The start date formatted as YYYYMMDD.
        :param end:      The end date formatted as YYYYMMDD.
        :return: The request id.
        :raises RequestException: If an error occurred while processing the request.
        """

        out = [ReqArg.REQ.name + "=" + str(req.code) + "&", ReqArg.SEC_TYPE.name + "=OPTION&",
               ReqArg.ROOT.name + "=" + root + "&", ReqArg.EXPIRATION.name + "=" + exp + "&",
               ReqArg.STRIKE.name + "=" + str(strike) + "&", ReqArg.RIGHT.name + "=" + right + "&",
               ReqArg.INTERVAL_SIZE.name + "=" + str(interval)]

        if dur is not None:
            out.append("&" + ReqArg.DURATION.name + "=" + str(dur))
        if start is not None:
            out.append("&" + ReqArg.START_DATE.name + "=" + start)
        if end is not None:
            out.append("&" + ReqArg.END_DATE.name + "=" + dur)
        print(''.join(out))
        return self.req(MessageType.HIST, ''.join(out))

    # CACHE RETRIEVAL

    def get(self, req_id, timeout=2000):
        """
        Blocks for a specified amount of time or until the response
        for a specified request id is available in the cache.
        :param req_id: The request id.
        :param timeout: The time to wait for the response in milliseconds.
        :return: The response for the specified id or None if the request timed out.
        :raises RequestException: If an error occurred while processing the request.
        """
        for i in range(int(timeout / 5)):
            if self.data.get(req_id) is not None:
                if isinstance(self.data.get(req_id), RequestException):
                    raise self.data.get(req_id)
                return self.data.get(req_id)
            time.sleep(.005)
        return None

    # LISTING DATA

    def req_get_all_expirations(self, root: str):
        """
        Sends a listing request and blocks for 2000ms or until a response
        is received.

        :param root: The root symbol.
        :return: All expirations that Theta Data provides data for (YYYYMMDD) or None is the request timed out.
        :raises RequestException: If an error occurred while processing the request.
        """
        req_id = self.req(MessageType.ALL_STRIKES, ReqArg.ROOT + "=" + root)
        return self.get(req_id)

    def req_get_all_strikes(self, root: str, exp: str):
        """
        Sends a listing request and blocks for 2000ms or until a response
        is received.

        :param root: The root symbol.
        :param exp: The expiration date (YYYYMMDD).
        :return: The strike prices on the expiration or None is the request timed out.
        :raises RequestException: If an error occurred while processing the request.
        """
        req_id = self.req(MessageType.ALL_STRIKES, ReqArg.ROOT + "=" + root + "&" + ReqArg.EXPIRATION + "=" + exp)
        return self.get(req_id)

    # LOW LEVEL IO

    def req(self, msg: MessageType, args: str):
        """
        Sends a request. Each argument should adhere
        to the following format conventions.

        1. There should be no spaces.
        2. An argument field and its corresponding value are separated by '='.
        3. Use ReqArg to get the argument field
        4. Argument field-value pairings should be separated by '&'.

        An example:

        req(MessageType.ALL_STRIKES, ReqArg.ROOT + "=AAPL&" + ReqArg.EXPIRATION + "=20220121");

        :param msg: The MessageType.
        :param args: The arguments formatted as field=value and separated by '&'
        :return: The request id.
        """
        req = self.req_id
        self.req_id += 1
        out = ReqArg.ID.name + "=" + str(req) + '&' + ReqArg.MSG_CODE.name + "=" + str(msg.code) + "&" + args + "\n"
        self.server.send(out.encode("utf-8"))
        return req

    def on_historical_bars(self, req_id, bars):
        """
        Called every time there is a historical data callback.

        :param req_id: The original request id.
        :param bars: The historical data.
        """

    def on_err(self, req_id, err):
        """
        Called every time there is an error in relation to a request.
        It is recommended that this method is overridden for production.

        :param req_id: The original request id.
        :param err: The error.
        """
        print("ERROR: reqId: " + req_id + " message: " + err)

    def on_disconnect(self):
        """
        Called when a connection is lost between the Theta Terminal
        and Theta Data servers, not a loss of connection between this API
        and the Theta Terminal. It is recommended that this method is
        overridden for production.
        """
        print("Connection lost. Implement ThetaClient#disconnected() to handle this.")

    def on_reconnect(self):
        """
        Called when the connection is regained between the Theta Terminal
        and Theta Data servers. It is recommended that this method is
        overridden for production.
        """
        print("Reconnected. Implement ThetaClient#reconnected() to handle this.")
