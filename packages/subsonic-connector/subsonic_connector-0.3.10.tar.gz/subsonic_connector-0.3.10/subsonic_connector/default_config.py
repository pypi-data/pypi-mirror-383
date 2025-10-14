import libsonic
import os

from .configuration import ConfigurationInterface


class DefaultConfiguration(ConfigurationInterface):

    def __getParameter(self, name: str, default: str = None) -> str:
        return os.getenv(name, default)

    def getBaseUrl(self) -> str:
        return self.__getParameter("SUBSONIC_SERVER_URL")

    def getPort(self) -> str:
        return self.__getParameter("SUBSONIC_SERVER_PORT")

    def getServerPath(self) -> str:
        return self.__getParameter("SUBSONIC_SERVER_PATH")

    def getUserName(self) -> str:
        return self.__getParameter("SUBSONIC_USERNAME")

    def getPassword(self) -> str:
        return self.__getParameter("SUBSONIC_PASSWORD")

    def getLegacyAuth(self) -> bool:
        legacy_auth_enabled_str: str = self.__getParameter(
            name="SUBSONIC_LEGACY_AUTH")
        if not legacy_auth_enabled_str:
            legacy_auth_enabled_str = self.__getParameter(
                name="SUBSONIC_LEGACYAUTH")
        if not legacy_auth_enabled_str:
            legacy_auth_enabled_str = "false"
        if not legacy_auth_enabled_str.lower() in ['true', 'false']:
            raise Exception("Invalid value for "
                            f"SUBSONIC_LEGACY_AUTH [{legacy_auth_enabled_str}]")
        return legacy_auth_enabled_str == "true"

    def getSalt(self) -> str:
        return None

    def getToken(self) -> str:
        return None

    def getUserAgent(self) -> str:
        return self.__getParameter("SUBSONIC_USER_AGENT")

    def getApiVersion(self) -> str:
        return self.__getParameter(
            name="SUBSONIC_API_VERSION",
            default=libsonic.API_VERSION)

    def getAppName(self) -> str:
        return self.__getParameter("SUBSONIC_APP_NAME", "subsonic-connector")
