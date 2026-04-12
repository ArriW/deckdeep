# DeckDeep Complete Integration - Playtesting Guide

## Overview
This guide provides step-by-step instructions for validating all three agent integrations through 5 comprehensive playthroughs.

---

## Playthrough 1: Early Game Validation

**Focus**: Progression improvements in early levels (1-9)  
**Duration**: 20-30 minutes  
**Objective**: Verify progression feels fair and engaging

### What to Verify

#### Progression Improvements (Agent 2)
- [ ] Level 1: Game feels like proper tutorial (not trivial)
- [ ] Healing per combat: Should be 3 HP (increased from 2)
- [ ] Enemy health: First enemies should have ~20 HP (15 base, was 12)
- [ ] Enemy damage: First attacks should deal 7 damage (was 6)
- [ ] Level progression: Difficulty increases smoothly
- [ ] Boss at Level 9: Dragon/Troll should be beatable (not impossible)

#### Animation System (Agent 1)
- [ ] Card play triggers animation effects
- [ ] Hit feedback appears on screen (flash + shake)
- [ ] Effects are not distracting or obstructive
- [ ] Damage numbers float up when taking damage (optional visual)

#### New Content Check
- [ ] New enemies: SHOULD NOT appear at levels 1-9
- [ ] New cards: May appear in victory selection (probability-based)
- [ ] New relics: May appear in relic selection (probability-based)
- [ ] New events: May trigger in dungeon nodes

### Success Criteria
- [ ] Game is not too easy (not autopilot)
- [ ] Game is not frustratingly hard
- [ ] Boss fight is challenging but winnable
- [ ] Healing mechanic feels right
- [ ] Animation feedback works smoothly

### Notes
```
Early game difficulty should feel like: "This is a proper challenge"
Not: "This is too easy" or "This is unfair"
```

---

## Playthrough 2: Mid Game Validation

**Focus**: Mid-game progression (10-18) and new content  
**Duration**: 30-40 minutes  
**Objective**: Verify new enemies/cards/relics work in mid-game context

### What to Verify

#### Progression Improvements (Agent 2)
- [ ] Level 10 (stage 2): Should start with bonus health from stage clear
- [ ] Stage 2 healing bonus: Should get +0.5 HP additional healing
- [ ] Difficulty at level 10-14: Moderate challenge
- [ ] Difficulty at level 15+: Card pool increases to 4 (from 3)
- [ ] Boss multiplier adjustments: Easier than original (by 10-20%)
- [ ] Card choices: Feel meaningful (deck building)

#### New Content (Agent 3)
- [ ] Encounter Plague Rat: Should appear in mid-game
- [ ] Encounter Sentinel: Should appear in mid-game
- [ ] Get new card from victory: Note which card if any
- [ ] Get new relic from selection: Try to track which one
- [ ] Trigger random event: Prefer new events (VoidGate, etc.)

#### New Enemy Abilities
- [ ] Plague Rat uses PlagueSpread: Should see "Bleed 3" applied
- [ ] Sentinel uses SentinelStrike: Should see high damage (~1.4x)
- [ ] Their abilities feel balanced (not overpowered)

### Success Criteria
- [ ] Progression feels smooth, not spiky
- [ ] New enemies present real but fair challenge
- [ ] New cards feel useful when obtained
- [ ] Deck-building feels more strategic
- [ ] Stage 2 rewards (health bonus) feel earned

### Notes
```
If you get a new card: Try to build around it
If you get a new relic: Note its effect
Record any new enemies encountered
```

---

## Playthrough 3: Late Game Validation

**Focus**: Late game progression (19+) and difficulty scaling  
**Duration**: 40-50 minutes  
**Objective**: Verify late-game feels challenging but fair

### What to Verify

#### Progression Improvements (Agent 2)
- [ ] Level 15+: Card pool gives 4 cards per victory
- [ ] Late game difficulty: Feels appropriately challenging
- [ ] Boss encounters: Still beatable but require skill
- [ ] Player health scaling: Should have significant health by level 20+
- [ ] Stage progression: Stages 2+ give +5 health per boss clear
- [ ] End-game feel: Should feel earned, not frustrated

