import numpy as np
import json
import onnxruntime
import librosa
from pathlib import Path
from huggingface_hub import snapshot_download

class Indic_STT_ALL:
    def __init__(self, model_path=None, device="cpu"):
        if not model_path:
            model_path = snapshot_download("shethjenil/IndicASR-ONNX")
        model_path = Path(model_path)
        self.BLANK_ID = 256
        self.RNNT_MAX_SYMBOLS = 10
        self.PRED_RNN_LAYERS = 2
        self.PRED_RNN_HIDDEN_DIM = 640
        self.SOS = 256
        self.supported_langs = ['as', 'bn', 'brx', 'doi', 'gu', 'hi', 'kn', 'kok', 'ks', 'mai', 'ml', 'mni', 'mr', 'ne', 'or', 'pa', 'sa', 'sat', 'sd', 'ta', 'te', 'ur']
        provider = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if "cuda" in str(device) else ['CPUExecutionProvider']
        self.joint_enc = onnxruntime.InferenceSession(model_path/"joint_enc.onnx", providers=provider)
        self.joint_pred = onnxruntime.InferenceSession(model_path/"joint_pred.onnx", providers=provider)
        self.joint_pre_net = onnxruntime.InferenceSession(model_path/"joint_pre_net.onnx", providers=provider)
        self.rnnt_decoder = onnxruntime.InferenceSession(model_path/"rnnt_decoder.onnx", providers=provider)
        self.ctc_decoder = onnxruntime.InferenceSession(model_path/"ctc_decoder.onnx", providers=provider)
        self.models = {n: onnxruntime.InferenceSession(model_path/f'joint_post_net_{n}.onnx', providers=provider) for n in self.supported_langs}
        self.encoder = onnxruntime.InferenceSession(model_path/"encoder.onnx", providers=provider)
        self.preprocessor = onnxruntime.InferenceSession(model_path/"preprocessor.onnx", providers=provider)
        self.vocab = json.load(open(model_path/'vocab.json'))
        self.language_masks = json.load(open(model_path/'language_masks.json'))
        self.device = device

    def log_softmax(self, x, axis=-1):
        x_max = np.max(x, axis=axis, keepdims=True)
        e_x = np.exp(x - x_max)
        return np.log(e_x / np.sum(e_x, axis=axis, keepdims=True))

    def unique_consecutive(self, arr):
        if len(arr) == 0:
            return arr
        result = [arr[0]]
        for a in arr[1:]:
            if a != result[-1]:
                result.append(a)
        return np.array(result)

    def ctc_decode(self, encoder_outputs, lang):
        logprobs = self.ctc_decoder.run(['logprobs'], {'encoder_output': encoder_outputs})[0]
        logprobs = logprobs[:, :, self.language_masks[lang]]
        logprobs = self.log_softmax(logprobs, axis=-1)
        pred_tokens = np.argmax(logprobs[0], axis=-1)
        pred_tokens = self.unique_consecutive(pred_tokens)
        pred_tokens = [t for t in pred_tokens if t != self.BLANK_ID]
        pred_text = ''.join([self.vocab[lang][x] for x in pred_tokens]).replace('▁', ' ').strip()
        return pred_text

    def rnnt_decode(self, encoder_outputs, lang):
        joint_enc = self.joint_enc.run(['output'], {'input': encoder_outputs.transpose(0, 2, 1)})[0]

        hyp = [self.SOS]
        prev_dec_state = (np.zeros((self.PRED_RNN_LAYERS, 1, self.PRED_RNN_HIDDEN_DIM), dtype=np.float32),
                          np.zeros((self.PRED_RNN_LAYERS, 1, self.PRED_RNN_HIDDEN_DIM), dtype=np.float32))

        for t in range(joint_enc.shape[1]):
            f = joint_enc[:, t:t+1, :]  # B x 1 x H
            not_blank = True
            symbols_added = 0

            while not_blank and (self.RNNT_MAX_SYMBOLS is None or symbols_added < self.RNNT_MAX_SYMBOLS):
                g, _, dec_state_0, dec_state_1 = self.rnnt_decoder.run(
                    ['outputs', 'prednet_lengths', 'states', '162'],
                    {'targets': np.array([[hyp[-1]]], dtype=np.int32),
                     'target_length': np.array([1], dtype=np.int32),
                     'states.1': prev_dec_state[0],
                     'onnx::Slice_3': prev_dec_state[1]}
                )
                g = self.joint_pred.run(['output'], {'input': g.transpose(0, 2, 1)})[0]
                joint_out = f + g
                joint_out = self.joint_pre_net.run(['output'], {'input': joint_out})[0]
                logits = self.models[lang].run(['output'], {'input': joint_out})[0]
                log_probs = self.log_softmax(logits, axis=-1)
                pred_token = np.argmax(log_probs)

                if pred_token == self.BLANK_ID:
                    not_blank = False
                else:
                    hyp.append(pred_token)
                    prev_dec_state = (dec_state_0, dec_state_1)

                symbols_added += 1
        pred_text = ''.join([self.vocab[lang][x] for x in hyp if x != self.SOS]).replace('▁', ' ').strip()
        return pred_text

    def predict(self, audio_path, lang):
        wav, _ = librosa.load(audio_path, sr=16000)
        wav = wav.astype(np.float32)
        audio_signal, length = self.preprocessor.run(None, {"audio_signal": wav[np.newaxis, :], "lengths": np.array([wav.shape[-1]], dtype=np.int64)})
        encoder_outputs, _ = self.encoder.run(['outputs', 'encoded_lengths'], {'audio_signal': audio_signal, 'length': length})
        return self.ctc_decode(encoder_outputs, lang), self.rnnt_decode(encoder_outputs, lang)
