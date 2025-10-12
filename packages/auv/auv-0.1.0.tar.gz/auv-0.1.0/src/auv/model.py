import torch
import torch.nn as nn

from auv.modules.codec import AUVCodecDec, AUVCodecEncWithVQ


class AUV(nn.Module):
    def __init__(self):
        super().__init__()

    def from_pretrained(self, ckpt_path, device="cuda"):
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=True)
        self.tokenizer = AUVCodecEncWithVQ(
            sample_rate=16000,
            enc_conf={
                "hop_length": 320,
                "num_layers": 8,
                "hidden_size": 512,
                "ffn_mult": 4,
                "max_position_embeddings": 4096,
            },
            vq_conf={
                "vq_type": "fvq",
                "num_quantizers": 1,
                "dim": 512,
                "codebook_size": 20480,
                "codebook_dim": 8,
                "commitment": 0.25,
                "codebook_partition_maps": {
                    "speech": [0, 8192],
                    "vocal": [0, 12288],
                    "music": [0, 20480],
                    "audio": [0, 20480],
                    "other": [12288, 20480],
                },
            },
        )
        self.token2wav = AUVCodecDec(
            dec_conf={
                "hop_length": 320,
                "num_layers": 12,
                "hidden_size": 512,
                "ffn_mult": 4,
                "max_position_embeddings": 4096,
            },
        )
        self.load_state_dict(ckpt)
        del ckpt

    def forward(self, feature):
        raise NotImplementedError

    @torch.no_grad()
    def encode(self, data):
        wav_input = data.get("sample", None)
        sample_rate = data.get("sample_rate", None)
        if "tokens" not in data:
            assert wav_input is not None, "Neither tokens (vq_codes) nor raw wavfiles were provided"
            assert wav_input.size(0) == 1, "Only support batch_size == 1 when inference"
            if wav_input.dim() == 2:
                wav_input = wav_input.unsqueeze(1)
            tokenizer_out = self.tokenizer(wav_input.squeeze(1), input_sample_rate=sample_rate)
            quantized = tokenizer_out["quantized"]
            tokens = tokenizer_out["tokens"]
            before_quantize = tokenizer_out["before_quantize"]
        else:
            tokens = data["tokens"]
            quantized = self.tokenizer.vq2emb(tokens)
            before_quantize = None

        res = {
            "quantized": quantized,
            "tokens": tokens,
            "before_quantize": before_quantize,
        }

        return res

    @torch.no_grad()
    def decode(self, emb, **kwargs):
        audio = self.token2wav(emb)
        return audio

    @torch.no_grad()
    def decode_tokens(self, tokens, **kwargs):
        quantized = self.tokenizer.vq2emb(tokens)
        audio = self.token2wav(quantized)
        return audio
