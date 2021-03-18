import sys
import transforms
import maltego_trx.maltego

from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app
from maltego_trx.handler import handle_run

register_transform_classes(transforms)

# just a hotfix until upstream adjusts this
maltego_trx.maltego.DISP_INFO_TEMPLATE = "<Label Name=\"%(name)s\" Type=\"text/html\"><![CDATA[%(content)s]]></Label>"

handle_run(__name__, sys.argv, app, port=8080)
