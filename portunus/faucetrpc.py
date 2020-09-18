
def get_faucetconfrpc(key, cert, ca, server, port):
    # TODO: FaucetConfRpcClient's use of the C YAML parser causes pytest-cov to fail to report any coverage.
    from faucetconfrpc.faucetconfrpc_client_lib import FaucetConfRpcClient
    return FaucetConfRpcClient(key, cert, ca, ':'.join((server, port)))
