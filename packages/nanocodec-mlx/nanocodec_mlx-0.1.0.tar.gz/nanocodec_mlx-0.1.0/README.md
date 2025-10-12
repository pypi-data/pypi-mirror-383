# NanoCodec for Apple Silicon

This is an MLX implementation of [NVIDIA NeMo NanoCodec](https://huggingface.co/nvidia/nemo-nano-codec-22khz-0.6kbps-12.5fps), a lightweight neural audio codec.

## Model Description

- **Architecture**: fully convolutional generator neural network and three discriminators. The generator comprises an encoder, followed by vector quantization, and a [HiFi-GAN-based](https://arxiv.org/abs/2010.05646) decoder.
- **Sample Rate**: 22.05 kHz
- **Framework**: MLX
- **Parameters**: 105M

## Installation

```bash
pip install nanocodec-mlx soundfile
# Install your mlx_codec package
```

## Usage

```python

from nanocodec_mlx.models.audio_codec import AudioCodecModel
import soundfile as sf
import mlx.core as mx
import numpy as np

# Load model from HuggingFace Hub
model = AudioCodecModel.from_pretrained("nineninesix/nemo-nano-codec-22khz-0.6kbps-12.5fps-MLX")

# Load audio
audio, sr = sf.read("input.wav")
audio_mlx = mx.array(audio, dtype=mx.float32)[None, None, :]

audio_len = mx.array([len(audio)], dtype=mx.int32)

# Encode and decode
tokens, tokens_len = model.encode(audio_mlx, audio_len)
reconstructed, recon_len = model.decode(tokens, tokens_len)

# Save output
output = np.array(reconstructed[0, 0, :int(recon_len[0])])
sf.write("output.wav", output, 22050)
```

#### Input
  - **Input Type:** Audio 
  - **Input Format(s):** .wav files
  - **Input Parameters:** One-Dimensional (1D)
  - **Other Properties Related to Input:** 22050 Hz Mono-channel Audio

#### Output
  - **Output Type**: Audio
  - **Output Format:** .wav files
  - **Output Parameters:** One Dimensional (1D)
  - **Other Properties Related to Output:** 22050 Hz Mono-channel Audio

## License

This code is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

The original NVIDIA NeMo NanoCodec model weights and architecture are developed by NVIDIA Corporation and are licensed under the NVIDIA Open Model License. See [NOTICE](NOTICE) for attribution.

When using this project, you must comply with both licenses.

## Citation

This is an MLX implementation of NVIDIA NeMo NanoCodec. If you use this work, please cite the original:

- [NVIDIA NeMo NanoCodec](https://huggingface.co/nvidia/nemo-nano-codec-22khz-0.6kbps-12.5fps)
- [NVIDIA Open Model License](https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf)

