from flask_restful import Api

from .auth import AuthResource, AuthCallbackResource
from .user import GetUser, GetListenedTracks
from .services import SaveSpotifyData, UpdateTopmix


def register_routes(api: Api):
    api.add_resource(AuthResource, '/api/auth/')
    api.add_resource(AuthCallbackResource, '/api/auth/callback')
    api.add_resource(GetUser, '/api/user/')
    api.add_resource(GetListenedTracks, '/api/user/listened')
    api.add_resource(SaveSpotifyData, '/api/service/save')
    api.add_resource(UpdateTopmix, '/api/service/topmix')
