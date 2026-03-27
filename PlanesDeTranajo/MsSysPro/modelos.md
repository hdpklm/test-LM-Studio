# Modelos para probar

## Análisis de Modelos LLM para QA (v1.70)

Este documento resume la investigación sobre los mejores modelos "Small Language Models" (SLM) enfocados en responder preguntas sobre textos cortos (QA) con alta velocidad.

### Top 5 Modelos Recomendados

| Puesto | Modelo | Parámetros | t/s (Est.) | Fortalezas |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Qwen 2.5 7B-Instruct** | 7.6B | ~100-140 | El más inteligente en su rango. Excelente en español. |
| 2 | **Llama 3.2 3B-Instruct** | 3.2B | ~150-250 | Estándar de la industria, muy fiable y rápido. |
| 3 | **Phi 3.5 mini-instruct** | 3.8B | ~120-180 | Lógica superior para textos complejos (Microsoft). |
| 4 | **Gemma 3 4B-IT** | 4.0B | ~130-200 | Nueva arquitectura Google, precisión en extracción. |
| 5 | **DeepSeek-R1-Distill-Qwen-7B** | 7.0B | ~80-120 | Razonamiento profundo (CoT) para evitar alucinaciones. |

### Opiniones de la Comunidad e Insights

- **Qwen 2.5** es actualmente el favorito de la comunidad para tareas locales debido a su gran rendimiento en idiomas distintos al inglés y su baja tasa de alucinaciones.
- **Llama 3.2 3B** se destaca por su "seguimiento de instrucciones" (instruction following), siendo muy difícil que se salga del formato pedido.
- **Phi 3.5** es el que mejor "entiende" conceptos difíciles en textos densos, a pesar de ser muy pequeño.

### Resumen de Rendimiento
Para textos de 10 líneas y 5 preguntas, todos estos modelos responden en menos de 1-2 segundos en una GPU moderna (RTX 3060+).

---
---
---

