import json
import textwrap
from typing import Mapping, Sequence

import langextract as lx
import yaml
from json_repair import repair_json
from langextract.core import data, exceptions
from langextract.core.format_handler import ExtractionValueType, FormatHandler


# 自定义了 LangExtract 的格式处理器，将反序列化 json.loads 改为了 json_repair
class CustomFormatHandler(FormatHandler):
    def parse_output(
        self, text: str, *, strict: bool | None = None
    ) -> Sequence[Mapping[str, ExtractionValueType]]:
        if not text:
            raise exceptions.FormatParseError("Empty or invalid input string.")

        content = self._extract_content(text)

        try:
            if self.format_type == data.FormatType.YAML:
                parsed = yaml.safe_load(content)
            else:
                parsed = repair_json(content, return_objects=True)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            msg = (
                f"Failed to parse {self.format_type.value.upper()} content:"
                f" {str(e)[:200]}"
            )
            raise exceptions.FormatParseError(msg) from e

        if parsed is None:
            if self.use_wrapper:
                raise exceptions.FormatParseError(
                    f"Content must be a mapping with an '{self.wrapper_key}' key."
                )
            else:
                raise exceptions.FormatParseError(
                    "Content must be a list of extractions or a dict."
                )

        require_wrapper = self.wrapper_key is not None and (
            self.use_wrapper or bool(strict)
        )

        if isinstance(parsed, dict):
            if require_wrapper:
                if self.wrapper_key not in parsed:
                    raise exceptions.FormatParseError(
                        f"Content must contain an '{self.wrapper_key}' key."
                    )
                items = parsed[self.wrapper_key]
            else:
                if data.EXTRACTIONS_KEY in parsed:
                    items = parsed[data.EXTRACTIONS_KEY]
                elif self.wrapper_key and self.wrapper_key in parsed:
                    items = parsed[self.wrapper_key]
                else:
                    items = [parsed]
        elif isinstance(parsed, list):
            if require_wrapper:
                raise exceptions.FormatParseError(
                    f"Content must be a mapping with an '{self.wrapper_key}' key."
                )
            if strict and self.use_wrapper:
                raise exceptions.FormatParseError(
                    "Strict mode requires a wrapper object."
                )
            if not self.allow_top_level_list:
                raise exceptions.FormatParseError("Top-level list is not allowed.")
            items = parsed
        else:
            raise exceptions.FormatParseError(
                f"Expected list or dict, got {type(parsed)}"
            )

        if not isinstance(items, list):
            raise exceptions.FormatParseError(
                "The extractions must be a sequence (list) of mappings."
            )

        for item in items:
            if not isinstance(item, dict):
                raise exceptions.FormatParseError(
                    "Each item in the sequence must be a mapping."
                )
            for k in item.keys():
                if not isinstance(k, str):
                    raise exceptions.FormatParseError(
                        "All extraction keys must be strings (got a non-string key)."
                    )

        return items


# 手动指定模型结果格式化处理器
resolver_params = {"format_handler": CustomFormatHandler()}

# 手动指定模型和提供者
config = lx.factory.ModelConfig(
    model_id="Qwen3-30B-A3B-Instruct-2507",
    provider="OpenAILanguageModel",  # 明确使用 OpenAI
    provider_kwargs={
        "base_url": "http://192.168.11.124:8750/v1",
        "api_key": "abc",
    },
)
model = lx.factory.create_model(config)

# 1. 定义提示词和提取规则
prompt = textwrap.dedent("""\
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context.""")

# 2. 提供示例来指导模型
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO",
                attributes={"emotional_state": "wonder"},
            ),
            lx.data.Extraction(
                extraction_class="emotion",
                extraction_text="But soft!",
                attributes={"feeling": "gentle awe"},
            ),
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Juliet is the sun",
                attributes={"type": "metaphor"},
            ),
        ],
    )
]


def extract(input_text: str):
    # Run the extraction
    result = lx.extract(
        text_or_documents=input_text,
        prompt_description=prompt,
        examples=examples,
        model=model,
        resolver_params=resolver_params,
    )

    lx.io.save_annotated_documents(
        [result], output_name="extraction_results.jsonl", output_dir="."
    )

    # Generate the visualization from the file
    html_content = lx.visualize("extraction_results.jsonl")
    return html_content


if __name__ == "__main__":
    html_content = extract(
        input_text="Lady Juliet gazed longingly at the stars, her heart aching for Romeo"
    )
    with open("index.html", "w") as f:
        if hasattr(html_content, "data"):
            f.write(html_content.data)
        else:
            f.write(html_content)
