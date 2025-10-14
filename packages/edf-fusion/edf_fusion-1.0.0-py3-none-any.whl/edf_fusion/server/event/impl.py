"""Fusion Event API"""

from dataclasses import dataclass

from aiohttp.web import Application, HTTPBadRequest, Request, get

from ...concept import Case, EventType
from ...helper.aiohttp import get_guid, pubsub_sse_response
from ...helper.logging import get_logger
from ...helper.notifier import FusionNotifier, create_notifier_session
from ...helper.pubsub import PubSub
from ..auth import get_fusion_auth_api
from ..storage import get_fusion_storage
from .config import FusionEventAPIConfig

_LOGGER = get_logger('server.event.impl')
_FUSION_EVENT_API = 'fusion_evt_api'


@dataclass(kw_only=True)
class FusionEventAPI:
    """Fusion Event API"""

    config: FusionEventAPIConfig
    event_cls: EventType
    _pubsub: PubSub | None = None
    _notifier: FusionNotifier | None = None

    def setup(self, webapp: Application):
        """Setup web application routes"""
        _LOGGER.info("install event api...")
        webapp[_FUSION_EVENT_API] = self
        webapp.add_routes(
            [
                get('/api/events/case/{case_guid}', self.subscribe),
            ]
        )
        webapp.cleanup_ctx.append(self.context)
        _LOGGER.info("event api installed.")

    async def context(self, webapp: Application):
        """Context"""
        if not self.config.enabled:
            _LOGGER.info("event api disabled.")
            yield
            return
        _LOGGER.info("startup event api...")
        session = create_notifier_session(
            self.config.api_key, self.config.timeout
        )
        async with session:
            self._pubsub = PubSub()
            self._notifier = FusionNotifier(
                session=session, api_ssl=self.config.api_ssl
            )
            yield
            await self._pubsub.terminate()
            self._notifier = None
            self._pubsub = None
        _LOGGER.info("cleanup event api...")

    async def notify(
        self, category: str, case: Case, ext: dict | None = None
    ) -> dict[str, int]:
        """Send event to endpoints (including global endpoint if set)"""
        if not self.config.enabled:
            return {}
        webhooks = []
        if self.config.webhook:
            webhooks.append(self.config.webhook)
        event = self.event_cls(category=category, case=case, ext=ext)
        await self._pubsub.publish(event, str(case.guid))
        status_map = await self._notifier.notify(event, webhooks)
        return status_map

    async def subscribe(self, request: Request):
        """Subscribe to case event channel"""
        case_guid = get_guid(request, 'case_guid')
        fusion_storage = get_fusion_storage(request)
        fusion_auth_api = get_fusion_auth_api(request)
        if not case_guid:
            raise HTTPBadRequest(reason="Invalid case GUID")
        identity = await fusion_auth_api.authorize(
            request, 'subscribe', context={'case_guid': case_guid}
        )
        case = await fusion_storage.retrieve_case(case_guid)
        if not case_guid:
            raise HTTPBadRequest(reason="Failed to retrieve case from GUID")
        ext = {'username': identity.username}
        await self.notify(category='subscribe', case=case, ext=ext)
        response = await pubsub_sse_response(
            request, self._pubsub, identity.username, str(case_guid)
        )
        await self.notify(category='unsubscribe', case=case, ext=ext)
        return response


def get_fusion_evt_api(request: Request) -> FusionEventAPI:
    """Retrieve FusionEventAPI instance from request"""
    return request.app[_FUSION_EVENT_API]