#### Enemy Scaling
- [ ] Regular enemies: Health scales properly (~30-40 HP by level 20)
- [ ] Boss encounters: Troll King should be ~around 97 HP (3.8 x base)
- [ ] Dragon: Should be ~around 80 HP (2.5 x base)
- [ ] Challenge level: Beatable with proper strategy

#### Card Synergies
- [ ] Bleed cards: Can build effective bleed deck
- [ ] Defense cards: Can build tank strategy
- [ ] Draw cards: Card advantage strategies work
- [ ] Cost/benefit: Feel balanced throughout

### Success Criteria
- [ ] Difficult but not frustrating
- [ ] High-level enemies feel like real threats
- [ ] Strong card synergies rewarding
- [ ] Win condition feels achievable (not RNG-dependent)
- [ ] Final boss is memorable experience

### Notes
```
Track final win/loss
Record any standout moments or frustrations
Note which strategy worked best
```

---

## Playthrough 4: New Content Focused

**Focus**: All new content from Agent 3  
**Duration**: 50-60 minutes  
**Objective**: Experience all 5 new enemies, sample new cards/relics, see new events

### What to Verify

#### All 5 New Enemies
- [ ] **Sentinel**: Appears at least once - verify SentinelStrike ability
- [ ] **Plague Rat**: Appears at least once - verify PlagueSpread (Bleed 3)
- [ ] **Lich**: Appears at least once - verify DeathCurse ability
- [ ] **Void Aberration**: Appears at least once - verify VoidRift
- [ ] **Stone Golem**: Appears at least once - verify StoneForm defense

Enemy Notes:
```
Sentinel: Precision striker - should feel dangerous but manageable
Plague Rat: Disease spreader - bleed buildup is the threat
Lich: Magic caster - ranged threat
Void Aberration: Exotic - unpredictable but interesting
Stone Golem: Tank - requires strategy to break through
```

#### New Cards (Try to get at least 5)
- [ ] One Plague/Bleed card (Wave, Drain, etc.)
- [ ] One Defense card (Discipline, Prison, etc.)
- [ ] One Rare card (Echo, Assault, etc.)
- [ ] One Synergy card (Pact, Wish, Metamorphosis)
- [ ] One utility card (Wisdom, etc.)

Build tracking:
```
Cards obtained: _________________
Relics obtained: _________________
Events encountered: _________________
```

#### All 3 New Events
- [ ] **Necromancer's Pact**: Should trigger - try accepting pact
- [ ] **Void Gate**: Should trigger - risk/reward choice
- [ ] **Eldritch Scholar**: Should trigger - card advantage trade

Event Notes:
```
Record which events you experienced
Note which choices felt good/bad
```

#### New Relics (Try to get at least 3)
- [ ] **Void Stone**: +2 damage - should feel useful
- [ ] **Plague Amulet**: +1 bleed - synergizes with bleed cards
- [ ] **Sentinel's Resolve**: +15 HP, +1 shield - defense focused
- [ ] **Necrotic Focus**: Heal on bleed - sustain relic
- [ ] **Eldritch Tome**: +1 card draw - accelerator
- [ ] **Golem's Heart**: +20 HP - tank synergy

### Success Criteria
- [ ] Can encounter all 5 enemies
- [ ] New content feels balanced
- [ ] Build variety possible with new content
- [ ] New events offer meaningful choices
- [ ] New relics feel useful and fun

### Notes
```
This playthrough is explicitly about new content testing
Try to intentionally trigger different paths
Experiment with new card synergies
```

---

## Playthrough 5: Full Run (Winning Preferred)

**Focus**: Complete integration test  
**Duration**: 60-90 minutes  
**Objective**: Play complete run testing all systems together

### What to Verify

