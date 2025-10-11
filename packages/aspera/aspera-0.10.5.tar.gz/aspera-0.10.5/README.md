# 🧠 ASPERA — Linguaggio Cognitivo Ibrido

<div align="center">

<img src="assets/logo.png" alt="ASPERA Logo" width="400"/>

**Un framework innovativo per sistemi cognitivi che unisce ragionamento simbolico e intelligenza artificiale**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BUSL--1.1-blue)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-37%2F39%20passing-brightgreen)](aspera/tests/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Powered-orange)](https://groq.com)
[![Product Status](https://img.shields.io/badge/status-PRODUCTION%20READY-success)](STARTUP_ROADMAP.md)
[![Roadmap](https://img.shields.io/badge/roadmap-24%2F24%20(100%25)-brightgreen)](STARTUP_ROADMAP.md)

[🚀 Quick Start](#-quick-start) • [💡 Innovation](docs/INNOVATION_IMPACT.md) • [🏗️ Architecture](docs/ARCHITECTURE.md) • [📄 Paper](papers/ASPERA_NeurIPS_Draft.md) • [📚 Docs](docs/quickstart.md) • [🧪 Type Checking](docs/TYPE_CHECKING.md) • [🎯 Threshold Learning](docs/LEARNING_THRESHOLDS.md) • [🔌 Plugins](docs/PLUGINS.md) • [📘 Onboarding DSL](docs/ONBOARDING_DSL.md) • [🤝 Contributing](#-contributing)

</div>

---

## 💡 What is ASPERA?

> **"ASPERA is the Python of AI Orchestration"**

Just as Python became the universal language for data science, **ASPERA is the foundational language for building cognitive AI systems**.

**ASPERA** combines:

- 🧮 **Symbolic Reasoning** - Fast, cheap, deterministic logic (80% of decisions)
- 🤖 **LLM Orchestration** - Groq-powered intelligence when needed (20% of decisions)
- 🧠 **Memory Systems** - Episodic and semantic memory for context
- 🎯 **Policy Intentions** - Goal-oriented behavior strategies
- 📊 **Complete Audit Trail** - 100% explainability for compliance (FDA/SEC/GDPR)

### 🚀 Why ASPERA?

I sistemi AI tradizionali soffrono di due limiti:
1. **LLM puri**: potenti ma opachi, non tracciabili, non deterministici
2. **Sistemi simbolici**: rigidi, limitati, incapaci di gestire ambiguità

**ASPERA** risolve questo dilemma attraverso un'**architettura ibrida** che:
- ✅ Mantiene la trasparenza del ragionamento simbolico
- ✅ Sfrutta la flessibilità dei LLM per situazioni complesse
- ✅ Garantisce audit trail completo di ogni decisione
- ✅ Permette policy-based control sui comportamenti

Include parser BNF completo, runtime orchestratore, integrazione Groq LLM, SDK Python e UI React interattiva.

## 🎯 Caratteristiche Principali

- **Linguaggio Cognitivo Dichiarativo**: Sintassi leggibile per definire concetti, associazioni, stati, inferenze e intenzioni
- **Runtime Ibrido**: Orchestrazione tra reasoner simbolico, memoria episodica/semantica e LLM
- **Integrazione Groq**: Adapter per modelli LLM avanzati con spiegazioni naturali
- **SDK Python**: API pulite per sviluppatori
- **Web Editor & Playground**: UI React moderna con editor Monaco e runtime interattivo
- **Tracciabilità Completa**: Audit log di ogni inferenza per trasparenza e debug
- **Estensibile**: Architettura modulare per nuovi adapter LLM e feature linguistiche
- **🆕 Enterprise-Grade Error Messages**: Parser con error messages ricchi, "did you mean" suggestions, esempi di codice ([docs](docs/PARSER_ERROR_MESSAGES.md))
- **🆕 Macro System**: Template riutilizzabili per DRY code, 5 built-in macros + custom macros ([docs](docs/MACRO_SYSTEM.md))
 - **🆕 Resilienza Enterprise LLM**: Circuit breaker, retry con backoff, cache LLM, graceful degradation (Groq reale stabile)

## 🚀 Quick Start

### Prerequisiti

- Python 3.10+
- Node.js 18+ (per UI)
- Account Groq con API key (https://console.groq.com)

### Installazione

```bash
# 1. Clone e setup ambiente
cd aspera
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura variabili d'ambiente
cp .env.example .env
# Edita .env e aggiungi la tua GROQ_API_KEY
```

### Uso CLI

```bash
# Parse un file .aspera
python aspera_cli.py parse aspera/lang/examples/empathetic.aspera -o ast.json

# Run con auto-detect (RACCOMANDATO - usa Groq se GROQ_API_KEY configurata)
python aspera_cli.py run --aspera aspera/lang/examples/empathetic.aspera --signals examples/signals.json

# Run forzando Groq
python aspera_cli.py run --aspera aspera/lang/examples/empathetic.aspera --signals examples/signals.json --mode groq

# Run con mock LLM (solo per testing, no API key needed)
python aspera_cli.py run --aspera aspera/lang/examples/empathetic.aspera --signals examples/signals.json --mode mock

# Valida un AST
python aspera_cli.py validate ast.json
```

### Plugin: installazione, discovery e uso (incluso Gemini)

```bash
# Installa plugin esterni (esempi)
python -m pip install -e plugins/aspera-vector-weaviate
python -m pip install -e plugins/aspera-llm-openai
python -m pip install -e plugins/aspera-llm-gemini

# Scopri e lista plugin disponibili
python aspera_cli.py plugins discover
python aspera_cli.py plugins list
```

Uso programmatico con `PluginManager`:

```python
from aspera.plugins.plugin_interface import PluginManager

pm = PluginManager()
pm.discover_plugins()

llm = pm.get_plugin("openai_llm") or pm.get_plugin("gemini_llm")
if llm:
    llm.initialize({"model": "gpt-4o-mini", "temperature": 0.7})
    print(llm.generate_inference(context={}, signals={}, rules=["if a then b"]))

vec = pm.get_plugin("weaviate_vector")
if vec:
    vec.initialize({"url": "http://localhost:8080", "class_name": "AsperaVector"})
    vec.save("demo", "hello")
    print("Loaded:", vec.load("demo"))
```

### 🔌 Plugins: installazione rapida

```bash
# Installa plugin pubblici (LLM OpenAI e Vector Weaviate)
python -m pip install aspera-llm-openai aspera-vector-weaviate

# Scopri e lista plugin disponibili
python aspera_cli.py plugins discover
python aspera_cli.py plugins list
```

#### Esempio programmatico (PluginManager)

```python
from aspera.plugins.plugin_interface import PluginManager

pm = PluginManager()
pm.discover_plugins()

# OpenAI LLM (richiede OPENAI_API_KEY nell'ambiente)
llm = pm.get_plugin("openai_llm")
if llm:
    llm.initialize({"model": "gpt-4o-mini", "temperature": 0.7})
    res = llm.generate_inference(context={}, signals={}, rules=["if a then b"])
    print("LLM result:", res)

# Weaviate Vector Storage
vec = pm.get_plugin("weaviate_vector")
if vec:
    vec.initialize({"url": "http://localhost:8080", "class_name": "AsperaVector"})
    vec.save("demo", "hello")
    print("Loaded:", vec.load("demo"))
```

### LSP (Language Server) Setup

Per abilitare diagnostica in editor e completamento base:

```powershell
# Avvio server LSP (stdin/stdout)
python -m aspera.tools.lsp_server
# oppure, se installato come script
aspera-lsp
```

In VS Code, configura un client LSP generico puntando al comando sopra. Aggiungi anche `.vscode/settings.json` con:

```json
{
  "ltex.language": "it-IT",
  "python.analysis.diagnosticMode": "openFilesOnly"
}
```

Funzionalità attuali: diagnostica parser in tempo reale, completion basica (`concept.`, `signals.`, `state.`, `threshold(`).

### Telemetry (OpenTelemetry)

ASPERA emette traces/metrics OTLP (HTTP) per observe/step/decide. Per provare in locale:

```powershell
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
python aspera_cli.py run --aspera agents\enterprise\ecommerce_conversion_optimizer\conversion_optimizer.aspera --signals examples\signals_ecommerce.json --mode mock
```

Metriche principali: `aspera_observe_total`, `aspera_step_total`, `aspera_decide_total`. Configura il tuo collector OTLP (es. OpenTelemetry Collector) e visualizza in Grafana/Tempo.

### Smoke test con Groq (tutti gli agent)

```powershell
$code = @"
import sys, os, json
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
from aspera.sdk.client import create_engine, run_observation
files = [str(p) for p in Path('agents').rglob('*.aspera')]
report = []
for f in files:
    print('==> ', f)
    eng = create_engine(f, use_mock_llm=False, auto_detect=True, enable_cache=True)
    res = run_observation(eng, {}, {}, True)
    report.append({'agent': f, 'actions': res['actions'], 'explanation': res['explanation']})
with open('SMOKE_REPORT_GROQ.json','w', encoding='utf-8') as fp:
    json.dump(report, fp, ensure_ascii=False, indent=2)
print('Saved: SMOKE_REPORT_GROQ.json')
"@
$code | python -
```

### Uso Docker

```bash
# Build e avvia tutti i servizi
docker-compose up -d

# Accedi all'UI
# http://localhost:3000

# API backend
# http://localhost:8000/docs
```

### Uso SDK

```python
from aspera.sdk.client import create_engine, run_observation

# Carica un programma Aspera
engine = create_engine("examples/empathetic.aspera")

# Esegui osservazione
signals = {
    "coerenza_comportamento": 0.7,
    "trasparenza": 0.8
}
context = {
    "experiences": {"shared": 5},
    "interaction_count": 10
}

result = run_observation(engine, signals, context)

print("Azioni:", result["actions"])
print("Spiegazione:", result["explanation"])
print("Trace:", result["audit_trace"])
```

## 📖 Struttura Progetto

```
aspera/
├─ README.md
├─ LICENSE
├─ pyproject.toml
├─ requirements.txt
├─ .env.example
├─ aspera_cli.py                    # CLI principale
├─ aspera/
│  ├─ __init__.py
│  ├─ lang/                         # Definizione linguaggio
│  │  ├─ grammar.aspera.bnf         # Grammatica BNF
│  │  ├─ parser.py                  # Parser Python
│  │  ├─ ast_schema.json            # JSON Schema AST
│  │  └─ examples/                  # Esempi .aspera
│  ├─ runtime/                      # Runtime cognitivo
│  │  ├─ engine.py                  # CognitiveEngine
│  │  ├─ symbolic.py                # Reasoner simbolico
│  │  ├─ memory.py                  # Memoria episodica/semantica
│  │  ├─ policy.py                  # Policy executor
│  │  └─ llm_adapters/
│  │      └─ groq_adapter.py        # Groq integration
│  ├─ sdk/                          # SDK pubblico
│  │  ├─ client.py
│  │  └─ utils.py
│  ├─ web/                          # Web stack
│  │  ├─ api.py                     # FastAPI backend
│  │  └─ ui/                        # React frontend
│  └─ tests/                        # Test suite
├─ docs/                            # Documentazione
├─ training/                        # Training plan & scripts
├─ datasets/                        # Dataset examples
└─ infra/                           # Docker & CI
```

## 🧠 Linguaggio Aspera

### Sintassi Base

```aspera
// Definisci un concetto
concept "fiducia" {
  definition: "credenza nella coerenza e buona volontà dell'altro";
  signals: ["coerenza_comportamento", "trasparenza", "esperienze_condivise"];
  baseline: 0.5;
}

// Associa concetti
associate "fiducia" -> "cooperazione" {
  weight: 0.8;
  bidirectional: true;
}

// Stato del sistema
state {
  mood: "neutral";
  energy_level: 0.7;
  interaction_phase: "initial";
}

// Regola di inferenza
inference "valuta_fiducia" {
  when: signals.coerenza_comportamento > 0.6 and experiences.shared > 3;
  then: increase concept:"fiducia" by 0.2;
  confidence: 0.8;
}

// Intenzione strategica
intention "costruire_cooperazione" {
  priority: high;
  strategy:
    - if concept:"fiducia" < 0.4 -> action: "aumenta_trasparenza"
    - else -> action: "proponi_collaborazione_graduale";
}

// Template spiegazione
explain {
  format: "human";
  template: "Credo che tu sia [interpretation] perché ho osservato [evidence].";
}
```

## 🔧 Architettura Runtime

### CognitiveEngine

Il motore cognitivo orchestra tre componenti:

1. **Symbolic Reasoner**: Applica regole deterministiche (inferenze)
2. **LLM Adapter**: Gestisce ragionamento complesso e spiegazioni naturali
3. **Memory System**: Mantiene contesto episodico e semantico

### Flusso di Esecuzione

```
observe(signals, context) → step() → decide() → explain()
     ↓                         ↓         ↓          ↓
  Context              Apply Rules   Select    Generate
  Update               Update State  Actions   Explanation
```

## 🤖 Integrazione Groq

### Configurazione

```bash
# .env
GROQ_API_KEY=gsk_...
ASPERA_ENV=development
ASPERA_DB_URL=sqlite:///aspera.db
```

### Prompt Templates & Resilienza

ASPERA include template ottimizzati per e resilienza LLM:
- **Inference**: Produce JSON strutturato con changes, confidence, rationale
- **Explain**: Genera spiegazioni empatiche seguendo template personalizzati
- **Policy**: Traduce strategie in azioni prioritizzate
 - **Resilienza**: Circuit breaker (soglia 3, timeout 30s) + retry (3 tentativi, backoff 2x) + cache dei risultati

## 📊 Training & Valutazione

Vedi `training/plan.md` per dettagli su:

- **Dataset**: Conversazioni annotate, segnali multimodali, rationales umane
- **Distillation**: Supervised fine-tuning + RLHF esteso
- **Metriche**: EmpathyScore, CoherenceConsistency, RationaleQuality, TaskSuccess, SafetyScore
- **Synthetic Generator**: Script per generare 50+ scenari toy

## 🛡️ Sicurezza & Ethics

- **Audit Log Obbligatorio**: Ogni inferenza tracciata (rule, inputs, confidence, outputs)
- **Human-in-the-Loop**: Azioni ad alto impatto richiedono conferma umana
- **Output Sanitization**: Blacklist/whitelist per prevenire contenuti dannosi
- **Privacy**: No secrets in code, gestione retention dati documentata

## 🧪 Testing

```bash
# Run test suite
pytest aspera/tests/ -v

# Con coverage
pytest aspera/tests/ --cov=aspera --cov-report=html

# Test specifici
pytest aspera/tests/test_parser.py -k "test_parse_concept"
```

## 📚 Documentazione Completa

- [Grammar Reference](docs/grammar_reference.md)
- [AST Schema](docs/ast_schema.md)
- [Runtime API](docs/runtime_api.md)
- [SDK Guide](docs/sdk_guide.md)
- [Training Plan](training/plan.md)
- [Dataset Schema](datasets/README.md)

## 🎬 Demo Video Script

1. **Intro (30s)**: Mostra editor con esempio empathetic.aspera
2. **Parse (30s)**: CLI parse → mostra AST JSON
3. **Run Mock (1m)**: Esegui con mock LLM, mostra trace
4. **Run Groq (1m)**: Esegui con Groq, mostra spiegazione naturale
5. **UI Playground (1m)**: Editor interattivo, modifica signals live
6. **Audit & Safety (1m)**: Mostra log tracciabilità
7. **Wrap-up (30s)**: Architettura e next steps

## 🤝 Contributing

ASPERA è un progetto in evoluzione. Per contribuire:

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit con messaggi descrittivi
4. Push e apri Pull Request

## 📄 License

MIT License - vedi file `LICENSE`

## 👤 Author

**RTH Italia** ideato da **Christian Quintino De Luca**

## 🔗 Links

- [Groq Console](https://console.groq.com)
- [Documentation](docs/)
- [Examples](aspera/lang/examples/)

---

**ASPERA** — *Thinking, Transparently*

