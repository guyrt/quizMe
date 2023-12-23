import logging
from dataclasses import asdict
from json import dumps
from typing import Optional

from django.db import transaction

from azurewrapper.openai_client import OpenAIClient
from azurewrapper.prompt_types import fill_prompt
from extensionapis.models import RawDocCapture
from mltrack.consumer_prompt_models import ConsumerPromptTrack
from parser_utils.utilities import get_rough_article_content, parse_contents
from rfp_utils.json_utils import find_json

from .models import SimpleQuiz
from .quiz_prompts import quiz_gen

logger = logging.getLogger("default")


class QuizGenerator:

    def __init__(self) -> None:
        self._oai = OpenAIClient(model='gpt4', temp=0.7)


    def create_quiz(self, raw_doc : RawDocCapture) -> Optional[SimpleQuiz]:
        logger.error("Creating a quiz init for %s", raw_doc.id)

        raw_dom = parse_contents(raw_doc.get_content())
        article_content = get_rough_article_content(raw_doc, raw_dom)
        if article_content == "":
            logger.error("No article content for %s", raw_doc.id)
            return None

        # Generate response
        quiz_content = self._run_openai(article_content)
        if not quiz_content:
            logger.error("No content from openai for %s", raw_doc.id)
            return None

        preamble, raw_quiz_content = self._extract_quiz_json(quiz_content['response'])

        # Generate PromptResponse
        pr = ConsumerPromptTrack.objects.create(
            user=raw_doc.user,
            template_name=quiz_gen.name,
            template_version=quiz_gen.version,
            source_type='RawDocCapture',
            source_id=str(raw_doc.pk),
            prompt_tokens=quiz_content['tokens'].prompt_tokens,
            completion_tokens=quiz_content['tokens'].completion_tokens,
            model_service=self._oai.api_type,
            model_name=self._oai.engine
        )

        # Generate Quiz
        # with transaction:
        with transaction.atomic():
            SimpleQuiz.objects.filter(url=raw_doc.url_model).update(active=False)
            quiz = SimpleQuiz.objects.create(
                owner=raw_doc.user,
                content=dumps(raw_quiz_content),
                reasoning=preamble,
                url=raw_doc.url_model
            )

        # return it.
        return quiz

    def _run_openai(self, article_content : str):
        current = fill_prompt(quiz_gen, {'doc_content': article_content, 'num_questions': 'three'})
        messages = [asdict(c) for c in current.content]
        try:
            response = self._oai.call(messages, temp=quiz_gen.temp)
            return response
        except Exception as e:
            logger.error("Error trying to generate quiz: %s", e)
            return None
        
    def _extract_quiz_json(self, raw_content : str):
        """Find the specific JSON quiz"""
        # TODO - brittle. validate that quiz is right shape.
        # also handle bad JSON in some better way.
        preamble, obj, _ = find_json(raw_content)
        return preamble, obj
