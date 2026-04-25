User's AI provider is Chutes (https://llm.chutes.ai/v1). API key is in ~/.hermes/config.yaml under model.api_key. Can query available models at https://llm.chutes.ai/v1/models with that key. Current default model: zai-org/GLM-5.1-TEE. Chutes has ~43 models, mostly mainstream (DeepSeek, Qwen, Mistral, GLM, NousResearch). No dedicated uncensored/NSFW models on Chutes; least restrictive are NousResearch/Hermes-4-14B and NousResearch/DeepHermes-3-Mistral-24B-Preview.
§
User's stock watchlist is stored in the resource-investing-research skill: ~/.hermes/skills/research/resource-investing-research/SKILL.md - has tables for copper, uranium, and solar stocks. Don't create new CSV files — update this skill instead.
§
Edge skill debugging limitation: browser_console cannot execute JavaScript functions - it's only for DOM snapshots. Must use curl to verify HTML content is served correctly.
§
Image reading fallback: vision_analyze sometimes fails on screenshots. Fallback: install tesseract-ocr + pytesseract + Pillow, then run `tesseract /path/to/image.png stdout` to OCR. Already installed on this machine.
§
Vision was failing because provider:auto fell back to GLM-5.1-TEE (text-only model). Fixed by setting auxiliary.vision to Qwen/Qwen2.5-VL-32B-Instruct on Chutes in config.yaml. OCR (tesseract+pytesseract+Pillow) still available as fallback.
§
Chutes model capability ranking (Apr 2026, Arena ELO): GLM-5.1=1472(#15), Qwen3.5-397B=1446(#38), Kimi-K2.5=1451(#31), GLM-5=1456(#25), DeepSeek-V3.2=1424(#58), DeepSeek-R1-0528=1422(#64), gpt-oss-120b=1353(#143). Full ranking saved at ~/chutes-models-ranking.md. GLM-5.1 is best default (Arena Code #4). For vision: Qwen2.5-VL-32B. For unrestricted: NousResearch/Hermes-4-14B.