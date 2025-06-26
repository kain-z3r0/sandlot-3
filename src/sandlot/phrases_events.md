```text
entry=game_meta
gameid=
home_team=
away_team=

entry=inning_meta
inning=
half=
batting_team=
pitching_team=

entry=atbat_meta
abid=
batter=
pitcher=
count=
k_swinging_count=
k_looking_count=
foul_count=
ab_result= [hit, out, error, etc.]

# Track every distinct baserunning event (e.g., so two base running events for a double stolen base)
baserunning=[event=hold, reason=remains, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]

baserunning=[event=advance, reason=hit, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=error, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=wild_pitch, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=passed_ball, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=balk, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=fielder_choice, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=throw, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=sac_fly, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=groundout, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=interference, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=obstruction, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=intentional_walk, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=dropped_third_strike, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=pickoff_error, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=steal, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=advance, reason=admin, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=] # this for runner placed on base

baserunning=[event=out, reason=caught_stealing, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=out, reason=picked_off, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=out, reason=generic, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]
baserunning=[event=out, reason=interference, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]


baserunning=[event=stolen_base, b1_before=, b1_after=, b2_before=, b2_after=, b3_before=, b3_after=, b4_after=]

```

















```python
grouped_phrases = {
    # Hits
    "singles on a line drive": "",
    "singles on a ground ball to right fielder": "",
    "singles on a hard ground ball to center fielder": "",
    "singles on a hard ground ball to second baseman": "",
    "singles on a hard ground ball to shortstop": "",
    "singles on a ground ball to catcher": "",
    "singles on a fly ball to shortstop": "",
    "singles on a fly ball to third baseman": "",
    "singles on a fly ball to left fielder": "",
    "singles on a fly ball to center fielder": "",
    "singles on a line drive to center fielder": "",
    "singles on a line drive to third baseman": "",
    "singles on a line drive to right fielder": "",
    "singles on a line drive to first baseman": "",
    "singles on a line drive to shortstop": "",
    "singles on a line drive to second baseman": "",
    "singles on a line drive to left fielder": "",
    "singles on a ground ball to second baseman": "",
    "singles on a ground ball to first baseman": "",
    "singles on a ground ball to shortstop": "",
    "singles on a ground ball to pitcher": "",
    "singles on a ground ball to third baseman": "",
    "singles on a ground ball to center fielder": "",
    "singles on a ground ball to left fielder": "",
    "singles on a pop fly to third baseman": "",
    "singles on a pop fly to first baseman": "",
    "singles on a fly ball to first baseman": "",
    "singles on a fly ball to second baseman": "",
    "singles on a fly ball to right fielder": "",
    "singles on a fly ball to catcher": "",
    "singles on a fly ball": "",
    "singles on a bunt to pitcher": "",
    "singles on a hard ground ball to third baseman": "",
    "singles on a hard ground ball to first baseman": "",
    "singles on a hard ground ball to left fielder": "",
    "singles on a hard ground ball to pitcher": "",
    "singles on a hard ground ball": "",

    "doubles on a fly ball to right fielder": "",
    "doubles on a fly ball to left fielder": "",
    "doubles on a fly ball to center fielder": "",
    "doubles on a ground ball to left fielder": "",
    "doubles on a ground ball to right fielder": "",
    "doubles on a ground ball to second baseman": "",
    "doubles on a ground ball to third baseman": "",
    "doubles on a ground ball to shortstop": "",
    "doubles on a ground ball to first baseman": "",
    "doubles on a line drive to right fielder": "",
    "doubles on a line drive to left fielder": "",
    "doubles on a line drive to center fielder": "",
    "doubles on a hard ground ball to center fielder": "",
    "doubles on a hard ground ball to right fielder": "",
    "doubles on a hard ground ball to left fielder": "",
    "doubles on a hard ground ball": "",
    "doubles on a line drive": "",
    "doubles on a fly ball": "",

    "triples on a line drive to right fielder": "",
    "triples on a line drive to center fielder": "",
    "triples on a line drive to left fielder": "",
    "triples on a fly ball to right fielder": "",
    "triples on a fly ball to center fielder": "",
    "triples on a fly ball to left fielder": "",
    "triples on a line drive": "",
    "triples on a hard ground ball to right fielder": "",
    "triples on a hard ground ball to center fielder": "",
    "triples on a hard ground ball to left fielder": "",

    "homers on a fly ball to center field": "",
    "hits an inside the park home run on a hard ground ball to right fielder": "",
    "hits an inside the park home run on a fly ball to left fielder": "",
    "hits an inside the park home run on a hard ground ball to center fielder": "",

    # Reaches on Error
    "hits a ground ball and reaches on an error by second baseman": "",
    "hits a ground ball and reaches on an error by third baseman": "",
    "hits a ground ball and reaches on an error by shortstop": "",
    "hits a ground ball and reaches on an error by catcher": "",
    "hits a ground ball and reaches on an error by first baseman": "",
    "hits a ground ball and reaches on an error by pitcher": "",
    "hits a fly ball and reaches on an error by catcher": "",
    "hits a fly ball and reaches on an error by center fielder": "",
    "hits a fly ball and reaches on an error by shortstop": "",
    "hits a fly ball and reaches on an error by second baseman": "",
    "hits a fly ball and reaches on an error by right fielder": "",
    "hits a fly ball and reaches on an error by pitcher": "",
    "hits a fly ball and reaches on an error by left fielder": "",
    "hits a hard ground ball and reaches on an error by second baseman": "",
    "hits a hard ground ball and reaches on an error by third baseman": "",
    "hits a hard ground ball and reaches on an error by right fielder": "",
    "hits a hard ground ball and reaches on an error by center fielder": "",
    "hits a hard ground ball and reaches on an error by shortstop": "",
    "hits a hard ground ball and reaches on an error by first baseman": "",
    "hits a line drive and reaches on an error by right fielder": "",
    "hits a line drive and reaches on an error by first baseman": "",
    "hits a line drive and reaches on an error by left fielder": "",
    "hits a hard ground ball and reaches on an error": "",

    "reaches on dropped 3rd strike (wild pitch)": "",
    "reaches on dropped 3rd strike (passed ball)": "",

    # Strikeouts / Walks / HBP
    "strikes out swinging": "",
    "strikes out looking": "",
    "out at first on dropped 3rd strike": "",
    "walks": "",
    "is hit by pitch": "",

    # Outs
    "grounds out to right fielder": "",
    "grounds out to second baseman": "",
    "grounds out to shortstop": "",
    "grounds out to third baseman": "",
    "grounds out to first baseman": "",
    "grounds out to pitcher": "",
    "grounds out to catcher": "",
    "grounds out to pitcher #100": "",
    "grounds out": "",
    "flies out to left fielder": "",
    "flies out to right fielder": "",
    "flies out to center fielder": "",
    "flies out to shortstop": "",
    "flies out to second baseman": "",
    "flies out to first baseman": "",
    "flies out to pitcher": "",
    "flies out to third baseman": "",
    "flies out in foul territory to first baseman": "",
    "flies out in foul territory to third baseman": "",
    "flies out in foul territory to left fielder": "",
    "flies out in foul territory to catcher": "",
    "flies out in foul territory to pitcher": "",
    "lines out to shortstop": "",
    "lines out to center fielder": "",
    "lines out to left fielder": "",
    "lines out to right fielder": "",
    "lines out to third baseman": "",
    "lines out to second baseman": "",
    "lines out to pitcher": "",
    "lines out to first baseman": "",
    "lines out": "",
    "pops out": "",
    "pops into a double play": "",
    "out (other)": "",
    "out on sacrifice fly to center fielder": "",
    "out on infield fly to second baseman": "",
    "out on infield fly to shortstop": "",
    "is out on foul tip": "",

    # Double / Multiple Outs
    "lines into a double play to pitcher": "",
    "flies into a double play to center fielder": "",
    "flies into a double play to second baseman": "",
    "flies into a double play to shortstop": "",
    "flies into a double play": "",
    "grounds into a double play": "",
    "grounds into fielder's choice to third baseman": "",
    "grounds into fielder's choice double play": "",

    # Misc
    "sacrifices": "",
    "to first baseman": "",
    "pitching": "",
    "advances to 3rd on wild pitch": "",
    "e": ""
}
```


