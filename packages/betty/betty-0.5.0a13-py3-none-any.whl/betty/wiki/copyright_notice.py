"""
Wikipedia copyright notices.
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Self, final

from typing_extensions import override

from betty.app.factory import AppDependentFactory
from betty.copyright_notice import CopyrightNotice, CopyrightNoticeDefinition
from betty.fetch import Fetcher, FetchError
from betty.locale import negotiate_locale, to_babel_identifier
from betty.locale.localizable import Localizable, _
from betty.locale.localized import LocalizedStr

if TYPE_CHECKING:
    from collections.abc import Mapping

    from betty.app import App
    from betty.locale.localized import Localized
    from betty.locale.localizer import Localizer


@final
@CopyrightNoticeDefinition(
    id="wikipedia-contributors",
    label=_("Wikipedia contributors"),
)
class WikipediaContributors(AppDependentFactory, CopyrightNotice):
    """
    The copyright for resources on Wikipedia.
    """

    def __init__(self, urls: Mapping[str, str]):
        self._url = _WikipediaContributorsUrl({"en": "Wikipedia:Copyrights", **urls})

    @classmethod
    async def new(cls, fetcher: Fetcher) -> Self:
        """
        Create a new instance.
        """
        urls = {}
        try:
            languages_response = await fetcher.fetch(
                "https://en.wikipedia.org/w/api.php?action=query&titles=Wikipedia:Copyrights&prop=langlinks&lllimit=500&format=json&formatversion=2"
            )
        except FetchError:
            pass
        else:
            for link in languages_response.json["query"]["pages"][0]["langlinks"]:
                with suppress(ValueError):
                    urls[to_babel_identifier(link["lang"])] = link["title"]
        return cls(urls)

    @override
    @classmethod
    async def new_for_app(cls, app: App) -> Self:
        return await cls.new(await app.fetcher)

    @override
    @property
    def summary(self) -> Localizable:
        return _("Copyright Wikipedia contributors")

    @override
    @property
    def text(self) -> Localizable:
        return _(
            "Copyright of these works lies with the original authors who contributed them to Wikipedia."
        )

    @override
    @property
    def url(self) -> Localizable:
        return self._url


class _WikipediaContributorsUrl(Localizable):
    def __init__(self, urls: Mapping[str, str]):
        self._urls = urls

    @override
    def localize(self, localizer: Localizer) -> Localized & str:
        locale = negotiate_locale([localizer.locale, "en"], list(self._urls))
        # We know there's always "en" (English).
        assert locale is not None
        return LocalizedStr(
            f"https://{locale}.wikipedia.org/wiki/{self._urls[locale.language]}",
            locale=locale.language,
        )
