#!/bin/bash
kill $(cat /tmp/tutor-agent.pid 2>/dev/null) 2>/dev/null && echo "Agent stopped" || echo "Agent not running"
kill $(cat /tmp/tutor-ui.pid 2>/dev/null) 2>/dev/null && echo "UI stopped" || echo "UI not running"
kill $(cat /tmp/tutor-proxy.pid 2>/dev/null) 2>/dev/null && echo "Proxy stopped" || echo "Proxy not running"
rm -f /tmp/tutor-agent.pid /tmp/tutor-ui.pid /tmp/tutor-proxy.pid
