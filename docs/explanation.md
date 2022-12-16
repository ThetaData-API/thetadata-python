# Explanation

This part of the documentation focuses on an
**understanding-oriented** approach. You'll get a
chance to read about the background of the project,
as well as reasoning about how it was implemented.

## The Theta Terminal

The **Theta Terminal** is an intermediate layer that bridges our data
providing server with the Python API. The terminal runs as a background
process. It hosts a local server on your machine, to which the Python API connects.

When you make a request using the Python API:

- The API forwards the request to the Terminal (background process launched by the API).
- The Terminal then forwards your request to the nearest thetadata MDDS (market data distribution server) and awaits a response.
- The Terminal interprets the response and forwards the result to your Python application.
- The Python API then parses the response header and body into a digestible format.

This intermediate-application approach has several benefits, but its most significant
is that it separates data processing (i.e. decompression) with
language-specific API features.
