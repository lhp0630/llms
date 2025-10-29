# %% [markdown]
# 使用 `pydantic_ai` 与 `pydantic_ai_skills`，通过本地 `.skills` 目录加载技能并运行 Agent。

# %% [markdown]
# 安装依赖
# uv venv
# uv add "pydantic-ai-slim[openai]" "pydantic-ai-skills[git]"

# %%

import os
from pydantic_ai import Agent
from pydantic_ai_skills import SkillsCapability

os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
os.environ["OPENAI_API_KEY"] = "sk-xxx"

capabilities = [
    SkillsCapability(directories=[".skills"]),
]

# from pydantic_ai_skills import GitSkillsRegistry
#
# registry = GitSkillsRegistry("https://github.com/anthropics/skills.git")
#
# capabilities = [
#     SkillsCapability(registries=[registry]),
# ]

agent = Agent(
    model="gpt-4o-mini",
    capabilities=capabilities,
)

result = agent.run_sync("列出所有技能")
print(result)

# %%
