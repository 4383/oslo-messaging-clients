#!/usr/bin/env python
#
import optparse, sys, time

from oslo.config import cfg
from oslo import messaging

class TestEndpoint01(object):
    def __init__(self, server, target=None):
        self.server = server
        self.target = target

    def methodA(self, ctx, **args):
        print("%s::TestEndpoint01::methodA( ctxt=%s arg=%s ) called!!!"
              % (self.server, str(ctx),str(args)))
    def common(self, ctx, **args):
        print("%s::TestEndpoint01::common( ctxt=%s arg=%s ) called!!!"
              % (self.server, str(ctx),str(args)))

class TestEndpoint02(object):
    def __init__(self, server, target=None):
        self.server = server
        self.target = target

    def methodB(self, ctx, **args):
        print("%s::TestEndpoint02::methodB( ctxt=%s arg=%s ) called!!!"
              % (self.server, str(ctx),str(args)))
        return ctx
    def common(self, ctx, **args):
        print("%s::TestEndpoint02::common( ctxt=%s arg=%s ) called!!!"
              % (self.server, str(ctx),str(args)))


def main(argv=None):

    _usage = """Usage: %prog [options]"""
    parser = optparse.OptionParser(usage=_usage)
    parser.add_option("--exchange", action="store", default="my-exchange")
    parser.add_option("--topic", action="store", default="my-topic")
    parser.add_option("--server", action="store", default="my-server-name")
    parser.add_option("--namespace", action="store", default="my-namespace")
    parser.add_option("--version", action="store", default="1.1")
    parser.add_option("--eventlet", action="store_true")

    opts, extra = parser.parse_args(args=argv)
    print "Running server, name=%s exchange=%s topic=%s namespace=%s" % (
        opts.server, opts.exchange, opts.topic, opts.namespace)

    transport = messaging.get_transport(cfg.CONF, url="qpid://localhost:5672")

    target = messaging.Target(exchange=opts.exchange,
                              topic=opts.topic,
                              namespace=opts.namespace,
                              server=opts.server,
                              version=opts.version)

    endpoints = [
        TestEndpoint01(opts.server, target),
        TestEndpoint02(opts.server, target),
        ]
    server = messaging.get_rpc_server(transport, target, endpoints,
                                      executor='eventlet' if opts.eventlet else 'blocking')

    try:
        server.start()
        while True:
            time.sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("Stopping..")
        server.stop()
        server.wait()
    return 0

if __name__ == "__main__":
    sys.exit(main())
