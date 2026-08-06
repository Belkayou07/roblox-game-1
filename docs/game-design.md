# Game Design Foundation

## Core loop

```text
Lobby
→ Start a nonstop forward run
→ Fight enemies and avoid obstacles
→ Choose between positive and negative gates
→ Grow or lose power and allied soldiers
→ Die or reach the end
→ Receive money based on performance
→ Buy permanent upgrades
→ Repeat until the world can be completed consistently
→ Earn trophies and unlock later worlds
```

## Run rules

- The player moves forward automatically at a constant base speed.
- The main immediate input is choosing a left, middle, or right lane.
- Gameplay does not pause at enemy waves or gates.
- Gate choices must be readable quickly and may improve or weaken the current run.
- Examples include soldier addition, soldier multiplication, damage boosts, money boosts, unit loss, and enemy-strength increases.
- The run ends when the player dies or completes the final encounter.

## Progression layers

### Temporary run power

Gate effects, collected soldiers, temporary multipliers, and other effects reset after the run.

### Permanent account power

Weapons, damage upgrades, starting bonuses, auras, and future special upgrades persist between runs.

### World progression

Finishing a world awards trophies. Trophy requirements unlock later worlds with stronger enemies, different environments, new gate combinations, and better rewards.

## Development stages

1. Runner movement and prototype track
2. Gate generation and gate selection
3. Basic enemies and fist combat
4. Allied soldier group
5. Obstacles and run failure
6. Run rewards and temporary result screen
7. Lobby and permanent upgrades
8. Data saving
9. World completion, trophies, and world selection
10. Visual production, balancing, mobile polish, and monetization
