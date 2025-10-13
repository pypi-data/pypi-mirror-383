# SPDX-FileCopyrightText: 2024-present Edoardo Abati
#
# SPDX-License-Identifier: MIT

import os
from contextlib import nullcontext
from unittest import mock

import pytest
from haystack import Pipeline
from haystack.utils import Secret

from outlines_haystack.generators.openai import OpenAIChoiceGenerator
from tests.utils import CHOICES, mock_choice_func

MODEL_NAME = "gpt-4-mini"


@mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
def test_init_default() -> None:
    component = OpenAIChoiceGenerator(model_name=MODEL_NAME, choices=CHOICES)
    assert component.model_name == MODEL_NAME
    assert component.api_key.resolve_value() == "test-api-key"
    assert component.organization is None
    assert component.project is None
    assert component.base_url is None
    assert component.timeout == 30
    assert component.max_retries == 5
    assert component.default_headers is None
    assert component.default_query is None
    assert component.generation_kwargs == {}
    assert component.openai_config is None
    assert component.choices == CHOICES


def test_init_params() -> None:
    component = OpenAIChoiceGenerator(
        model_name=MODEL_NAME,
        choices=CHOICES,
        api_key=Secret.from_token("test-api-key"),
        timeout=60,
        max_retries=10,
        default_headers={"test-header": "test-value"},
        generation_kwargs={"temperature": 0.5},
    )
    assert component.model_name == MODEL_NAME
    assert component.api_key.resolve_value() == "test-api-key"
    assert component.organization is None
    assert component.project is None
    assert component.timeout == 60
    assert component.max_retries == 10
    assert component.default_headers == {"test-header": "test-value"}
    assert component.default_query is None
    assert component.generation_kwargs == {"temperature": 0.5}
    assert component.openai_config.temperature == 0.5
    assert component.choices == CHOICES


def test_init_value_error() -> None:
    with pytest.raises(ValueError, match="None of the following authentication environment variables are set"):
        OpenAIChoiceGenerator(model_name=MODEL_NAME, choices=CHOICES)


@mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
def test_to_dict() -> None:
    component = OpenAIChoiceGenerator(
        model_name=MODEL_NAME,
        choices=CHOICES,
        timeout=60,
        max_retries=10,
        default_headers={"test-header": "test-value"},
    )
    assert component.to_dict() == {
        "type": "outlines_haystack.generators.openai.OpenAIChoiceGenerator",
        "init_parameters": {
            "model_name": MODEL_NAME,
            "choices": CHOICES,
            "api_key": {"type": "env_var", "env_vars": ["OPENAI_API_KEY"], "strict": True},
            "organization": None,
            "project": None,
            "base_url": None,
            "timeout": 60,
            "max_retries": 10,
            "default_headers": {"test-header": "test-value"},
            "default_query": None,
            "generation_kwargs": {},
        },
    }


@pytest.mark.parametrize(
    "mock_os_environ",
    [
        {},
        {
            "OPENAI_API_KEY": "test-api-key",
        },
    ],
)
def test_from_dict(mock_os_environ: dict[str, str]) -> None:
    component_dict = {
        "type": "outlines_haystack.generators.openai.OpenAIChoiceGenerator",
        "init_parameters": {
            "model_name": MODEL_NAME,
            "choices": CHOICES,
            "api_key": {"type": "env_var", "env_vars": ["OPENAI_API_KEY"], "strict": True},
            "organization": None,
            "project": None,
            "base_url": None,
            "timeout": 60,
            "max_retries": 10,
            "default_headers": {"test-header": "test-value"},
            "default_query": None,
            "generation_kwargs": {"temperature": 0.5},
        },
    }
    error_context = (
        pytest.raises(ValueError, match="None of the following authentication environment variables are set")
        if not mock_os_environ
        else nullcontext()
    )

    with mock.patch.dict(os.environ, mock_os_environ), error_context:
        component = OpenAIChoiceGenerator.from_dict(component_dict)

        if mock_os_environ:
            assert component.model_name == MODEL_NAME
            assert component.api_key.resolve_value() == "test-api-key"
            assert component.timeout == 60
            assert component.max_retries == 10
            assert component.default_headers == {"test-header": "test-value"}
            assert component.openai_config.temperature == 0.5
            assert component.choices == CHOICES


@mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
def test_pipeline() -> None:
    component = OpenAIChoiceGenerator(model_name=MODEL_NAME, choices=CHOICES)
    p = Pipeline()
    p.add_component(instance=component, name="generator")
    p_str = p.dumps()
    q = Pipeline.loads(p_str)
    assert p.to_dict() == q.to_dict()


@mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
def test_run() -> None:
    component = OpenAIChoiceGenerator(model_name=MODEL_NAME, choices=CHOICES)

    with mock.patch("outlines_haystack.generators.openai.generate.choice") as mock_generate:
        mock_generate.return_value = mock_choice_func
        response = component.run("Which option should I choose?")

    assert isinstance(response, dict)
    assert "choice" in response
    assert response["choice"] == "yes"
