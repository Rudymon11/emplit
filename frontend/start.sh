#!/bin/bash
export HOST=0.0.0.0
export PORT=3000
export DANGEROUSLY_DISABLE_HOST_CHECK=true
export WDS_SOCKET_HOST=0.0.0.0
export WDS_SOCKET_PORT=0

yarn start --host 0.0.0.0 --disable-host-check