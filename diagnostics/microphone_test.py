from __future__ import annotations

import argparse
import time

import numpy as np
import sounddevice as sd


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico local do microfone do ATLAS.")
    parser.add_argument("--device", type=int, default=None, help="Índice do microfone no PortAudio.")
    parser.add_argument("--seconds", type=float, default=5.0, help="Duração do teste em segundos.")
    args = parser.parse_args()

    print("\n=== Dispositivos de entrada disponíveis ===")
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        if int(device.get("max_input_channels", 0)) > 0:
            marker = "  <-- selecionado" if args.device == index else ""
            print(
                f"[{index}] {device['name']} | canais: {device['max_input_channels']} | "
                f"padrão: {device['default_samplerate']} Hz{marker}"
            )

    try:
        info = sd.query_devices(args.device, "input")
        rate = int(round(float(info["default_samplerate"])))
        print(f"\nTestando: {info['name']} ({rate} Hz) por {args.seconds:.1f} s.")
        print("Fale normalmente e depois fique em silêncio...")
        with sd.InputStream(
            device=args.device,
            samplerate=rate,
            channels=1,
            dtype="float32",
            blocksize=max(1, rate // 5),
        ) as stream:
            rms_values = []
            peak_values = []
            overflow_count = 0
            start = time.monotonic()
            while time.monotonic() - start < args.seconds:
                block, overflowed = stream.read(max(1, rate // 5))
                samples = np.asarray(block, dtype=np.float32).reshape(-1)
                rms_values.append(float(np.sqrt(np.mean(samples ** 2))))
                peak_values.append(float(np.max(np.abs(samples))))
                overflow_count += int(bool(overflowed))

        print(f"RMS médio: {np.mean(rms_values):.5f}")
        print(f"Pico máximo: {np.max(peak_values):.5f}")
        print(f"Blocos com overflow: {overflow_count}")
        if np.max(peak_values) < 0.005:
            print("ATENÇÃO: sinal muito baixo. Confira o headset, ganho e entrada selecionada.")
        elif np.max(peak_values) > 0.98:
            print("ATENÇÃO: houve pico próximo de clipping. Reduza o ganho do microfone.")
        else:
            print("Captura concluída. O sinal foi recebido.")
        return 0
    except Exception as exc:
        print(f"Falha no teste: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
