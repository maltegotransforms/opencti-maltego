import os

from maltego_trx.decorator_registry import TransformRegistry, TransformSetting

HOST_URL = os.environ.get("HOST_URL", "https://localhost:8088")

opencti_url_setting = TransformSetting('opencti_url', 'OpenCTI URL', setting_type='string', default_value="",
                                       popup=True)
opencti_token_setting = TransformSetting('opencti_token', 'OpenCTI Token', setting_type='string',
                                         default_value="", popup=True)
ssl_verify_setting = TransformSetting('opencti_ssl_verify', 'SSL Verify', setting_type='boolean', default_value="false",
                                      popup=False)
http_proxies_setting = TransformSetting('opencti_http_proxies', 'HTTP Proxies', setting_type='string', optional=True,
                                        popup=False)

global_settings = [
    opencti_url_setting,
    opencti_token_setting,
    ssl_verify_setting,
    http_proxies_setting
]

global_registry = TransformRegistry(owner='Maltego Technologies GmbH - OpenCTI GitHub',
                                    author='Maltego Technologies GmbH - OpenCTI GitHub',
                                    host_url=HOST_URL,
                                    seed_ids=['opencti'],
                                    global_settings=global_settings)
