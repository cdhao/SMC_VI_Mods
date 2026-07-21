# Runtime Patterns

## Scope every feature to the intended civilization and leader

Custom projects, Lua rewards, modifiers, and UI-visible abilities must not leak
to another civilization. SQL should attach to the unique civilization trait or
replacement district. Lua should use one predicate that validates both IDs:

```lua
player:GetCivilizationTypeName() == "CIVILIZATION_EXAMPLE"
player:GetLeaderTypeName() == "LEADER_EXAMPLE"
```

This matters in multiplayer and when different leaders can share a civilization.
Never treat a player ID as the Mod identity.

## Use the native system first

Use SQL Requirements and Modifiers for static effects, scope, combat conditions,
district adjacency, and dynamic on-plot buffs. Projects may use native resource
costs for their baseline cost. Reserve Lua for effects that Civ6 does not model
well, such as random Eureka selection, variable batch resource conversion, or
forced healing.

The Grace Ark implementation is a reference: Campus adjacency is inherited,
extra adjacency is SQL, production mirrors science adjacency with the native
adjacency-yield Modifier, and the Currency garrison range/sight effect does not
scan units in Lua.

## Persistent state and events

`PlayerProperty` is suitable for compact Mod state such as an upgrade level or
one-shot flag. Always guard absent values before `tonumber`; a missing property
is not numeric. For stockpile-like gameplay currency, use a real strategic
resource when the native UI and project resource costs matter.

When forcing unit healing, mutate the unit object:

```lua
unit:ChangeDamage(-actualHeal)
```

`UnitManager.ChangeDamage` is not the unit healing API. Clamp the healing to
current damage and log before/after values during runtime testing.

## Project and game-speed edge cases

`Projects.CostProgressionParam1` is non-null; write `0` for
`NO_COST_PROGRESSION`, not `NULL`. Game speed can scale displayed strategic
resource quantities. Treat a native project resource cost as the baseline and
perform optional batch conversion in Lua only after completion, using the
actual remaining stockpile.
