# Thin aliases over the CLI. No logic lives here.
.PHONY: recon fetch split seal train eval figures report reproduce verify test
recon:     ; agepretext recon
fetch:     ; agepretext fetch
split:     ; agepretext split
seal:      ; agepretext seal
train:     ; agepretext train
eval:      ; agepretext eval
figures:   ; agepretext figures
report:    ; agepretext report
reproduce: ; bash reproduce.sh --profile mvr
verify:    ; agepretext ledger verify
test:      ; pytest -q
