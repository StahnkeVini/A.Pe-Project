# ATLAS — Nova arquitetura de reconhecimento de voz

## O que mudou

O reconhecimento foi dividido em módulos:

- `voice_v2/microphone.py`: seleciona e captura o headset, padroniza o áudio em 16 kHz e gera quadros de 80 ms.
- `voice_v2/wake_word.py`: integra o openWakeWord com um modelo ONNX personalizado para a palavra isolada **ATLAS**.
- `voice_v2/vad_engine.py`: usa Silero VAD para identificar fala sem depender de um limite RMS fixo.
- `voice_v2/segmenter.py`: mantém pré-buffer e fecha segmentos após silêncio.
- `voice_v2/speech_to_text.py`: transcreve em português com Faster-Whisper em CPU INT8.
- `voice_v2/pipeline.py`: coordena os componentes.

A Radeon não é requisito para esta primeira versão. A inferência de voz roda localmente na CPU.

## Instalação no Windows

Use o mesmo ambiente virtual do projeto. Primeiro instale a versão CPU do PyTorch para evitar a instalação acidental de pacotes CUDA:

```powershell
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-voice-v2.txt
```

O restante das dependências do projeto continua em `requirements.txt`. Não reinstale o ambiente inteiro sem necessidade.

## Diagnóstico do headset

Execute:

```powershell
python diagnostics/microphone_test.py
```

O programa lista os dispositivos, mede o nível RMS, o pico e os blocos perdidos. Para testar uma entrada específica:

```powershell
python diagnostics/microphone_test.py --device 3
```

Use o índice mostrado na lista. Para fixá-lo para o ATLAS:

```powershell
$env:ATLAS_MIC_DEVICE="3"
python main.py
```

Também é possível colocar `ATLAS_MIC_DEVICE=3` no arquivo `.env`.

## Modelo personalizado da palavra ATLAS

Os modelos pré-treinados distribuídos com openWakeWord são voltados a palavras e frases em inglês. Não use "hey jarvis" como substituto. O modelo personalizado deve reconhecer a palavra isolada **ATLAS**, pronunciada em português brasileiro.

O local esperado é:

```text
models/atlas.onnx
```

O treinamento pode ser iniciado pelo material de treinamento de modelos customizados do projeto openWakeWord:

https://pypi.org/project/openwakeword/

Ao treinar, gere exemplos com diferentes vozes, velocidades e entonações para "ATLAS", além de exemplos negativos com fala cotidiana e ruído de ventilador/ar-condicionado. O modelo precisa ser testado no headset real antes de elevar sua confiança como detector principal.

### Modo provisório

Até que `models/atlas.onnx` exista, o sistema entra automaticamente em modo provisório: Silero VAD detecta segmentos de fala e Faster-Whisper verifica se a transcrição começa com "ATLAS". Isso mantém a interface utilizável, mas **não equivale à detecção dedicada por palavra-chave** e ainda pode apresentar erros.

Quando o modelo ONNX for instalado no caminho indicado, o pipeline muda automaticamente para o detector independente.

## Ajustes por variável de ambiente

| Variável | Padrão | Função |
|---|---:|---|
| `ATLAS_MIC_DEVICE` | dispositivo padrão | Índice do headset |
| `ATLAS_WAKEWORD_MODEL` | `models/atlas.onnx` | Caminho do modelo customizado |
| `ATLAS_WAKEWORD_THRESHOLD` | `0.65` | Confiança mínima do detector |
| `ATLAS_VAD_THRESHOLD` | `0.52` | Limiar de fala |
| `ATLAS_SILENCE_SECONDS` | `0.75` | Silêncio para concluir um comando |
| `ATLAS_COMMAND_GRACE_SECONDS` | `1.5` | Tempo mínimo após a chamada |
| `ATLAS_MAX_COMMAND_SECONDS` | `12` | Duração máxima de um comando |
| `ATLAS_WHISPER_MODEL` | `small` | Modelo de transcrição |
| `ATLAS_WHISPER_CPU_THREADS` | `4` | Threads de CPU do Whisper |

Os valores devem ser calibrados com testes reais. Não altere vários parâmetros de uma vez.

## Privacidade e limitações

O processamento de reconhecimento é local. Esta implementação não grava automaticamente arquivos de áudio. O Edge TTS existente permanece separado e continua dependendo de conexão com a internet para gerar a voz.