#### Full Integration Test
- [ ] Progression feels smooth throughout run
- [ ] Animation system smooth throughout
- [ ] New content appears naturally (not forced)
- [ ] No crashes or errors during play
- [ ] Performance stable throughout run
- [ ] Game remains fun and engaging

#### Progression Curve
- [ ] Early levels (1-9): Appropriate difficulty
- [ ] Mid levels (10-18): Good progression
- [ ] Late levels (19+): Challenging but fair
- [ ] Boss fights: Feel like meaningful milestones
- [ ] Overall run: 10-20 minute estimated time

#### Win/Loss Analysis
- [ ] If WIN: Verify boss multiplier changes felt right
- [ ] If WIN: Verify progression enabled the win
- [ ] If LOSS: Verify loss felt like player fault, not unfair
- [ ] If LOSS: Verify difficulty curve was fair up to loss point

#### Overall Feel
- [ ] Game is fun and engaging
- [ ] Decisions feel meaningful
- [ ] Progression feels rewarding
- [ ] New content feels integrated (not tacked on)
- [ ] Would recommend this version to players

### Success Criteria
- [ ] Complete run possible without crashes
- [ ] Win rate feels 30-40% achievable
- [ ] Difficulty curve smooth throughout
- [ ] Integration seamless (feels like one cohesive game)
- [ ] New content feels part of base game

### Performance Notes
```
Start time: ________
End time: ________
Total duration: ________
Final level reached: ________
Win/Loss: ________
Final score: ________
```

---

## Validation Checklist

### Agent 1 (Animation System) - All Playthroughs
- [ ] Screen flash appears on card play
- [ ] Screen shake appears on damage
- [ ] Effects are smooth (not stuttering)
- [ ] Effects are not distracting
- [ ] Monster damage numbers show visual feedback
- [ ] Death animations work smoothly
- [ ] No performance impact from animations

### Agent 2 (Progression) - All Playthroughs
- [ ] Early game: Appropriately challenging (not trivial)
- [ ] Healing mechanic: 3 HP per combat feels right
- [ ] Boss difficulty: Beatable (not impossible)
- [ ] Stage progression: Health bonuses feel earned
- [ ] Late game: Appropriately challenging
- [ ] Card pool: Increases to 4 at level 15+
- [ ] Difficulty curve: Smooth progression (no spikes)

### Agent 3 (New Content) - Playthroughs 2, 4, 5
- [ ] All 5 enemies can spawn
- [ ] New cards appear in selection
- [ ] New relics appear in selection
- [ ] New events trigger
- [ ] Abilities work correctly
- [ ] Content balanced
- [ ] Synergies create build variety

### Overall Quality
- [ ] No crashes
- [ ] No error messages
- [ ] No performance issues
- [ ] All features work as designed
- [ ] Game is fun to play
- [ ] Feels like complete product

---

## Issue Tracking Template

If you encounter any issues, record them:

```
ISSUE #_
Severity: [Critical/Major/Minor]
Description: ________________
Steps to Reproduce: ________________
Expected Behavior: ________________
Actual Behavior: ________________
Playthrough: [1/2/3/4/5]
Level: ________
Screenshot/Log: [attached]
```

---

## Summary Statistics

After all 5 playthroughs, record:

```
Total playthroughs: 5
Wins: ___
Losses: ___
Crashes: ___
Critical issues: ___
Major issues: ___
Minor issues: ___
Overall assessment: [Excellent/Good/Acceptable/Needs Work]
```

---

## Testing Conclusion

When complete, answer:

1. **Did all new content appear naturally in game?**
   Yes / No / Partially

2. **Did progression feel balanced and fair?**
   Yes / No / Partially

3. **Did animations enhance experience without distracting?**
   Yes / No / Partially

4. **Is the game fun and engaging?**
   Yes / No / Partially

5. **Would you recommend this for release?**
   Yes / No / With caveats (list below)

---

**Playtesting Complete**: ___________  
**Tester Name**: ___________  
**Overall Result**: ___________
