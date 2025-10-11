import torch
import torch.nn as nn
from torch import Tensor
from typing import Optional, Tuple
import torch.nn.functional as F

from .config import VapConfig
from ..encoder import EncoderCPC
from ..modules import GPT, GPTStereo
from ..objective import ObjectiveVAP

class VapGPT(nn.Module):
    
    BINS_P_NOW = [0, 1]
    BINS_PFUTURE = [2, 3]
    
    def __init__(self, conf: Optional[VapConfig] = None):
        super().__init__()
        if conf is None:
            conf = VapConfig()
        self.conf = conf
        self.sample_rate = conf.sample_rate
        self.frame_hz = conf.frame_hz

        self.temp_elapse_time = []

        # Single channel
        self.ar_channel = GPT(
            dim=conf.dim,
            dff_k=3,
            num_layers=conf.channel_layers,
            num_heads=conf.num_heads,
            dropout=conf.dropout,
            context_limit=conf.context_limit,
        )

        # Cross channel
        self.ar = GPTStereo(
            dim=conf.dim,
            dff_k=3,
            num_layers=conf.cross_layers,
            num_heads=conf.num_heads,
            dropout=conf.dropout,
            context_limit=conf.context_limit,
        )

        self.objective = ObjectiveVAP(bin_times=conf.bin_times, frame_hz=conf.frame_hz)

        # Outputs
        # Voice activity objective -> x1, x2 -> logits ->  BCE
        self.va_classifier = nn.Linear(conf.dim, 1)
        
        if self.conf.lid_classify == 1:
            self.lid_classifier = nn.Linear(conf.dim, conf.lid_classify_num_class)
        
        elif self.conf.lid_classify == 2:
            self.lid_classifier_middle = nn.Linear(conf.dim*2, conf.lid_classify_num_class)
        
        if self.conf.lang_cond == 1:
            self.lang_condition = nn.Linear(conf.lid_classify_num_class, conf.dim)
        
        self.vap_head = nn.Linear(conf.dim, self.objective.n_classes)

    def load_encoder(self, cpc_model):
        
        # Audio Encoder
        #if self.conf.encoder_type == "cpc":
        self.encoder1 = EncoderCPC(
            load_pretrained=True if self.conf.load_pretrained == 1 else False,
            freeze=self.conf.freeze_encoder,
            cpc_model=cpc_model
        )
        self.encoder1 = self.encoder1.eval()
        #print(self.encoder1)
        #self.encoder1 = self.encoder1.half()
        
        self.encoder2 = EncoderCPC(
            load_pretrained=True if self.conf.load_pretrained == 1 else False,
            freeze=self.conf.freeze_encoder,
            cpc_model=cpc_model
        )

        self.encoder2 = self.encoder2.eval()
        #self.encoder2 = self.encoder2.half()
        
        if self.conf.freeze_encoder == 1:
            print('freeze encoder')
            self.encoder1.freeze()
            self.encoder2.freeze()

    @property
    def horizon_time(self):
        return self.objective.horizon_time

    def encode_audio(self, audio1: torch.Tensor, audio2: torch.Tensor) -> Tuple[Tensor, Tensor]:
        
        x1 = self.encoder1(audio1)  # speaker 1
        x2 = self.encoder2(audio2)  # speaker 2
        
        return x1, x2

    def vad_loss(self, vad_output, vad):
        return F.binary_cross_entropy_with_logits(vad_output, vad)
    
    def forward(
        self,
        x1: Tensor,
        x2: Tensor,
        cache: Optional[dict] = None,
    ) -> Tuple[dict, dict]:
        """
        Forward pass for the VapGPT model.

        Args:
            x1 (Tensor): Input audio embedded tensor for speaker 1.
            x2 (Tensor): Input audio embedded tensor for speaker 2.
            cache (dict, optional): Cache of past keys/values.

        Returns:
            Tuple[dict, dict]: Model outputs and updated cache.
        """

        if cache is None:
            cache = {}

        o1 = self.ar_channel(x1, past_kv=cache.get("ar1"))
        o2 = self.ar_channel(x2, past_kv=cache.get("ar2"))
        out = self.ar(
            o1["x"],
            o2["x"],
            past_kv1=cache.get("cross1"),
            past_kv2=cache.get("cross2"),
            past_kv1_c=cache.get("cross1_c"),
            past_kv2_c=cache.get("cross2_c"),
        )

        new_cache = {
            "ar1": (o1["past_k"], o1["past_v"]),
            "ar2": (o2["past_k"], o2["past_v"]),
            "cross1": (out["past_k1"], out["past_v1"]),
            "cross2": (out["past_k2"], out["past_v2"]),
            "cross1_c": (out["past_k1_c"], out["past_v1_c"]),
            "cross2_c": (out["past_k2_c"], out["past_v2_c"]),
        }

        # Outputs
        vad1 = self.va_classifier(o1["x"])
        vad2 = self.va_classifier(o2["x"])
        logits = self.vap_head(out["x"])

        probs = logits.softmax(dim=-1)

        p_now = self.objective.probs_next_speaker_aggregate(
            probs,
            from_bin=self.BINS_P_NOW[0],
            to_bin=self.BINS_P_NOW[-1],
        )

        p_future = self.objective.probs_next_speaker_aggregate(
            probs,
            from_bin=self.BINS_PFUTURE[0],
            to_bin=self.BINS_PFUTURE[1],
        )

        # Get back to the CPU
        p_now = p_now.to("cpu").tolist()[0][-1]
        p_future = p_future.to("cpu").tolist()[0][-1]

        vad1 = vad1.sigmoid().to("cpu").tolist()[0][-1][0]
        vad2 = vad2.sigmoid().to("cpu").tolist()[0][-1][0]

        ret = {"p_now": p_now, "p_future": p_future, "vad": [vad1, vad2]}

        return ret, new_cache