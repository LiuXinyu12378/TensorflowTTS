# MFA based extraction for Fast speech 

## Prepare
Everything is done from main repo folder so TensorflowTTS/

0. Optional* Modify MFA scripts to work with your language (https://montreal-forced-aligner.readthedocs.io/en/latest/pretrained_models.html)

1. bash examples/mfa_extraction/scripts/prepare_mfa.sh
 python examples/mfa_extraction/run_mfa.py --corpus_directory=< your dataset path >
   
   (corpus_directory should be splited based on speakers example => dataset/speaker_1/001.wav dataset/speaker_1/001.txt)
   
2. python examples/mfa_extraction/txt_grid_parser.py 

3. Optional* add your own dataset parser based on tensorflow_tts/processor/experiment/example_dataset.py ( If base processor dataset didnt match yours )

4. Run preprocess and normalization using preprocess_multispeaker.yaml or preprocess_libritts.yaml based config

5. Run fix mismatch to fix few frames difference in audio and duration files examples/mfa_extraction/fix_mismatch.py --base_path=< your preprocess outdir location on above step > 
--trimmed_dur_path=< trimmed durations directory > --dur_path=< durations directory >


## Problems with MFA extraction
Looks like MFA have problems with trimmed files it works better (in my experiments) with ~100ms of silence at start and end

Short files can get a lot of false positive like only silence extraction (LibriTTS example) so i would get only samples >2s