```python

baserunning_phrases = {
    # Steals
    "steals 2nd": "",
    "steals 3rd": "",

    # Advances
    "advances to 1st": "",
    "advances to 2nd": "",
    "advances to 3rd": "",

    "advances to 1st on the throw": "",
    "advances to 2nd on the throw": "",
    "advances to 3rd on the throw": "",


    "advances to 2nd on wild pitch": "",
    "advances to 3rd on wild pitch": "",

    "advances to 2nd on passed ball": "",
    "advances to 3rd on passed ball": "",

    "advances to 2nd after tagging up": "",
    "advances to 3rd after tagging up": "",

    "advances to 2nd on the same error": "",
    "advances to 3rd on the same error": "",

    "advances to 2nd on the same pitch": "",
    "advances to 3rd on the same pitch": "",
    
    "advances to 3rd on error by catcher": "",
    "advances to 2nd on error by catcher": "",

    "advances to 3rd on error by first baseman": "",
    "advances to 2nd on error by first baseman": "",

    "advances to 3rd on error by second baseman": "",
    "advances to 2nd on error by second baseman": "",

    "advances to 3rd on error by shortstop": "",
    "advances to 2nd on error by shortstop": "",

    "advances to 3rd on error by third baseman": "",
    "advances to 2nd on error by third baseman": "",

    "advances to 3rd on error by pitcher": "",
    "advances to 2nd on error by pitcher": "",

    "advances to 3rd on error by left fielder": "",
    "advances to 2nd on error by left fielder": "",

    "advances to 3rd on error by center fielder": "",
    "advances to 2nd on error by center fielder": "",

    "advances to 3rd on error by right fielder": "",
    "advances to 2nd on error by right fielder": "",

    # Scores
    "scores": "",
    "scores on wild pitch": "",
    "scores on passed ball": "",
    "scores on the throw": "",
    "scores on steal of home": "",
    "scores after tagging up": "",
    "scores on error by catcher": "",
    "scores on the same error": "",
    "scores on error by first baseman": "",
    "scores on error by second baseman": "",
    "scores on error by shortstop": "",
    "scores on error by third baseman": "",
    "scores on error by pitcher": "",

    # Remain / Held
    "remains at 1st": "",
    "remains at 2nd": "",
    "remains at 3rd": "",
    "held up at 1st": "",
    "held up at 2nd": "",
    "held up at 3rd": "",

    # Caught stealing / Pick-offs
    "caught stealing 2nd": "",
    "caught stealing 3rd": "",
    "caught stealing home": "",
    "picked off at 1st": "",
    "picked off at 2nd": "",
    "picked off at 3rd": "",

    # Outs / misc
    "out advancing to 1st": "",
    "out advancing to 2nd": "",
    "out advancing to 3rd": "",
    "out advancing to home": "",
    #"grounds into fielder's choice": "",
    "gets placed on 1st": "",
    "gets placed on 2nd": "",
    "gets placed on 3rd": "",
    "did not score": "",
}

```