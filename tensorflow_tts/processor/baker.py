import os
import re
import numpy as np
import librosa
import soundfile as sf


_pause = ['sil', 'sp1']
_initials = ['b', 'c', 'ch', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 'sh', 't', 'x', 'z', 'zh']
_tones = ['1', '2', '3', '4', '5']
_finals = ['a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'er', 'i', 'ia', 'ian', 'iang', 'iao', 'ie',
           'ii', 'iii', 'in', 'ing', 'iong', 'iou', 'o', 'ong', 'ou', 'u', 'ua', 'uai', 'uan', 'uang',
           'uei', 'uen', 'ueng', 'uo', 'v', 'van', 've', 'vn']
_special = ['io5']
# _r = ['air2', 'air4', 'anr1', 'anr3', 'anr4', 'aor3', 'aor4', 'ar2', 'ar3', 'ar4', 'enr1', 'enr2', 'enr4', 'enr5',
#       'iangr4', 'ianr1', 'ianr2', 'ianr3', 'iar1', 'iar3', 'iiir4', 'ingr2', 'ingr3', 'inr4', 'iour1',
#       'ir1', 'ir2', 'ir3', 'ir4', 'ir5', 'ongr4', 'our2', 'uair4', 'uanr1', 'uanr2',
#       'ueir1', 'ueir3', 'ueir4', 'uenr3', 'uenr4', 'uor2', 'uor3', 'ur3', 'ur4', 'vanr4']

symbols = _pause + _initials + [i + j for i in _finals for j in _tones] + _special

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}


#
# class MyConverter(NeutralToneWith5Mixin, DefaultConverter):
#     pass

def process_phonelabel(label_file):
    with open(label_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[12:]
    assert len(lines) % 3 == 0

    text = []
    for i in range(0, len(lines), 3):
        begin = float(lines[i].strip())
        if i == 0:
            assert begin == 0.
        phone = lines[i + 2].strip()
        text.append(phone.replace('"', ''))

    return text


class BakerProcessor(object):

    def __init__(self, root_path, target_rate):
        self.root_path = root_path
        self.target_rate = target_rate

        items = []
        self.speaker_name = "baker"
        if root_path is not None:
            with open(os.path.join(root_path, 'ProsodyLabeling/000001-010000.txt'), encoding='utf-8') as ttf:
                lines = ttf.readlines()
                for idx in range(0, len(lines), 2):
                    utt_id, _ = lines[idx].strip().split()
                    phonemes = process_phonelabel(os.path.join(root_path, f'PhoneLabeling/{utt_id}.interval'))
                    phonemes = self.deal_r(phonemes)
                    if 'pl' in phonemes or 'ng1' in phonemes:
                        print(f'Skip this: {utt_id} {phonemes}')
                        continue
                    wav_path = os.path.join(root_path, 'Wave', '%s.wav' % utt_id)
                    items.append([' '.join(phonemes), wav_path, self.speaker_name, utt_id])
            self.items = items

    @staticmethod
    def deal_r(phonemes):
        result = []
        for p in phonemes:
            if p[-1].isdigit() and p[-2] == 'r' and p[:2] != 'er':
                result.append(p[:-2] + p[-1])
                result.append('er5')
            else:
                result.append(p)
        return result

    # @staticmethod
    # def get_initials_and_finals(text):
    #     result = []
    #     for x in text.split():
    #         initials = get_initials(x.strip(), False)
    #         finals = get_finals(x.strip(), False)
    #         if initials != "":
    #             result.append(initials)
    #         if finals != "":
    #             # we replace ar4 to a4 er5
    #             if finals[-2] == 'r' and finals[:2] != 'er':
    #                 finals = finals[:-2] + finals[-1] + ' er5'
    #             result.append(finals)
    #     return ' '.join(result)

    def get_one_sample(self, idx):
        text, wav_file, speaker_name, utt_id = self.items[idx]

        # normalize audio signal to be [-1, 1], soundfile already norm.
        audio, rate = sf.read(wav_file)
        audio = audio.astype(np.float32)
        if rate != self.target_rate:
            assert rate > self.target_rate
            audio = librosa.resample(audio, rate, self.target_rate)

        # convert text to ids
        try:
            text_ids = np.asarray(self.text_to_sequence(text), np.int32)
        except Exception as e:
            print(e, utt_id, text)
            return None

        # return None
        sample = {
            "raw_text": text,
            "text_ids": text_ids,
            "audio": audio,
            "utt_id": str(int(utt_id)),
            "speaker_name": speaker_name,
            "rate": self.target_rate
        }

        return sample

    @staticmethod
    def text_to_sequence(text):
        global _symbol_to_id

        sequence = []
        for symbol in text.split():
            idx = _symbol_to_id[symbol]
            sequence.append(idx)
        return sequence