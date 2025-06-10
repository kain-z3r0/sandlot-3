# Processing Steps


1. Load/read game log file
2. Extract relevant data in raw form (keep text unchanged)
3. Create/transform data into format to be inserted into text
4. Create a mapping using diciontaries to replace raw text with tagged text







Bottom 1st - JGB Diamond Kollective 9U -> inning=1, half=bottom, team_batting=JBGDKOLL

Foul, Ball 1, Ball 2, In play.
type=atbat, abid=0001, strike_looking_count=0, strike_swinging_count=0, strike_foul_count=1, ball_count=2, 
pitch_counter=4, event=batted_ball

A Gutwein singles on a ground ball to right fielder.
type=atbat, abid=0001, result=single, hit_location=right_field, type=groundball, batter=agutwein, 
pitcher=unknown, batter_dest=1, runner1=None, runner2=None, runner3=None 

Strike 1 looking, Foul, Ball 1, Foul, Ball 2, A Gutwein advances to 2nd on passed ball, Strike 3 looking.
J Martinez strikes out looking, A Gutwein remains at 2nd.
Ball 1, Strike 1 looking, Ball 2, A Gutwein advances to 3rd on passed ball, Foul, Strike 3 swinging.
J Brooks strikes out swinging, A Gutwein remains at 3rd.
Ball 1, A Gutwein scores on wild pitch, Strike 1 looking, Strike 2 swinging, Ball 2, In play.
C Farmer flies out to pitcher.









Foul, G Francis scores on steal of home, Strike 2 swinging, A Avitia advances to 2nd on passed ball, Foul, Strike 3 looking.
L Ortiz strikes out looking, A Avitia remains at 2nd.


ab_id=00001, batter=lortiz, pitcher=unknown, result=out, type=strikeout_looking, 
home_team = 


event=strikeout, type=looking,
balls=3, strikes=2, runner1=player1, runner2=None, runner



ab_id=003, event=sb, runner=z_e, from=1st, to=2nd, success=True, base=100, outs=0
ab_id=003, event=sb, runner=z_e, from=2nd, to=3rd, success=True, base=010, outs=0
ab_id=003, event=strike, type=foul, pitch_number=1
ab_id=003, event=strike, type=swinging, pitch_number=2
ab_id=003, event=strike, type=foul, pitch_number=3
ab_id=003, event=strike, type=looking, pitch_number=4

runner1=z_e, runner1_event=sb, runner1_dest=2nd,3rd, runner1_success=True,
base=001, outs=0, base_after=001, outs_after=1, runs_scored=0



type=baserunning, event=stolenbase,
hit_location
home_team
away_team
batter_name
pitcher_name
bb_type (batted ball, e.g., ground ball)
balls
strikes
strike_type
outs_before
outs_after
inning, half
home_score_before
away_score_before
home_score_after
away_score_after