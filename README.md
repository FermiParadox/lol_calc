# MyLoLCalc2
It calculates the damage output (along with other metrics) of any setup for League of Legends. 

###  What's League of Legends 
"LoL" for short, is a popular game. The player can choose among hundreds of items, runes, masteries, 
abilities, and use-order of spells and is matched against other players with the same options. 
All those options allow a vast amount of possible setups, called "builds". 

### Does it work 
**Yes.** It's functional and for given builds it produces 
exactly the expected results. **But it's incomplete and outdated**. 

Check `results_example.png` to see some of the results. 
Note that this output was purely for testing. 
Nearly no front-end development took place.

![image](https://user-images.githubusercontent.com/10809024/143953108-fbb38688-dfab-4c4d-bbe7-48fc44a0f616.png)


### How to run it
Works on python 3.8 (excluding Kivy).

Install dependencies and run  `functional_testing/full_tests.py` and you'll get an image 
similar to `results_example.png`. Modify `functional_testing/default_config.py` to test other builds.


### Current state
The whole project was abandoned due to external issues. 


### No unit tests?
MyLoLCalc**2** was practically my 1st program created on Python (actually it's my 1st program on *any* language). 
Its 1st version MyLoLCalc**1** was abandoned very early since there were some fundamental bugs. 
I'm not a professional programmer and this project was not my full time job. However, it got to a functional state, 
it was maintainable (perhaps excluding portions of "factory" module which I'd rather rewrite than refactor). 


# Licence 
The MyLoLCalc2 (the Software) is under CC0. Check `LICENSE_NON_LOL`.

The following are not considered part of the Software:
all data from LoL and LoL API, like champions', items', masteries' description,
icons, stats and/or anything else that belongs to Riot,
along with any metadata and derivatives from the aforementioned materials;
those are Riot's property and are **not** under MIT.



# Disclaimer of endorsement

This program isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone 
officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks 
or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
