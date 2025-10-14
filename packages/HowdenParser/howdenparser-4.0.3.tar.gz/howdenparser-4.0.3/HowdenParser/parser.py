from abc import ABC, abstractmethod
import os
import logging
from pathlib import Path
from PyPDF2 import PdfReader
import dotenv
from typing import overload, Literal
from inspect import signature, Signature

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    _registry: dict[str, type["BaseParser"]] = {}

    def __init__(self):
        # Every instance gets a .name attribute
        self.name = getattr(self.__class__, "_parser_name", self.__class__.__name__)

    def __init_subclass__(cls, name: str | None = None, **kwargs):
        """Automatically register subclasses under a key."""
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower().replace("parser", "")
        BaseParser._registry[key] = cls
        BaseParser._registry.pop("", None)

    @abstractmethod
    def parse(self, text: str):
        pass


class Parser(BaseParser):
    """Factory + registry interface for all parsers."""

    def __new__(cls, config_or_dict: "Parameter | dict | str" = None, **kwargs) -> BaseParser:
        """
        Factory entrypoint.
        Allows calling Parser(...) directly to create the correct subclass.
        """
        return cls._create(config_or_dict, **kwargs)

    @classmethod
    def available_parsers(cls) -> None:
        """Print registered parsers and their init arguments."""
        import inspect
        result = {}
        for name, parser_cls in BaseParser._registry.items():
            sig = inspect.signature(parser_cls.__init__)
            result[name] = [p for p in sig.parameters if p != "self"]
        result.pop("", None)
        for key, values in result.items():
            print(f"{key} with parameters: {values}")

    # ---- Overloads for IDE autocomplete ----
    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["llamaparser:"],
            result_type: str,
            mode: bool,
            preserve_layout_alignment_across_pages: bool,
            merge_tables_across_pages_in_markdown: bool,
            hide_footers: bool,
            hide_headers: bool,
    ) -> "LlamaParser": ...

    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["mistralocr:ocr-large", "mistralocr:ocr-small"],
    ) -> "MistralOCRParser": ...

    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal["langchain:gpt-3.5-turbo", "langchain:gpt-4"],
    ) -> "LangChainParser": ...

    @overload
    @classmethod
    def _create(
            cls,
            *,
            provider_and_model: Literal[
                "huggingface:microsoft/trocr-base-handwritten",
                "huggingface:microsoft/trocr-large-printed",
            ],
    ) -> "HuggingFaceParser": ...

    # ---- Implementation ----
    @classmethod
    def _create(cls, config_or_dict: "Parameter | dict | str" = None, **kwargs) -> BaseParser:
        """
        Dynamically create parser instances.
        Supports: Parameter, dict, str (provider_and_model), or kwargs.
        """

        if config_or_dict is None:
            config_dict = {}
        elif hasattr(config_or_dict, "model_dump"):
            config_dict = config_or_dict.model_dump()
        elif isinstance(config_or_dict, dict):
            config_dict = config_or_dict
        elif isinstance(config_or_dict, str):  # shorthand
            config_dict = {"provider_and_model": config_or_dict}
        else:
            raise TypeError("Expected Parameter instance, dict, str, or None for config_or_dict")

        merged_args = {**config_dict, **kwargs}

        if "provider_and_model" not in merged_args:
            raise ValueError("provider_and_model must be specified, e.g. 'llamaparser:'")

        provider_and_model = str(merged_args.get("provider_and_model")).strip()

        if ":" not in provider_and_model:
            raise ValueError("provider_and_model must include a colon, e.g. 'llamaparser:'")

        provider, model = provider_and_model.split(":", 1)
        provider = (provider or "").strip().lower()
        model = (model or "").strip().lower()

        if not provider:
            raise ValueError(f"Invalid provider_and_model '{provider_and_model}': provider part is empty.")

        if provider not in BaseParser._registry:
            raise ValueError(f"Unknown parser '{provider}'. Available: {list(BaseParser._registry)}")

        parser_cls = BaseParser._registry[provider]

        # --- Filter valid constructor args ---
        sig = signature(parser_cls.__init__)
        valid_args = {k: v for k, v in merged_args.items() if k in sig.parameters and k != "self"}

        # Auto-fill common args
        if "model" in sig.parameters and "model" not in valid_args:
            valid_args["model"] = model
        if "provider_and_model" in sig.parameters and "provider_and_model" not in valid_args:
            valid_args["provider_and_model"] = provider_and_model

        # --- Check required args ---
        required_params = [
            p.name
            for p in sig.parameters.values()
            if p.name != "self"
               and p.default is Signature.empty
               and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        ]
        missing = [name for name in required_params if name not in valid_args]

        # Special rule: for llamaparser we allow empty `model`
        if provider != "llamaparser" and not model:
            missing.append("model")

        if missing:
            example = ""
            if provider == "llamaparser":
                example = "Example: Parser('llamaparser:', result_type='md', mode=True, extract_tables=True)"
            elif provider == "mistralocr":
                example = "Example: Parser('mistralocr:ocr-large')"
            elif provider == "huggingface":
                example = "Example: Parser('huggingface:microsoft/trocr-base-handwritten')"
            elif provider == "langchain":
                example = "Example: Parser('langchain:gpt-3.5-turbo')"

            raise TypeError(
                f"{parser_cls.__name__} cannot be created because it is missing required argument(s): {', '.join(missing)}. {example}"
            )

        return parser_cls(**valid_args)

    @abstractmethod
    def parse(self, text: str):
        pass


