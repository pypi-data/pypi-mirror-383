
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

from typing import Any
from typing import Dict

from langchain_core.language_models.base import BaseLanguageModel

from leaf_common.config.resolver import Resolver

from neuro_san.internals.run_context.langchain.llms.langchain_llm_factory import LangChainLlmFactory


class StandardLangChainLlmFactory(LangChainLlmFactory):
    """
    Factory class for LLM operations

    Most methods take a config dictionary which consists of the following keys:

        "model_name"                The name of the model.
                                    Default if not specified is "gpt-3.5-turbo"

        "temperature"               A float "temperature" value with which to
                                    initialize the chat model.  In general,
                                    higher temperatures yield more random results.
                                    Default if not specified is 0.7

        "prompt_token_fraction"     The fraction of total tokens (not necessarily words
                                    or letters) to use for a prompt. Each model_name
                                    has a documented number of max_tokens it can handle
                                    which is a total count of message + response tokens
                                    which goes into the calculation involved in
                                    get_max_prompt_tokens().
                                    By default the value is 0.5.

        "max_tokens"                The maximum number of tokens to use in
                                    get_max_prompt_tokens(). By default this comes from
                                    the model description in this class.
    """

    def create_base_chat_model(self, config: Dict[str, Any]) -> BaseLanguageModel:
        """
        Create a BaseLanguageModel from the fully-specified llm config.
        :param config: The fully specified llm config which is a product of
                    _create_full_llm_config() above.
        :return: A BaseLanguageModel (can be Chat or LLM)
                Can raise a ValueError if the config's class or model_name value is
                unknown to this method.
        """
        # Construct the LLM
        llm: BaseLanguageModel = None
        chat_class: str = config.get("class")
        if chat_class is not None:
            chat_class = chat_class.lower()

        # Check for key "model_name", "model", and "model_id" to use as model name
        # If the config is from default_llm_info, this is always "model_name"
        # but with user-specified config, it is possible to have the other keys will be specifed instead.
        model_name: str = config.get("model_name") or config.get("model") or config.get("model_id")

        # Set up a resolver to use to resolve lazy imports of classes from
        # langchain_* packages to prevent installing the world.
        resolver = Resolver()

        if chat_class == "openai":

            # OpenAI is the one chat class that we do not require any extra installs.
            # This is what we want to work out of the box.
            # Nevertheless, have it go through the same lazy-loading resolver rigamarole as the others.

            # pylint: disable=invalid-name
            ChatOpenAI = resolver.resolve_class_in_module("ChatOpenAI",
                                                          module_name="langchain_openai.chat_models.base",
                                                          install_if_missing="langchain-openai")
            llm = ChatOpenAI(
                model_name=model_name,
                temperature=config.get("temperature"),
                openai_api_key=self.get_value_or_env(config, "openai_api_key",
                                                     "OPENAI_API_KEY"),
                openai_api_base=self.get_value_or_env(config, "openai_api_base",
                                                      "OPENAI_API_BASE"),
                openai_organization=self.get_value_or_env(config, "openai_organization",
                                                          "OPENAI_ORG_ID"),
                openai_proxy=self.get_value_or_env(config, "openai_organization",
                                                   "OPENAI_PROXY"),
                request_timeout=config.get("request_timeout"),
                max_retries=config.get("max_retries"),
                presence_penalty=config.get("presence_penalty"),
                frequency_penalty=config.get("frequency_penalty"),
                seed=config.get("seed"),
                logprobs=config.get("logprobs"),
                top_logprobs=config.get("top_logprobs"),
                logit_bias=config.get("logit_bias"),
                streaming=True,     # streaming is always on. Without it token counting will not work.
                n=1,                # n is always 1.  neuro-san will only ever consider one chat completion.
                top_p=config.get("top_p"),
                max_tokens=config.get("max_tokens"),    # This is always for output
                tiktoken_model_name=config.get("tiktoken_model_name"),
                stop=config.get("stop"),

                # The following three parameters are for reasoning models only.
                reasoning=config.get("reasoning"),
                reasoning_effort=config.get("reasoning_effort"),
                verbosity=config.get("verbosity"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,

                # Set stream_usage to True in order to get token counting chunks.
                stream_usage=True
            )
        elif chat_class == "azure-openai":
            model_kwargs: Dict[str, Any] = {
                "stream_options": {
                    "include_usage": True
                }
            }
            openai_api_key: str = self.get_value_or_env(config, "openai_api_key", "AZURE_OPENAI_API_KEY")
            if openai_api_key is None:
                openai_api_key = self.get_value_or_env(config, "openai_api_key", "OPENAI_API_KEY")

            # AzureChatOpenAI just happens to come with langchain_openai
            # pylint: disable=invalid-name
            AzureChatOpenAI = resolver.resolve_class_in_module("AzureChatOpenAI",
                                                               module_name="langchain_openai.chat_models.azure",
                                                               install_if_missing="langchain-openai")
            llm = AzureChatOpenAI(
                model_name=model_name,
                temperature=config.get("temperature"),
                openai_api_key=openai_api_key,
                openai_api_base=self.get_value_or_env(config, "openai_api_base",
                                                      "OPENAI_API_BASE"),
                openai_organization=self.get_value_or_env(config, "openai_organization",
                                                          "OPENAI_ORG_ID"),
                openai_proxy=self.get_value_or_env(config, "openai_organization",
                                                   "OPENAI_PROXY"),
                request_timeout=config.get("request_timeout"),
                max_retries=config.get("max_retries"),
                presence_penalty=config.get("presence_penalty"),
                frequency_penalty=config.get("frequency_penalty"),
                seed=config.get("seed"),
                logprobs=config.get("logprobs"),
                top_logprobs=config.get("top_logprobs"),
                logit_bias=config.get("logit_bias"),
                streaming=True,     # streaming is always on. Without it token counting will not work.
                n=1,                # n is always 1.  neuro-san will only ever consider one chat completion.
                top_p=config.get("top_p"),
                max_tokens=config.get("max_tokens"),    # This is always for output
                tiktoken_model_name=config.get("tiktoken_model_name"),
                stop=config.get("stop"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,

                # Azure-specific
                azure_endpoint=self.get_value_or_env(config, "azure_endpoint",
                                                     "AZURE_OPENAI_ENDPOINT"),
                deployment_name=self.get_value_or_env(config, "deployment_name",
                                                      "AZURE_OPENAI_DEPLOYMENT_NAME"),
                openai_api_version=self.get_value_or_env(config, "openai_api_version",
                                                         "OPENAI_API_VERSION"),

                # AD here means "ActiveDirectory"
                azure_ad_token=self.get_value_or_env(config, "azure_ad_token",
                                                     "AZURE_OPENAI_AD_TOKEN"),
                model_version=config.get("model_version"),
                openai_api_type=self.get_value_or_env(config, "openai_api_type",
                                                      "OPENAI_API_TYPE"),
                # Needed for token counting
                model_kwargs=model_kwargs,
            )
        elif chat_class == "anthropic":

            # Use lazy loading to prevent installing the world
            # pylint: disable=invalid-name
            ChatAnthropic = resolver.resolve_class_in_module("ChatAnthropic",
                                                             module_name="langchain_anthropic.chat_models",
                                                             install_if_missing="langchain-anthropic")
            llm = ChatAnthropic(
                model_name=model_name,
                max_tokens=config.get("max_tokens"),    # This is always for output
                temperature=config.get("temperature"),
                top_k=config.get("top_k"),
                top_p=config.get("top_p"),
                default_request_timeout=config.get("default_request_timeout"),
                max_retries=config.get("max_retries"),
                stop_sequences=config.get("stop_sequences"),
                anthropic_api_url=self.get_value_or_env(config, "anthropic_api_url",
                                                        "ANTHROPIC_API_URL"),
                anthropic_api_key=self.get_value_or_env(config, "anthropic_api_key",
                                                        "ANTHROPIC_API_KEY"),
                streaming=True,     # streaming is always on. Without it token counting will not work.
                # Set stream_usage to True in order to get token counting chunks.
                stream_usage=True,

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,
            )
        elif chat_class == "ollama":

            # Use lazy loading to prevent installing the world
            # pylint: disable=invalid-name
            ChatOllama = resolver.resolve_class_in_module("ChatOllama",
                                                          module_name="langchain_ollama",
                                                          install_if_missing="langchain-ollama")
            # Higher temperature is more random
            llm = ChatOllama(
                model=model_name,
                mirostat=config.get("mirostat"),
                mirostat_eta=config.get("mirostat_eta"),
                mirostat_tau=config.get("mirostat_tau"),
                num_ctx=config.get("num_ctx"),
                num_gpu=config.get("num_gpu"),
                num_thread=config.get("num_thread"),
                num_predict=config.get("num_predict", config.get("max_tokens")),
                reasoning=config.get("reasoning"),
                repeat_last_n=config.get("repeat_last_n"),
                repeat_penalty=config.get("repeat_penalty"),
                temperature=config.get("temperature"),
                seed=config.get("seed"),
                stop=config.get("stop"),
                tfs_z=config.get("tfs_z"),
                top_k=config.get("top_k"),
                top_p=config.get("top_p"),
                keep_alive=config.get("keep_alive"),
                base_url=config.get("base_url"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,
            )
        elif chat_class == "nvidia":

            # Use lazy loading to prevent installing the world
            # pylint: disable=invalid-name
            ChatNVIDIA = resolver.resolve_class_in_module("ChatNVIDIA",
                                                          module_name="langchain_nvidia_ai_endpoints",
                                                          install_if_missing="langchain-nvidia-ai-endpoints")
            # Higher temperature is more random
            llm = ChatNVIDIA(
                base_url=config.get("base_url"),
                model=model_name,
                temperature=config.get("temperature"),
                max_tokens=config.get("max_tokens"),
                top_p=config.get("top_p"),
                seed=config.get("seed"),
                stop=config.get("stop"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,
                nvidia_api_key=self.get_value_or_env(config, "nvidia_api_key",
                                                     "NVIDIA_API_KEY"),
                nvidia_base_url=self.get_value_or_env(config, "nvidia_base_url",
                                                      "NVIDIA_BASE_URL"),
            )
        elif chat_class == "gemini":

            # Use lazy loading to prevent installing the world
            # pylint: disable=invalid-name
            ChatGoogleGenerativeAI = resolver.resolve_class_in_module("ChatGoogleGenerativeAI",
                                                                      module_name="langchain_google_genai.chat_models",
                                                                      install_if_missing="langchain-google-genai")
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.get_value_or_env(config, "google_api_key",
                                                     "GOOGLE_API_KEY"),
                max_retries=config.get("max_retries"),
                max_tokens=config.get("max_tokens"),    # This is always for output
                n=config.get("n"),
                temperature=config.get("temperature"),
                timeout=config.get("timeout"),
                top_k=config.get("top_k"),
                top_p=config.get("top_p"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,
            )
        elif chat_class == "bedrock":

            # Use lazy loading to prevent installing the world
            # pylint: disable=invalid-name
            ChatBedrock = resolver.resolve_class_in_module("ChatBedrock",
                                                           module_name="langchain_aws",
                                                           install_if_missing="langchain-aws")
            llm = ChatBedrock(
                model=model_name,
                aws_access_key_id=self.get_value_or_env(config, "aws_access_key_id", "AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=self.get_value_or_env(config, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY"),
                aws_session_token=self.get_value_or_env(config, "aws_session_token", "AWS_SESSION_TOKEN"),
                base_model_id=config.get("base_model_id"),
                beta_use_converse_api=config.get("beta_use_converse_api"),
                cache=config.get("cache"),
                config=config.get("config"),
                credentials_profile_name=config.get("credentials_profile_name"),
                custom_get_token_ids=config.get("custom_get_token_ids"),
                endpoint_url=config.get("endpoint_url"),
                guardrails=config.get("guardrails"),
                max_tokens=config.get("max_tokens"),
                metadata=config.get("metadata"),
                provider=config.get("provider"),
                rate_limiter=config.get("rate_limiter"),
                region_name=config.get("region_name"),
                stop_sequences=config.get("stop_sequences"),
                streaming=True,
                system_prompt_with_tools=config.get("system_prompt_with_tools"),
                tags=config.get("tags"),
                temperature=config.get("temperature"),

                # If omitted, this defaults to the global verbose value,
                # accessible via langchain_core.globals.get_verbose():
                # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/globals.py#L53
                #
                # However, accessing the global verbose value during concurrent initialization
                # can trigger the following warning:
                #
                # UserWarning: Importing verbose from langchain root module is no longer supported.
                # Please use langchain.globals.set_verbose() / langchain.globals.get_verbose() instead.
                # old_verbose = langchain.verbose
                #
                # To prevent this, we explicitly set verbose=False here (which matches the default
                # global verbose value) so that the warning is never triggered.
                verbose=False,
            )
        elif chat_class is None:
            raise ValueError(f"Class name {chat_class} for model_name {model_name} is unspecified.")
        else:
            raise ValueError(f"Class {chat_class} for model_name {model_name} is unrecognized.")

        return llm
