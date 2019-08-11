# master_thesis
A repository for my M.Sc. project, conducted at the department of Software Engineering and Technology at Chalmers University of Technology during study periods 3 and 4, spring of 2019.

##SecDFD extraction tool

A tool that automatically extracts a SecDFD from a project, given its call graphs and a set of selected keywords.

###How to use
Begin by running Doxygen on the project you wish to analyze, extracting both call- and called-by graphs. Be careful to 
set the "DOT_CLEANUP" variable to false (or uncheck the box, if you are using doxywizard).

The file "keywords.txt" determines what assets will be identified. You may between iterations add and/or remove keywords
to yield different results. 

To run the program, simply run *Main.py* and carefully follow the command line prompts. 

If your generated SecDFD appears empty, it could be due to:

1) inaccurate path given to the .dot-files. Make sure that there have been generated *cgraph.dot files, and that
they appear at the location you have specified.

2) Too specific keywords. No matches were made due to the exact keywords not being present at their expected locations
in the source code. Re-specify your keywords by modifying the file "keywords.txt", and try again.