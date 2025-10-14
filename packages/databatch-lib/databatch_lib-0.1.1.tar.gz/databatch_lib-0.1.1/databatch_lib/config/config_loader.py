import os
import re
import yaml
from typing import List, Optional, Union

from dotenv import dotenv_values, load_dotenv
from loguru import logger
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings
from ..utils.constants import DEFAULT_SQS_RETRIES

DEV_CONFIG = os.path.join(os.path.dirname(__file__), "dev.env")
print(os.path.exists(DEV_CONFIG))
# print(os.stat(DEV_CONFIG))
PROP_FILE = os.path.join(os.path.dirname(__file__), "ISOGENAI_CLM_Data_Load.properties")


class EnvVariables(BaseSettings):
    OPENSEARCH_VECTOR_INDEX: str
    TOC_VECTOR_INDEX: str
    PROFILE_NAME: Optional[str]
    REGION: str
    BEDROCK_URL_ENDPOINT: str
    OPENSEARCH_HOST_NAME: str
    SERVICE: str
    AUTH: str
    PORT: Union[int, str]
    SOURCE_BASE_URL: str
    SOURCE_SEARCH_URL: str
    SOURCE_DOWNLOAD_URL: str
    TEXT_EMBEDDING_MODEL_ID: str
    OPENSEARCH_VECTOR_INDEX_FOR_EI: str
    OPENSEARCH_VECTOR_INDEX_FOR_LMON: str
    OPENSEARCH_VECTOR_INDEX_FOR_MANUALS: str
    OPENSEARCH_VECTOR_INDEX_FOR_NEWS_FEED: str
    SOLR_URL: str
    SOLR_COLLECTION: str
    SOLR_USERNAME: str
    SOLR_PASSWORD: str
    PRODUCT_LINK_URL_ENV: str
    INPUT_SQS_QUEUE: str
    MANUALS_BASE_URL: str
    DYNAMODB_TABLE: str
    MAX_SQS_RETRIES: int

    @field_validator("PROFILE_NAME", mode="before")
    def set_none_if_empty(cls, value):
        """
        If profile is set to None, boto3 uses default profile present in the env.
        It throws error if profile is an empty string. Set profile to None in such case.
        """
        if value.strip() in ["", "#{aws_profile_name}", "#{profile_name}"]:
            return None
        return value
    
    @field_validator("MAX_SQS_RETRIES", mode="before")
    def parse_max_sqs_retries_or_default(cls, value):
        """
        Parses the input value and returns it as an integer representing the max SQS retries.
        If the input value cannot be converted to an integer (due to ValueError or TypeError), returns the default value
        specified by DEFAULT_SQS_RETRIES.

        Args:
            value: The input value to parse, expected to be convertible to an integer.

        Returns:
            int: The parsed integer value or the default value if parsing fails.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return DEFAULT_SQS_RETRIES

    def __str__(self):
        result = "\n"
        for key, value in self.model_dump().items():
            result += f"{key}: {value}\n"
        return result


def get_fields_without_defaults(model_cls: BaseModel) -> List[str]:
    """
    Return a list of required fields for a pydantic BaseModel
    """
    fields = model_cls.model_fields
    no_default_fields = [
        name for name, field in fields.items() if field.default == PydanticUndefined
    ]
    return no_default_fields


def load_from_env_file(env_file: str) -> EnvVariables:
    passed_keys_from_env = set(dotenv_values(env_file))
    required_keys = set(get_fields_without_defaults(EnvVariables))

    if not required_keys.issubset(passed_keys_from_env):
        missing_keys = ", ".join(required_keys - passed_keys_from_env)
        raise SystemExit(
            f"Environment File: {env_file} doesn't contain required keys: {missing_keys}"
        )

    load_dotenv(env_file)
    env_variable = EnvVariables()
    return env_variable


def load_properties_configuration_file(prop_file: str) -> EnvVariables:
    vars_dict = {}
    with open(os.path.join(os.path.dirname(__file__), prop_file)) as config_file:
        for row in config_file:
            clean_row = row.rstrip()

            empty_row = not clean_row
            is_comment = clean_row.startswith("#")
            if is_comment or empty_row:
                continue

            key, value = clean_row.split("=")
            value = re.sub(r"^\S*\s", "", value)
            vars_dict[key.upper().strip()] = value.strip()

    env_variable = EnvVariables(**vars_dict)
    logger.info(f"Initialized env_variable: {env_variable}")
    return env_variable


clm_env_value = os.environ.get("CLM_ENV", "")
logger.debug(f"CLM_ENV value is : {clm_env_value}")

if os.environ.get("CLM_ENV", "").lower() == "local":
    env_variable = load_from_env_file(DEV_CONFIG)
    logger.debug("loading env variables for dev environment")
    logger.info(env_variable)
    config_path = "dev_config.yaml"

else:
    env_variable = load_properties_configuration_file(PROP_FILE)
    logger.info(env_variable)
    config_path = "config.yaml"

## Loading yaml configuration and logging:
logger.debug(f"loading yaml configuration from path : {config_path}")
with open(os.path.join(os.path.dirname(__file__), config_path), "r") as f:
    chunking_config = yaml.load(f, Loader=yaml.SafeLoader)
    logger.info(chunking_config)
