from vcr_unittest import VCRTestCase
from django.conf import settings


class BaseTestCase(VCRTestCase):
    def _get_vcr(self, **kwargs):
        if not settings.USE_MOCK:
            self.vcr_enabled = False
            return False

        kwargs['record_mode'] = 'none' if settings.MOCK_OR_ERROR else 'new_episodes'
        kwargs['match_on'] = ['method', 'scheme', 'host', 'port', 'path', 'query', 'body', 'headers']
        kwargs['cassette_library_dir'] = settings.ROOT_PATH + '/src/tests/cassettes'

        myvcr = super(BaseTestCase, self)._get_vcr(**kwargs)
        return myvcr
