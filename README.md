# FreeOrionDataCollector

## Index: 

1, Important Notes

2, Acknowledgement

3, Introduction

4, File Structure

5, Problems

6, Work

7, Conclusion


## Important Notes

Read the ReadMe carefully. It describes the files placed in this directory and subdirectories, what assumptions are made and under which circumstances the scripts have been tested. 

The scripts come with no warranty, so use and manipulate them at your own risk.

The usage, the environment and the assumptions made to write the scripts are described in the chapter Work. Read this chapter carefully before starting any of the scripts to prevent errors.

The results presented here heavily depend on your version of FreeOrion and may differ when executed with different versions. 

This project uses statistical methods. It is no scientific research.

This project is an individuals work. As such, it executes and manipulates the files of the FreeOrion-project, but has otherwise no relationship to the FreeOrion-project.


## Acknowledgement

Thanks to Geoff, Oberlus and O01eg for standing my questioning. I've taken a different approach for starting the program later than the one they advised, but I used their ideas for observing the program and shutting it down. 

And thanks to the team of FreeOrion. It's a good game and I hope I can help you make it a bit better with this project.


## Introduction

I was playing FreeOrion when I got interested in tweaking its AI. When I started setting it up, the following problems arose: 

1, How to make the game stop and restart itself (so I don't have to do this in multiplayer all the time)?

2, Does the AI perform better with some races than with other ones (this is important to know how much effect a change in the AI would have)?

When I tackled number two by starting, stopping and recording results by hand, I recognized that not all races are played equally well by the AI. Still, when I would have to do this by hand, I wouldn't have gotten meaningful data until today. 

This project aims at comparing AIs by playing games of AI vs. AI at standard settings. The project consists of scripts for creating files that describe the battles done. The two most significant results are:

1, Fulver and Sly will lose two out of three games (given any random opponent),

2, Trith will win two out of three games (given any random opponent).

In the end, the project should have collected enough data to give meaningful results and analysis of the behaviour of the AI. Hopefully, this will help other programmers for the FreeOrion-AI to create even better AIs.


## File Structure

### Directories

There are three directories in the project: Log, LogFirstTen and FreeOrionSetupChanges. 

In LogFirstTen are about ten games per one vs. one constellation. They differ from the rest stored in Log as those games had no pruning mechanism enabled (described later in the chapter Work). Because of mistakes, some subdirectories contain more files and one directory was forgotten. 

The directory Log contains all files stored in LogFirstTen plus games that had an enabled pruning mechanism. Each constellation of one vs. one contains 70 games. 
Both directories are structured as (Unix-writing): Player 1 / Player 2 / game log. So that "SP_ABADDONI/SP_CHATO/gamelog...csv" is one game where Abaddoni (Player 1) plays against Chato (Player 2). For reasons of recombination, please read on in chapter Work.

FreeOrionSetupChanges contains all changes on the base of the FreeOrion-project. Currently, it's only a change in the turn_events.py that stores the logs later copied into the Log-directory.


### ReadMe

This file. Read carefully.

### R-Files (.R)

Those files contain statistical computation that didn't suit well in the python scripts. Those are: 

TreeCategorical.R is a list of instructions used for R to calculate the decision tree for pruning. See chapter Work for more information. 

meanEstimationSignificance.R and speciesWinningSignificance compute the significance of the mean values. See chapter Work for closer information.

### Data tables (.csv)

Those files store information in table form. While the files in Log and LogFirstTen store the information of the games played, the files outside of these directories store statistical calculations and aggregations. See chapter Work for more information. 

### Scripts (.py)

The Python-Files contains self-executable scripts (except FreeOrionSharedFunctionality.py which contains functionality used in several python files). Each script can be called by "python3 <script>.py" and has no options or parameter (all these are within the scripts). See chapter Work for more information. 


## Problems

When experimenting with the AI, two questions arose. The first one is: How do I know that the AI I wrote is better than the one I replaced? The answer to this question lies within the question: I have to be able to compare the results of the old AI with the new one. For this, records with the performance of the previous AI have to be collected. Those then have to be compared with the performance of the new AI. Simple "let them play against each other" may work only in a game where randomness seldom appears. And in FreeOrion, the whole map is created at random. So we need information on how good an AI performs and, if possible, so much data that we can make assumptions about the overall performance of the AI.

The second problem was the fact that games with similar settings should be played in a row. Initially, I aimed this feature at the training of self-learning algorithms. But the statistic described before needed this ability as well: Playing a game several times in a row produces the data needed to analyse tendencies of winning and losing of one species played by the AI against the other. 

Based on these findings, I decided to start a project that aims at creating the statistical data mentioned for later use and comparison. 


## Work

This chapter describes the assumptions done to start the project, the artefacts created by this project and the problems that appeared. Read this chapter carefully before executing the scripts.

### Assumptions

1, Environment: 

1.1, OS: Manjaro, 64 bit, updated until the end of the execution on 17th of July 2020. Also, all dependencies of FreeOrion were updated this way.

1.2, FreeOrion: Stable version v0.4.9 stable release (tag: release-v0.4.9)

1.3, For the Project: Python 3.8.3 with the additional package "scipy", R (cran) version 4.0.1 with the additional package "tree", 

2, Game: 

2.1, I assumed that the random generator produces complete random worlds (given the seed is changed every time) and does not bias towards a type of planet or player. 

2.2, I could not assume that the AI plays equally well with each species (thanks to the team of FreeOrion that showed me the flaws in my assumption) and that the AI plays each species equally well. 

2.3, To have a well-balanced game, most settings are at the level of the configuration installed when the game was first started (see version 0.4.9 for more information. It would be too much to describe every rule here). The settings changed are: 

2.3.1, The seed gets a random value of eight ASCII-letters (lowercase and uppercase) to guarantee random generation.

2.3.2, The size of the universe is fixed to 45. This size is the advised size (between 15 and 30) times two (two players). 

2.3.3, The Aggression level is set to "Maniac". I took this level to speed up computation (because the game finishes earlier) and to prevent equilibriums (they still appeared some times).

2.3.4, I set the shape to random to prevent bias for one kind of universe shape.

2.4, I assumed that when the game takes longer than 450 turns, the result does not depend much on the species or the AI but luck. The script then terminates the game and stores the logs. 

2.5, Each game, when played very very long, will end (by researching Singularity or by conquering the opponent) and it would be unlikely that the result would be a draw.

### The process

The first step was to find a way to start and stop the game and to log the data of the game.  Geoff, Oberlus and O01eg helped me here and described how to start a game, to terminate the game and to document the game's happenings. 

As I later found out, starting the game without defining the species playing was not sufficient for analysis as the number of games played with one species would depend on luck. Therefore, I overheard the network behaviour of the FreeOrion-server by writing a simple Man-In-The-Middle-program, connect the client to the Man-In-The-Middle, forwarded the communication to each side and logged it. That way, I was able to fabricate fake network messages, set up the lobby automatically and start the game. 

When the game starts, the script in the turn_events.py stores a log. With the "tail"-process (included into Linux), this log-file can be observed. The server can be shut down by an observing program when the game state met one of the following requirements: 

1, the game took more than 450 turns, 

2, one side had no more owned planets (colonised + outpost, described later),

3, a pruning mechanism (described later) will indicate a victory for one side.

The logging-mechanism of the turn_events.py stores a ".csv"-file in the same directory. I intended to use only information available to an observer so that for each game turn the mechanism stores: 

1, the current turn

2, the amount of owned planets (colonized + outposts) per player

3, the research output per player

4, the industry output per player

5, the number of ships per player

6, the inhabitants per player

Where each turn was a separated line. These settings provide a rough estimation of the current situation of the game. 

With these settings, the script (found in FreeOrionDataCollector.py) starts. It now starts the FreeOrion-server, sets up the conditions, starts the game, observes the logs, stops the game when one of the stopping condition was met, moved the log create by turn_events.py into the Log-directory and restarts everything. The script did this for ten games with each combination of species (more or less, one combination was forgotten and, at others, more files than necessary were computed). This low number of games per combination was chosen because there was no adequate pruning mechanism at the start of this project. 

When this computation finished, the data was analysed. Therefore, the script FreeOrionDataResultPrinter.py was written to analyse the logs and print the results (the analysing section was later moved to the FreeOrionSharedFunctionality.py to reuse it). The results are stored as 1 for player one won, -1 when player two won and 0 if there were more than 450 turns needed. Games with 0 to 1 coding failed for me in earlier attempts so that I decided to use this coding. Additionally, I implemented a translation to 0 to 1 coding in later scripts.

The FreeOrionMeanEstimation.py analyses the average (mean), variability (variance) and estimation of needed samples. Both mean and variance come in two flavours: 

1, The originally 1 to -1 coding as described above,

2, The 0 to 1 coding (added a _normalized to the name of the result). 

Based on these values the amount of samples needed for statistically significant results has been estimated (per species vs species). Again, I used two flavours: 

1, Sample_Estimation estimates the needed samples to give a statistically adequate mean by analysing the variance (not the _normalized ones).

2, Sample_Estimation_binomial estimates the needed samples to give a statistically adequate mean_normalized by expecting the values used are of type True-False (0 or 1). This assumption is not exactly the reality (as we inserted a third value for a draw), but, given that each game has to end theoretically (see Assumptions), it would be a correct approach. Also, these values were more stable then Sample_Estimation and were closer to the final results.

Both estimations needed a statistical frame: How precise should the answer be and what size should the confidence interval be? I decided to go for 90 % precision and a confidence interval of size 0.2 for normalized values and 0.4 for non-normalized values (those that don't get it: I would recommend Wikipedia https://en.wikipedia.org/wiki/Sample_size_determination or a good teacher for statistics cause it could get a bit mathematical. It would be too much to describe the meaning of those values here). The main reason for these values is that they gave numbers that seemed to be computable. 

Based on the estimation done, I decided to go for 20 more values (per combination), estimate again and then for 40 more samples (up to 70 in total). 

With this done, I wrote the FreeOrionDataMerger.py to create two ".csv"-files that combine all logs collected so far and store each line with the result of the game (pruningData*.csv). The pruningDataCategorical.csv kept every entry, even when log entries with similar content are already inserted, as a separated line. The pruningDataRegression.csv instead merged equal lines and stored an average of their results. Those files, as the names suggest, were intended to be used for the search for pruning algorithms.

Based on the pruningDataCategorical.csv, I wrote the TreeCategorical.R-script. This script was used to create a categorical decision tree for pruning the data. The following decisions were made: 

1, The decision tree was used because it's easy to implement and easy to understand. On the other hand, decision trees are volatile when the behaviour of the AI changes, so the decision tree presented here should only be used on the AI of version v0.4.9 and should be updated for other versions. 

2, Values indicating a draw were either replaced when one side was dominant in research and industry output or dropped. That way, the tree reduced in complexity.

3, As the beginning of the game can give imprecise data, for the computation of the tree, the first 100 turns of each game are ignored. The pruning algorithm will mark them as "keep on calculating".

4, Branches of the decision tree with less than 90 % correct classified values were implemented into the pruning mechanism as "keep on calculating". 

Based on this, the computation was restarted (as described before, first 20 additional games per combination, later 40 more games). When finished, the script FreeOrionWinningStatistics.py computes the mean of winning and losing for every single species. 

The scripts speciesWinningSignificance.R and meanEstimationSignificance.R tackle the file speciesMeanWinning.csv and meanAndSignificance.csv respectively. Those scripts make a hypothesis test on the mean values presented in the files. The hypothesis was that the mean values tend to draw (0 when not normalized, 0.5 when normalized) with a security of 90 % (ALPHA = 0.1). The test comes as both two-tailed, one-tailed and an added p-value. 


## Conclusion

Based on these assumptions, tests and data, the following conclusions can be made: 

1, The performance of Trith, Sly and Fulver are highly significant. Their p-value for their games sorted by species is 0 (or so small that R didn't bother computing it) so that we can say: Winning with the Trith and loosing with Sly or Fulver is no luck for the AI on the long run. It would be wise to test the AI if winning and losing 2/3rd of all games is just the AI (not) able playing with them or if it's the species' setting. 

2, Some other species seem to win in a statistically significant amount of times. Further research is needed to test if this holds for AI vs. human games or not. 

3, Some species seem to win against certain species more often. Further research is needed to test if this is a fair equilibrium or unintended bias.


## Licence

GNU Public Licence v3.0


