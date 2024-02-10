import logging
from dataclasses import asdict
from json import dumps
from typing import Optional, List

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
        self._return_tokens = 1000
        self._oai = OpenAIClient(model='gpt4', temp=0.7, max_doc_tokens=self._return_tokens)

    def create_quiz(self, raw_doc : RawDocCapture, quiz_id : int) -> Optional[SimpleQuiz]:
        logger.info("Creating a quiz init for %s", raw_doc.pk)

        SimpleQuiz.objects.filter(id=quiz_id).update(status=SimpleQuiz.QuizStatus.Building)

        raw_dom = parse_contents(raw_doc.get_content_prefer_readable())
        article_content = get_rough_article_content(raw_doc, raw_dom)
        if article_content == "":
            logger.error("No article content for %s", raw_doc.pk)
            return None

        current_size = len(article_content)
        article_content = self._shrink_article(article_content)
        new_size = len(article_content)
        if new_size != current_size:
            logger.info("Resized doc from %s to %s", current_size, new_size)

        # Generate response
        quiz_content = self._run_openai(article_content)
        if not quiz_content:
            logger.error("No content from openai for %s", raw_doc.pk)
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
            # update any other quizzes
            SimpleQuiz.objects.filter(url=raw_doc.url_model).exclude(id=quiz_id).update(active=False)
            s = SimpleQuiz.objects.get(id=quiz_id)
            s.content = dumps(raw_quiz_content)
            s.reasoning = preamble
            s.status = SimpleQuiz.QuizStatus.Completed
            s.save()

        # return it.
        return s

    def _shrink_article(self, article_content : str) -> str:
        """If the article is too long, shrink it to fit in payload"""
        num_prompt_tokens = 183  # this is from the system prompt.
        total_allowed_tokens = 8000 - self._return_tokens - num_prompt_tokens  # allow 1000 for return.

        total_article_size = self._oai.num_tokens_from_string(article_content)
        if total_article_size < total_allowed_tokens:
            return article_content
        
        num_tokens_to_remove = total_article_size - total_allowed_tokens
        sections = self._partition_string(article_content, 4)
        if total_article_size // num_tokens_to_remove < 0.25:
            # we can remove the tokens from third section.
            section = sections[2]
            delete_ratio = num_tokens_to_remove / self._oai.num_tokens_from_string(section) + 0.02  # fudge factor...
            delete_target = len(section) * (1 - delete_ratio)
            sections[2] = " ...omitted content... " + sections[2][:delete_target]
            return ''.join(sections)
        else:
            # we need to remove third section and rerun.
            sections[2] = " ...omitted content... "
            return self._shrink_article(''.join(sections))


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

    def _partition_string(self, s : str, num_partitions : int) -> List[str]:
        s += ' ' * (len(s) % num_partitions)
        part_length = len(s) // num_partitions
        parts = [s[i * part_length: (i + 1) * part_length] for i in range(4)]
        return parts