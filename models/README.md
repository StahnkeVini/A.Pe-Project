# Modelo de ativação do ATLAS

Coloque nesta pasta o modelo ONNX personalizado treinado para reconhecer a palavra **ATLAS**:

`models/atlas.onnx`

O arquivo não é incluído no pacote porque ainda precisa ser treinado e validado para a pronúncia usada no headset e no ambiente real.

Os modelos pré-treinados distribuídos com openWakeWord não incluem a palavra isolada ATLAS. Enquanto o modelo personalizado não existir, o sistema usa o modo provisório VAD + Faster-Whisper, que só aceita segmentos cuja transcrição comece com ATLAS.

Veja o procedimento em `VOICE_ENGINE_V2.md`.
