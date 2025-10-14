# proto-public-api

Provides the WebSocket API for controlling all kinds of robots.

All messages should be Binary. Text messages will be treated as errors. All messages from the robot is type APIUp. All messages sent to the robot must be type APIDown.

You can expect the server to be running on port 8439.
