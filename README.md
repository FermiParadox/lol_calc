# README #

### What's this ###
This is a program ("MyLoLCalc2" for short) intended to calculate the damage output (along with other metrics) of any setup for League of Legends (a popular MMO game). 

###  What's League of Legends ###
In League of Legends ("LoL" for short), the player can choose among many different items, runes, masteries, abilities, and use-order of spells and is matched against other players with the same options. All those options allow a vast amount of possible setups, called "builds". 

### Does it work ###
Yes, however it's not complete. And also it's outdated. LoL changes very often. There are probably many more bugs to fix, but it's functional and for given builds it produces exactly the expected results. 
You can check the `results_example.png` to get an idea of some of the results. Note that this output was purely for testing. Nearly no front-end development took place.

### Dog ate your unit tests? ###
MyLoLCalc**2** was practically my first program created on Python (actually it's my first program on *any* language). Its first version MyLoLCalc**1** was abandoned very early since there were some fundamental bugs. 
I'm not a professional programmer and this project was not my full time job. However it got to a functional state, it was maintainable (perhaps excluding portions of "factory" module which I'd rather rewrite than refactor) and preliminary timing testing indicated that it _might_ have been fast enough for production (might be wrong on that). 


### How to run it ###
Works on python 3.4 and 3.5 (though i haven't tested 3.5 for additional bugs), 

On Ubuntu, try to run `functional_testing/full_tests.py`, and the errors for missing dependencies along with a couple of easy searches should be enough to help you install whatever is missing.

Assuming all dependencies are installed, run  `functional_testing/full_tests.py` and you'll get an image similar to `results_example.png` along with test results regarding results' consistency and time profiling. Modify `functional_testing/default_config.py` to test other builds.


### Current state ###
The whole project was abandoned due to third parties involved. 


###Licence###
The MyLoLCalc2 (the Software) is under MIT licence (check the `LICENCE.TXT` file).

The following are not considered part of the Software:
all data from LoL and LoL API, like champions', items', masteries' description,
icons, stats and/or anything else that belongs to Riot,
along with any metadata and derivatives from the aforementioned materials;
those are Riot's property and are **not** under MIT.



### Disclaimer of endorsement###

This program isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.