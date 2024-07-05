import os
import sys
import ssl
import argparse
import transforms
import maltego_trx.maltego

from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app
from maltego_trx.handler import handle_run
from opencti.config import global_registry  # make sure to copy config.py to opencti folder

register_transform_classes(transforms)

if '--generate-config' in sys.argv:
    global_registry.write_transforms_config(config_path="output/transforms.csv")
    global_registry.write_settings_config(config_path="output/settings.csv")
    global_registry.write_local_mtz(mtz_path="output/local.mtz")
    print("Configuration files generated successfully")
    sys.exit(0)

maltego_trx.maltego.DISP_INFO_TEMPLATE = "<Label Name=\"%(name)s\" Type=\"text/html\"><![CDATA[%(content)s]]></Label>"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=os.environ.get("PORT", 8080), type=int, help="Application port")
    parser.add_argument("--ssl", action="store_true", help="Enable SSL")
    args, unknown = parser.parse_known_args()

    ssl_context = None
    if args.ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('./cert.pem', './key.pem')

    handle_run(__name__, ["runserver"] + unknown, app, port=args.port, ssl_context=ssl_context)


if __name__ == "__main__":
    main()
