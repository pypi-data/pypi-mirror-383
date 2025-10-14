import av
import numpy as np
import opuslib


class AudioOpus:

    def __init__(self, sample_rate, channels, frame_duration):
        self.frame_duration = frame_duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_size = self.sample_rate * self.frame_duration // 1000

        # 创建 Opus 编码器
        self.opus_encoder = opuslib.Encoder(fs=sample_rate, channels=channels, application=opuslib.APPLICATION_VOIP)

        self.resampler = av.AudioResampler(format="s16", layout="mono", rate=sample_rate)

    def set_out_audio_frame(self, audio_params):
        # 小智服务端 的 音频信息
        self.out_frame_size = audio_params["sample_rate"] * audio_params["frame_duration"] // 1000

        # 创建 Opus 解码器
        self.opus_decoder = opuslib.Decoder(
            fs=audio_params["sample_rate"],  # 采样率
            channels=audio_params["channels"],  # 单声道
        )

    async def pcm_to_opus(self, pcm):
        pcm_array = np.frombuffer(pcm, dtype=np.int16)
        pcm_bytes = pcm_array.tobytes()
        return self.opus_encoder.encode(pcm_bytes, self.frame_size)

    async def change_sample_rate(self, pcm_array) -> np.ndarray:
        # 采样率 变更
        frame = av.AudioFrame.from_ndarray(np.array(pcm_array).reshape(1, -1), format="s16", layout="mono")
        frame.sample_rate = self.opus_decoder._fs
        resampled_frames = self.resampler.resample(frame)
        samples = resampled_frames[0].to_ndarray().flatten()
        new_frame = av.AudioFrame.from_ndarray(
            samples.reshape(1, -1),
            format="s16",
            layout="mono",
            # layout="stereo",
        )
        new_frame.sample_rate = self.sample_rate
        new_samples = new_frame.to_ndarray().flatten()

        # 不足 self.frame_size 补 0
        samples_padded = np.pad(
            new_samples, (0, self.frame_size - new_samples.size), mode="constant", constant_values=0
        )
        return samples_padded.reshape(1, self.frame_size)

    async def opus_to_pcm(self, opus) -> np.ndarray:
        pcm_data = self.opus_decoder.decode(opus, frame_size=self.out_frame_size)
        pcm_array = np.frombuffer(pcm_data, dtype=np.int16)
        samples = await self.change_sample_rate(pcm_array)
        return samples
