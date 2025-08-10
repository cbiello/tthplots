#!/bin/zsh

set -e

# Create backup directory
mkdir -p mariussaved
cp *.NNLO.QCD.dat mariussaved/

# Mapping between NNLO names and MiNNLOPS names
declare -A mapping=(
    ["y_h"]="yHiggs"
    ["pT_h"]="ptHiggs"
    ["m_httx"]="massHiggs+top+tbar"
    ["m_ttx"]="masst+tbar"
    ["y_t"]="ytop"
    ["y_tx"]="ytbar"
    ["pT_t"]="pttop"
    ["pT_tx"]="pttbar"
    ["pT_ttx"]="ptt+tbar"
    ["dy_h_t"]="dyHiggstop"
    ["dy_h_tx"]="dyHiggstbar"
    ["dy_t_tx"]="dyttbar"
    ["dy_h_ttx"]="dyttbarHiggs"
    ["dphi_h_t"]="dphiHiggstop"
    ["dphi_h_tx"]="dphiHiggstbar"
    ["dphi_t_tx"]="dphittbar"
    ["dR_h_t"]="R_yHiggstop"
    ["dR_h_tx"]="R_yHiggstbar"
    ["dR_t_tx"]="R_yttbar"
    ["dR_h_ttx"]="R_yttbarHiggs"
    ["pT_httx"]="ptHiggs+top+tbar"
#    ["total_rate"]="total_rate"  # no MiNNLOPS match, keep
)

# Loop through NNLO files and rename
for file in *.NNLO.QCD.dat; do
    base="${file%%..NNLO.QCD.dat}"
    if [[ -n "${mapping[$base]}" ]]; then
        newname="${mapping[$base]}..NNLO.QCD.dat"
        mv "$file" "$newname"
        echo "Renamed $file → $newname"
    else
        echo "No mapping found for $base → skipping"
    fi
done
