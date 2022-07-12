# Explanation

This part of the project documentation focuses on an
**understanding-oriented** approach. You'll get a
chance to read about the background of the project,
as well as reasoning about how it was implemented.

## The Theta Terminal

The **Theta Terminal** is an intermediate layer that bridges our data
providing server with the Python API. When you run the Terminal,
the application hosts a server on your machine, to which the Python API connects.

When you make a request using the Python API:

- The API forwards the request to the Terminal.
- The Terminal then forwards your request to the data server and awaits a response.
- The Terminal decompresses the response and forwards the result to your Python application.
- The Python API then parses the response header and body into a digestible format.

This intermediate-application approach has several benefits, but its most significant
is that it separates data processing (i.e. decompression) with
language-specific API features.


Please see the [Theta Terminal setup guide](https://www.thetadata.net/terminal-setup)
for installation instructions.
