import requests
from davidkhala.http_request import default_on_response
from requests import HTTPError, Response

from davidkhala.ai.api import API

class OpenRouter(API):
    @property
    def free_models(self) -> list[str]:
        return list(
            map(lambda model: model['id'],
                filter(lambda model: model['id'].endswith(':free'), self.list_models())
                )
        )

    @staticmethod
    def on_response(response: requests.Response):
        r = default_on_response(response)
        # openrouter special error on response.ok
        err = r.get('error')
        if err:
            derived_response = Response()
            derived_response.status_code = err.pop('code', None)
            derived_response._content = err.pop('message', None)
            http_err =  HTTPError(response=derived_response)
            http_err.metadata = err.get("metadata")
            raise http_err
        return r

    def __init__(self, api_key: str, *models: str, **kwargs):

        super().__init__(api_key, 'https://openrouter.ai/api')

        if 'leaderboard' in kwargs and type(kwargs['leaderboard']) is dict:
            self._.options["headers"]["HTTP-Referer"] = kwargs['leaderboard'][
                'url']  # Site URL for rankings on openrouter.ai.
            self._.options["headers"]["X-Title"] = kwargs['leaderboard'][
                'name']  # Site title for rankings on openrouter.ai.
        if not models:
            models = [self.free_models[0]]
        self.models = models

        self._.on_response = OpenRouter.on_response

    def chat(self, *user_prompt: str, **kwargs):
        if len(self.models) > 1:
            kwargs["models"] = self.models
        else:
            kwargs["model"] = self.models[0]

        return super().chat(*user_prompt, **kwargs)