# --- Parsers ---
class MistralOCRParser(BaseParser, name="mistralocr"):
    def __init__(self, provider_and_model: str) -> None:
        from mistralai import Mistral
        self.model = provider_and_model.split(":")[1]
        self.current_cost: float = 0.0
        self.total_cost_euro: float = 0.0
        api_key = os.getenv("MISTRAL-OCR-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing MISTRAL-OCR-API-TOKEN in .env file.")
        self.client = Mistral(api_key=api_key)

    def parse(self, file_path: Path) -> str:
        def upload_pdf(filename):
            uploaded_pdf = self.client.files.upload(
                file={"file_name": filename, "content": open(filename, "rb")},
                purpose="ocr",
            )
            signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
            return signed_url.url

        ocr_response = self.client.ocr.process(
            model=self.model,
            document={"type": "document_url", "document_url": upload_pdf(file_path)},
            include_image_base64=True,
        )
        self.current_cost = 1 / 1000 * self._count_pages(file_path)
        self.total_cost_euro += self.current_cost
        return "\n".join(doc.markdown for doc in ocr_response.pages)

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)

    @staticmethod
    def _count_pages(file_path: Path) -> int:
        reader = PdfReader(str(file_path))
        return len(reader.pages)


class LangChainParser(BaseParser, name="langchain"):
    def __init__(self, provider_and_model: str):
        from langchain.llms import OpenAI
        self.model = provider_and_model.split(":")[1]
        self.model = OpenAI(model_name=self.model)

    def parse(self, text: str) -> dict:
        response = self.model(text)
        return {"source": "LangChain", "output": response}

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)


class LlamaParser(BaseParser, name="llamaparser"):
    def __init__(self, result_type: str,
                 mode: bool,
                 provider_and_model: str,
                 merge_tables_across_pages_in_markdown: bool,
                 preserve_layout_alignment_across_pages: bool,
                 hide_footers: bool,
                 hide_headers: bool
                 ) -> None:
        logging.info("Initializing LlamaParser...")
        self.result_type = result_type
        self.mode = mode
        self.provider_and_model = provider_and_model
        self.merge_tables_across_pages_in_markdown = merge_tables_across_pages_in_markdown
        self.preserve_layout_alignment_across_pages = preserve_layout_alignment_across_pages
        self.hide_footers=hide_footers
        self.hide_headers=hide_headers

        from llama_parse import LlamaParse, ResultType
        if result_type.lower() in ("md", "markdown"):
            result_type = ResultType.MD
        api_key = os.getenv("LLAMA-PARSER-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing LLAMA-PARSER-API-TOKEN in .env file.")
        self._parser = LlamaParse(api_key=api_key,
                                  result_type=result_type,
                                  premium_mode=self.mode,
                                  merge_tables_across_pages_in_markdown=self.merge_tables_across_pages_in_markdown,
                                  preserve_layout_alignment_across_pages=self.preserve_layout_alignment_across_pages,
                                  hide_footers=self.hide_footers,
                                  hide_headers=self.hide_headers)

    def parse(self, file_path: Path) -> str:
        documents = self._parser.load_data(str(file_path))
        return "\n".join(doc.text for doc in documents)

    def __call__(self, file_path: Path) -> str:
        return self.parse(file_path)


class HuggingFaceParser(BaseParser, name="huggingface"):
    def __init__(self, provider_and_model: str) -> None:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        api_key = os.getenv("HF-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing HF-API-TOKEN in .env file.")
        model_name = provider_and_model.split(":")[1]
        logger.info(f"Loading Hugging Face OCR model: {model_name}")
        self.processor = TrOCRProcessor.from_pretrained(model_name, token=api_key)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name, token=api_key)
        logger.info("Model and processor loaded successfully.")

    def parse(self, file_path: Path) -> str:
        from pdf2image import convert_from_path
        logger.info(f"Converting PDF to images: {file_path}")
        pages = convert_from_path(file_path, dpi=300)
        logger.info(f"PDF conversion complete. Total pages: {len(pages)}")

        all_text = ""
        for i, page in enumerate(pages, start=1):
            logger.info(f"Running OCR on page {i}/{len(pages)}")
            pixel_values = self.processor(page, return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            all_text += text + "\n"
            logger.debug(f"OCR text (page {i}): {text[:100]}...")
        logger.info("OCR completed for all pages.")
        return all_text
