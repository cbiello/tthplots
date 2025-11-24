
reset
set terminal pdfcairo enhanced dashed dl 1.5 lw 3 font "Helvetica,29" size 7.6, 8
set encoding utf8

## default key features
#set key at graph 1.03,0.97
set key reverse  # put text on right side
set key Left     # left bounded text
set key spacing 1.1
set key samplen 2
## to have a assisting grid of dashed lines
set grid front
## set margins
set lmargin 5
set rmargin 2

## general settings
set key at graph 0.7, 0.27
set xtics 
set xtics add 
set mxtics 
set mytics 10
set logscale y
#set logscale x
set ytic offset 0, 0.1
set format y "10^{\%T}"

set label "d{/Symbol s}/d{/Symbol D}{R^y}_{t{/b t̅},H} [fb]" at graph 0, 1.07
set label "t{/b t̅}H\\@LHC 13 TeV" right at graph 1, graph 1.07

set output "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/R_yttbarHiggs.pdf"

##############
# main frame #
##############

# origin, size of main frame
set origin 0, 0.48
set size 1, 0.47
set bmargin 0 # set marging to remove space
set tmargin 0 # set margin to remove space
set format x ""

## define line styles
#MiNNLOPS 5FS (LHE 1, PS 2)
set style line 1 lc rgb "blue" lw 1
set style line 2 lc rgb "dark-blue" lw 1
set style line 11 dt (3,3) lc rgb "blue" lw 0.1
set style line 12 dt (3,3) lc rgb "dark-blue" lw 0.1
#MiNLOp 5FS (LHE 3, PS 4)
set style line 3 dt (9,6) lc rgb "sienna4" lw 1
set style line 4 dt (9,6) lc rgb "black" lw 1
set style line 13 dt (8,4,8,4,3,4) lc rgb "sienna4" lw 0.1
set style line 14 dt (8,4,8,4,3,4) lc rgb "black" lw 0.1
#NLOPS 5FS (LHE 5, PS 6)
set style line 5 dt (15,2) lc rgb "violet" lw 1
set style line 6 dt (15,2) lc rgb "purple" lw 1
set style line 15 dt (10,3,3,3) lc rgb "violet" lw 0.1
set style line 16 dt (10,3,3,3) lc rgb "purple" lw 0.1
#MiNNLOPS 4FS (LHE 7 PS 8)
set style line 7 dt (3,3) lc rgb "light-red" lw 1 
set style line 8 dt (3,3) lc rgb "dark-orange" lw 1
set style line 17 dt (10,3,3,3) lc rgb "light-red" lw 0.1
set style line 18 dt (10,3,3,3) lc rgb "dark-orange" lw 0.1
#MiNLOp 4FS (LHE 9, PS 3 but activate it)
set style line 9 lc rgb "web-green" lw 1
#set style line 3 lc rgb "dark-green" lw 1
# set style line 19 dt (8,4,8,4,3,4) lc rgb "web-green" lw 0.1
# set style line 13 dt (8,4,8,4,3,4) lc rgb "dark-green" lw 0.1
#NLOPS 4FS (LHE 21, PS 22 but deactivate the others)
#set style line 1 lc rgb "orange" lw 1
#set style line 2 lc rgb "coral" lw 1
#set style line 11 dt (3,3) lc rgb "orange" lw 0.1
#set style line 12 dt (3,3) lc rgb "coral" lw 0.1


set style line 1 lc rgb "red" lw 1                                                                                                                                 
set style line 11 dt (8,4,8,4,3,4) lc rgb "red" lw 0.1
#set style line 2 dt (6,4) lc rgb "slateblue1" lw 1                                                                                                                 
#set style line 12 dt (10,3,3,3) lc rgb "slateblue1" lw 0.1

        
## define ranges
set xrange [0.0:5.0]
set yrange [:]

set multiplot
plot "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:2 with lines ls 2 title "MiNNLO_{PS} (0A)", "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:4:6 with filledcurves ls 2 fs transparent solid 0.15 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:4 with lines ls 12 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:6 with lines ls 12 notitle,\
"/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist" using 1:2 with lines ls 1 title "MiNNLO_{PS} (SA)", "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist" using 1:4:6 with filledcurves ls 1 fs transparent solid 0.15 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist" using 1:4 with lines ls 11 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist" using 1:6 with lines ls 11 notitle,\
"/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist" using 1:2 with lines ls 3 title "MiNNLO_{PS} (MA_{FC})", "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist" using 1:4:6 with filledcurves ls 3 fs transparent solid 0.15 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist" using 1:4 with lines ls 13 notitle, "/Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist" using 1:6 with lines ls 13 notitle
###############
# ratio inset #
###############

## remove previous settings
unset label  
#unset key
unset logscale y
unset format

## set ratio inset size
set size 1, 0.32
set origin 0, 0.11

## can be changed
#set logscale y
#set logscale x
set format y 
set key at graph 0.93, 0.95
#set label "ratio to MiNNLO_{PS} (0A)" at graph 0, 1.01
set label "d{/Symbol s}/d{/Symbol s}_{MiNNLO_{PS} (0A)}" at graph 0, 1.1
set label "kQ=0.5" at graph 0.03, 2.5
set label "" at graph 0.03, 2.35
set label "" at graph 0.03, 2.2
set yrange [0.7:1.3]
set ytics 0.2
set mytics 
set ytic offset 0.4, 0
set xtic offset -0.21,0.4
set xtics 
set xtics add 
set mxtics 
set xlabel offset 0,0.9
set xlabel  "{/Symbol D}{R^y}_{t{/b t̅},H} "
plot "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($2/$9) with lines ls 2 notitle\
, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9):($6/$9) with filledcurves ls 2 fs transparent solid 0.15 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9) with lines ls 12 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($6/$9) with lines ls 12 notitle,\
"<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($2/$9) with lines ls 1 notitle\
, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9):($6/$9) with filledcurves ls 1 fs transparent solid 0.15 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9) with lines ls 11 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jul26-lheanalysis-MiNNLOPSk05soft.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($6/$9) with lines ls 11 notitle,\
"<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($2/$9) with lines ls 3 notitle\
, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9):($6/$9) with filledcurves ls 3 fs transparent solid 0.15 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($4/$9) with lines ls 13 notitle, "<paste /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__aug10-lheanalysis-MiNNLOPSk05massFC.hist /Users/christianbiello/Desktop/PROJ_ttH/tthplots/nnlops/gnuplot_minnlo/histograms/R_yttbarHiggs__jun10-lheanalysis-MiNNLOPSk05.hist" using 1:($6/$9) with lines ls 13 notitle