## propmt:
```txt
necesito que me busques y compares modelos LLM que sean pequeños, pero que funcionen bien.
 
lo unico que necesito que que puedan responder preguntas pasandoles un texto.
 
es decir, tengo un texto de 10 lineas, unas 5 preguntas, y necesito que me responda a esas preguntas lo mejor posible.
 
puntos favorables:
1. lo mas pequeño posible
2. que solo hable un idioma
3. que tenga muy buen ratio de respuestas correctas
4. que genere mas de 100 token/s
5. contexto moderadamente mediano, no necesito que tenga millones de token de ventana de contexto
 
puntos que no me interesan:
1. que sepa mucho de todo, o que sea especialista en algun tema
2. que sea muy grande, y no pueda caber en una GPU medianamente moderna en un PC casero
 
 
genera una lista con unos 20 modelos de los que mejor cumplen con lo que necesito

generame la tabla con los mejores LLM que encontraste, en markdown dentro de un bloque de codigo, pero no utilices "```" en el markdown, para que no se cierre el bloque de codigo
```

## chatgpt:

| Modelo                | Idiomas                       | Parámetros (B)      | VRAM FP16 (GB)  | tokens/s (RTX3060) | QA (SQuAD2 F1 / Comentario)          |
|-----------------------|------------------------------|---------------------|-----------------|--------------------|-------------------------------------|
| Salamandra-2B-Inst    | 35 eur. idiomas (incl. es)【61†L1-L4】 | 2.25【48†L125-L130】  | ~6              | ~100               | Competitiva multilingüe【38†L25-L28】 |
| Salamandra-7B-Inst    | 35 eur. idiomas (incl. es)【46†L114-L122】 | 7.77【46†L125-L130】  | ~16             | ~60                | Competitiva multilingüe【38†L25-L28】 |
| Cecilia-2B-Inst       | Español (Cuba)【73†L56-L59】      | 2.0【73†L99-L101】   | ~4              | ~80                | Especializado en español cubano     |
| Qwen3-4B-Inst         | >100 idiomas (incl. es)【59†L112-L120】  | 4.0【59†L30-L36】   | ~8              | ~80               | 0.71 (SQuAD-2)【71†L183-L186】        |
| Meta Llama-3.2-1B-Inst| Multilingüe【55†L127-L133】         | ≈1.0              | ~2              | ~200               | Alta tras fine-tuning【71†L247-L251】 |
| SmolLM-1.7B           | Inglés【67†L72-L80】             | 1.7【67†L72-L80】    | ~4              | ~150               | *Estado del arte*【67†L72-L80】       |

## gemini:
| Modelo | Parámetros | Velocidad Proyectada | Ocupación VRAM | Enfoque Principal |
| :--- | :--- | :--- | :--- | :--- |
| Salamandra 2B Instruct | 2.0B | > 120 t/s | ~1.5 GB | Alta especialización nativa en español y lenguas europeas |
| Llama 3.2 1B Instruct | 1.23B | > 190 t/s | ~0.9 GB | Altísima velocidad, seguimiento estricto de instrucciones |
| Llama 3.2 3B Instruct | 3.21B | > 100 t/s | ~2.2 GB | Razonamiento deductivo avanzado para comprensión lectora |
| Qwen 3 0.6B | 0.6B | > 250 t/s | ~0.5 GB | Velocidad extrema, ideal para responder ceñido al texto |
| Qwen 3 1.5B | 1.5B | > 180 t/s | ~1.2 GB | Equilibrio ideal entre velocidad y extracción de respuestas |
| DeepSeek-R1-Distill-Qwen-1.5B | 1.5B | > 160 t/s | ~1.2 GB | Razonamiento profundo antes de responder (evita alucinaciones) |
| Qwen 2.5 3B Instruct | 3.0B | > 110 t/s | ~2.0 GB | Analista de texto excepcional con soporte nativo de español |
| Gemma 3 1B Instruct | 1.0B | > 180 t/s | ~0.8 GB | Atención entrelazada para captar todos los detalles del texto corto |
| Gemma 3 4B Instruct | 4.0B | > 80 t/s | ~2.6 GB | Estructuración muy robusta y mitigación estricta de invenciones |
| SmolLM3 3B | 3.0B | > 110 t/s | ~2.0 GB | Modo de pensamiento dual y alta fluidez multilingüe |
| SmolLM2 1.7B Instruct | 1.7B | > 150 t/s | ~1.3 GB | Estabilidad extrema para ejecución constante en dispositivos locales |
| Ministral 3B | 3.0B | > 110 t/s | ~2.0 GB | Excelente en inferencia rápida sin conexión a internet |
| IBM Granite 3.1 2B Instruct | 2.0B | > 140 t/s | ~1.5 GB | Arquitectura diseñada para detectar y evitar alucinaciones semánticas |
| IBM Granite 3.1 1B-A400M | 1.0B | > 220 t/s | ~0.8 GB | Arquitectura MoE que usa poca memoria activa logrando latencia mínima |
| Falcon 3 1B Instruct | 1.0B | > 190 t/s | ~0.8 GB | Vocabulario concentrado en solo 4 idiomas (incluye español nativo) |
| Falcon 3 3B Instruct | 3.0B | > 110 t/s | ~2.0 GB | Alta capacidad de entendimiento de sentido común en contextos cortos |
| Stable LM 2 1.6B | 1.6B | > 160 t/s | ~1.2 GB | Extracción rapidísima de información estructurada |
| Phi-3.5-mini Instruct | 3.8B | > 90 t/s | ~2.6 GB | Lógica impecable derivada de su entrenamiento con datos sintéticos |
| BitNet b1.58 3B (2B4T) | 2.4B | > 200 t/s | ~1.3 GB | Operaciones de 1 bit para máximo ahorro de energía y recursos |
| OLMo 2 1B | 1.0B | > 190 t/s | ~0.8 GB | Ventana de contexto pequeña por defecto para máxima concentración |

## claude:
### Comparativa LLMs pequeños para QA sobre textos cortos (RTX 3070 8GB)

#### Top Tier — Mejor relación calidad/VRAM (3B–4B)

| # | Modelo | Params | VRAM Q4_K_M | Contexto | MMLU | Velocidad (tok/s) | Idiomas | Ollama | Nota |
|---|--------|--------|-------------|----------|------|--------------------|---------|--------|------|
| 1 | **BLING-Phi-3-GGUF** | 3.8B | ~3.5 GB | 128K | 69 | 60–80 | EN | Si | 100/100 RAG benchmark, 0 alucinaciones |
| 2 | **Qwen3-4B** | 4.0B | ~3.0 GB | 32K | ~69 | 60–80 | 119 | Si | Supera Qwen2.5-7B en QA, modo /no_think |
| 3 | **Phi-4-mini-instruct** | 3.8B | ~3.5 GB | 128K | 67 | 60–80 | 24+ | Si | 81.2 BoolQ, 83.7 ARC-Challenge |
| 4 | **Gemma 3 4B-IT** | 4.0B | ~4.0 GB | 128K | ~70 | 50–70 | 140+ | Si | Iguala Gemma 2 27B, multimodal |

#### Tier 2 — Máxima calidad QA (7B–8B, ajustados en VRAM)

| # | Modelo | Params | VRAM Q4_K_M | Contexto | MMLU | Velocidad (tok/s) | Idiomas | Ollama | Nota |
|---|--------|--------|-------------|----------|------|--------------------|---------|--------|------|
| 5 | **Qwen3-8B** | 8.0B | ~6.5 GB | 128K | ~75 | 30–45 | 119 | Si | #1 en zero-shot QA sub-10B |
| 6 | Qwen2.5-7B-Instruct | 7.6B | ~5.5 GB | 128K | 74 | 35–45 | 29+ | Si | Ecosistema maduro, estable |
| 7 | Mistral 7B v0.3 | 7.3B | ~5.8 GB | 32K | 63 | ~63 | Multi | Si | 63 tok/s medido en RTX 3070 |
| 8 | Gemma 2 9B-IT | 9.2B | ~7.0 GB | 8K | 71 | 25–40 | EN | Si | Ajustado, poco margen VRAM |

#### Tier 3 — Ultra-rápidos (sub-2B)

| # | Modelo | Params | VRAM Q4_K_M | Contexto | MMLU | Velocidad (tok/s) | Idiomas | Ollama | Nota |
|---|--------|--------|-------------|----------|------|--------------------|---------|--------|------|
| 9 | **Qwen3-1.7B** | 1.7B | ~1.5 GB | 32K | 61 | 80–100 | 119 | Si | Iguala Qwen2.5-3B |
| 10 | SmolLM2-1.7B | 1.7B | ~1.5 GB | 8K | ~49 | 80–100 | EN | Si | 11T tokens de training |
| 11 | Qwen2.5-1.5B-Instruct | 1.5B | ~1.5 GB | 128K | 58 | 80–100 | 29+ | Si | Buen baseline multilingüe |
| 12 | BLING-Qwen-1.5B | 1.5B | ~1.5 GB | 4K | ~58 | 80–100 | EN | Si | ~95/100 RAG benchmark |
| 13 | Llama 3.2-1B | 1.2B | ~2.0 GB | 128K | 49 | 100–150 | 8 | Si | OK para QA simple |
| 14 | StableLM-2-1.6B | 1.6B | ~1.5 GB | 4K | 42 | 80–100 | 7 | Si | Superado por Qwen3-1.7B |
| 15 | H2O-Danube2-1.8B | 1.8B | ~1.5 GB | 8K | 40 | 80–100 | EN | Si | Funcional pero inferior |
| 16 | TinyLlama-1.1B | 1.1B | ~0.8 GB | 2K | 26 | 150+ | EN | Si | Solo viable con BLING fine-tune |

#### Tier 4 — Intermedios (2B–3B)

| # | Modelo | Params | VRAM Q4_K_M | Contexto | MMLU | Velocidad (tok/s) | Idiomas | Ollama | Nota |
|---|--------|--------|-------------|----------|------|--------------------|---------|--------|------|
| 17 | Llama 3.2-3B | 3.2B | ~3.6 GB | 128K | 63 | 60–90 | 8 | Si | Mejor modelo para fine-tuning QA |
| 18 | Ministral 3 3B | 3.0B | ~3.5 GB | 128K | ~65 | 80–120 | 40+ | Si | Nuevo, pocos benchmarks aún |
| 19 | RWKV-7-2.9B | 2.9B | ~2.5 GB | Infinito | ~55 | 70–90 | Multi | Parcial | RNN, memoria constante, degrada bajo Q5 |
| 20 | Phi-2 | 2.7B | ~2.5 GB | 2K | 57 | 80–120 | EN | Parcial | Superado por Phi-4-mini |
| 21 | H2O-Danube3-4B | 4.0B | ~3.0 GB | 8K | ~62 | 50–70 | EN | Si | OK pero inferior a Qwen3-4B |

#### Recomendación rápida

- **Mejor QA puro**: BLING-Phi-3-GGUF (Q8_0, ~5.5GB) → 100/100 sin alucinaciones
- **Mejor general + QA**: Qwen3-4B (Q6_K, ~4GB) → flexible, rápido, multilingüe
- **Máxima calidad**: Qwen3-8B (Q4_K_M, ~6.5GB) → #1 zero-shot QA
- **Máxima velocidad**: Qwen3-1.7B (Q8_0, ~2GB) → 80-100 tok/s, calidad sorprendente

#### Tips de cuantización para RTX 3070

- Q4_K_M: ~95% calidad original, mínimo recomendado para QA
- Q6_K: ~98% calidad, sweet spot si cabe en VRAM
- Q8_0: ~99.9% calidad, ideal para modelos sub-4B en 8GB
- Q3 o inferior: degradación notable, evitar para QA factual
- Flash attention ON siempre (OLLAMA_FLASH_ATTENTION=1)

## qween:
| # | Modelo | Parámetros | Idioma Principal | Ventana Contexto | Velocidad Est. (>100 t/s)* | Calidad QA | Notas Clave |
|---|---|---|---|---|---|---|---|
| 1 | Llama-3.2-3B-Instruct | 3.2B | Inglés | 128k | Muy Alta | Excelente | El rey actual de eficiencia/calidad. Ideal base para fine-tuning. |
| 2 | Phi-3.5-mini-instruct | 3.8B | Inglés | 128k | Muy Alta | Sobresaliente | Razonamiento superior a su tamaño. Microsoft. |
| 3 | Gemma-2-2b-it | 2.6B | Inglés | 8k | Extrema | Muy Buena | Arquitectura eficiente de Google. Muy rápido. |
| 4 | Qwen2.5-3B-Instruct | 3B | Multilingüe* | 32k | Muy Alta | Excelente | Soporta muchos idiomas, pero brilla en inglés. |
| 5 | Mistral-7B-Instruct-v0.3 | 7B | Inglés/Francés | 32k | Alta (con cuantización) | Muy Robusta | El estándar de la industria para 7B. Muy maduro. |
| 6 | StableLM-2-1.6B | 1.6B | Inglés | 4k-32k | Extrema | Buena | Sorprendentemente capaz para ser tan pequeño. |
| 7 | TinyLlama-1.1B-Chat-v1.0 | 1.1B | Inglés | 2k | Extrema | Aceptable | El más ligero. Bueno si la GPU es muy limitada. |
| 8 | Qwen2.5-1.5B-Instruct | 1.5B | Multilingüe* | 32k | Extrema | Muy Buena | Mejor ratio tamaño/calidad en sub-2B. |
| 9 | Phi-3-small-8k-instruct | 7B | Inglés | 8k | Alta | Excelente | Versión "pequeña" de Phi optimizada para velocidad. |
| 10 | Gemma-2-9b-it | 9B | Inglés | 8k | Media-Alta | Superior | Si tu GPU lo aguanta, tiene la mejor calidad de la lista. |
| 11 | Llama-3.2-1B-Instruct | 1.2B | Inglés | 128k | Extrema | Buena | Para contextos extremos en hardware mínimo. |
| 12 | SmolLM2-1.7B-Instruct | 1.7B | Inglés | 8k | Extrema | Buena | Diseñado específicamente para correr en local/móvil. |
| 13 | InternLM2.5-1.8B-Chat | 1.8B | Inglés/Chino | 32k | Extrema | Muy Buena | Arquitectura moderna, muy eficiente en tokens. |
| 14 | MiniCPM3-4B | 4B | Multilingüe* | 128k | Muy Alta | Excelente | Diseñado para igualar a modelos de 7B con menos params. |
| 15 | OpenHermes-2.5-Mistral-7B | 7B | Inglés | 8k | Alta | Muy Alta | Fine-tuneado específicamente para seguir instrucciones. |
| 16 | Dolphin-2.9-Llama-3-8B | 8B | Inglés | 8k | Alta | Muy Alta | Sin censura, excelente para tareas directas de QA. |
| 17 | Starling-LM-7B-beta | 7B | Inglés | 8k | Alta | Muy Alta | Entrenado con RLHF para ser muy preciso en respuestas. |
| 18 | NanoLLaMA-1.5B | 1.5B | Inglés | 2k | Extrema | Aceptable | Variante ultra-optimizada de Llama para recursos mínimos. |
| 19 | RecurrentGemma-2b-it | 2.6B | Inglés | 8k+ | Extrema | Buena | Usa arquitectura híbrida (RNN+Transformer) para velocidad. |
| 20 | MobileLLaMA-1.4B | 1.4B | Inglés | 2k | Extrema | Aceptable | Diseñado originalmente para móviles, vuela en PC. |

## grok:
| # | Modelo                          | Parámetros | VRAM aprox. (Q4) | Velocidad estimada (t/s) | Contexto | Idioma principal          | Notas para tu caso (QA texto corto 10 líneas + 5 preguntas) |
|---|---------------------------------|------------|------------------|---------------------------|----------|---------------------------|-------------------------------------------------------------|
| 1 | Qwen3.5-0.8B-Instruct          | 0.8B      | ~1 GB           | 250-400+                 | 128K    | Multilingual (fuerte ES) | El más pequeño con excelente fidelidad y cero alucinaciones en texto corto |
| 2 | Gemma-3-1B-Instruct            | 1B        | ~1.5 GB         | 300-500+                 | 128K    | Multilingual (buen ES)   | Ultra-rápido, máxima velocidad y muy preciso en extracción directa |
| 3 | Llama-3.2-1B-Instruct          | 1B        | ~1 GB           | 250-400                  | 128K    | Multilingual (buen ES)   | Ideal para hardware mínimo, responde con altísima precisión al texto |
| 4 | Gemma-2-2B-IT                  | 2B        | ~2 GB           | 180-300                  | 8K      | Inglés + fuerte ES       | Uno de los mejores pequeños en español y fidelidad a contexto corto |
| 5 | SmolLM-1.7B-Instruct           | 1.7B      | ~1.5 GB         | 200-350                  | 32K     | Inglés principal (buen ES) | Muy compacto y con gran ratio de respuestas correctas |
| 6 | Phi-4-mini-Instruct            | 3.8B      | ~3 GB           | 140-220                  | 128K    | Multilingual (fuerte ES) | Mejor equilibrio calidad/velocidad para QA fiel al texto |
| 7 | Llama-3.2-3B-Instruct          | 3B        | ~2 GB           | 150-250                  | 128K    | Multilingual (buen ES)   | Excelente instruction-following y respuestas 100% basadas en el texto |
| 8 | Qwen3-4B-Instruct              | 4B        | ~3 GB           | 130-200                  | 128K    | Multilingual (fuerte ES) | Muy fuerte en tareas estructuradas y extracción precisa |
| 9 | Gemma-3-4B-Instruct            | 4B        | ~3 GB           | 130-200                  | 128K    | Multilingual (buen ES)   | Alta precisión y velocidad aún muy alta |
|10 | Qwen3-7B-Instruct              | 7B        | ~5 GB           | 100-180                  | 128K    | Multilingual (excelente ES) | Mejor precisión general manteniendo >100 t/s |
|11 | Mistral Small 3 7B-Instruct    | 7B        | ~4.5 GB         | 110-170                  | 128K    | Multilingual (fuerte ES) | Muy fiable y rápido en respuestas correctas |
|12 | Phi-3.5-mini-Instruct          | 3.8B      | ~2.5 GB         | 140-220                  | 128K    | Multilingual             | Referencia en razonamiento pequeño y fidelidad |
|13 | Llama-3.2-3B-Instruct (var.)  | 3B        | ~2 GB           | 150-250                  | 128K    | Multilingual (buen ES)   | Versión optimizada para texto corto |
|14 | Marco-LLM-ES-7B                | 7B        | ~4.5 GB         | 100-160                  | 32K     | Español nativo           | Fine-tune específico en español, ideal si quieres monolingüe |
|15 | Ministral-3-3B-Instruct        | 3B        | ~2.5 GB         | 150-250                  | 32K     | Multilingual             | Muy eficiente y preciso en QA |
