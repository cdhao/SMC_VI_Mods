# Historic Moment Illustrations

## What the blank parchment means

Rise and Fall and Gathering Storm show a large Historic Moment card when a
player first constructs a unique building, district, improvement, or unit. The
parchment, title, description, date, turn, and Era Score are drawn by the
standard game UI. The large image in the upper part of the card is a separate
illustration.

If the title and Era Score appear but the center remains empty parchment, the
Historic Moment itself worked. The usual missing piece is a
`MomentIllustrations` row or a UI texture that cannot be resolved. This is not a
failure of the ordinary `ICON_BUILDING_*` atlas.

The standard UI resolves the illustration as follows:

```text
Historic Moment type
-> MomentIllustrationType
-> ExtraData MomentDataType and object index
-> gameplay type such as BUILDING_MY_UNIQUE_BUILDING
-> MomentIllustrations.Texture
-> cooked UITexture resource
```

For the first unique building, the built-in Moment is
`MOMENT_BUILDING_CONSTRUCTED_FIRST_UNIQUE`. Its illustration lookup uses:

```text
MOMENT_ILLUSTRATION_UNIQUE_BUILDING
MOMENT_DATA_BUILDING
```

The game performs this lookup automatically. A Mod does not need to replace
`HistoricMoments.lua` or fire the Moment from custom Lua.

## Database registration

Add an in-game database file after the unique object has been defined. For
example:

```sql
INSERT INTO MomentIllustrations
(
    MomentIllustrationType,
    MomentDataType,
    GameDataType,
    Texture
)
VALUES
(
    'MOMENT_ILLUSTRATION_UNIQUE_BUILDING',
    'MOMENT_DATA_BUILDING',
    'BUILDING_CLUB_MAGIC_CIRCLE',
    'MOMENT_BUILDING_CLUB_MAGIC_CIRCLE'
);
```

Register the SQL file under an in-game `UpdateDatabase` action in `.modinfo`.
Loading it after the building SQL makes the foreign-key ownership and intended
order explicit.

Use the corresponding pair for other unique object types:

| Object | MomentIllustrationType | MomentDataType |
| --- | --- | --- |
| Building | `MOMENT_ILLUSTRATION_UNIQUE_BUILDING` | `MOMENT_DATA_BUILDING` |
| District | `MOMENT_ILLUSTRATION_UNIQUE_DISTRICT` | `MOMENT_DATA_DISTRICT` |
| Improvement | `MOMENT_ILLUSTRATION_UNIQUE_IMPROVEMENT` | `MOMENT_DATA_IMPROVEMENT` |
| Unit | `MOMENT_ILLUSTRATION_UNIQUE_UNIT` | `MOMENT_DATA_UNIT` |

`GameDataType` must be the exact gameplay type recorded in the Moment's
ExtraData. For a replacement building, use the custom building type, not the
building it replaces.

## Artwork and texture contract

The Firaxis unique-building source texture contract is:

- Canvas: 456x332 pixels.
- Texture class: `UserInterface`.
- Pixel format: `PF_R8G8B8A8_UNORM`.
- Export mode: `TEXTURE_2D`.
- Mip generation disabled.

Create a dedicated wide illustration. Do not stretch a square building icon
over the frame. The normal building icon and the Historic Moment illustration
are independent assets with different consumers.

For the repository's XLP/BLP pipeline, a minimal entry is:

```xml
<Element>
  <m_EntryID text="MOMENT_BUILDING_CLUB_MAGIC_CIRCLE"/>
  <m_ObjectName text="MOMENT_BUILDING_CLUB_MAGIC_CIRCLE"/>
</Element>
```

The object name identifies the matching `.tex` input. Put the entry in the
Mod's `UITexture` XLP, cook it into the UI BLP, and make sure the `.dep` loads
that BLP through the `UITexture` game library.

Firaxis database files commonly spell `Texture` as a DDS filename such as
`Moment_Infrastructure_Khmer.dds`. The sample Mod in this repository uses the
extensionless XLP resource key. For new packages in this repository, keeping
the SQL `Texture`, XLP `m_EntryID`, and logical texture name identical is the
least ambiguous convention.

## Chuuni Society example

`BUILDING_CLUB_MAGIC_CIRCLE` already triggers the first-unique-building Moment.
Its current 512x512 source is an icon-atlas input, so it should remain unchanged.
Add a separate source such as:

```text
assets/ChuuniSociety/部室魔法阵历史时刻.png
```

Then:

1. Resize or compose it to 456x332 without distorting the subject.
2. Generate the DDS and TEX input named
   `MOMENT_BUILDING_CLUB_MAGIC_CIRCLE`.
3. Add that resource to `ChuuniUITextureV<revision>.xlp`.
4. Re-cook and deploy the updated UITexture BLP.
5. Add the `MomentIllustrations` SQL row and load that SQL from `.modinfo`.

The existing sample
`sample/东方project：妖精领袖包/DataBase/moments.sql` demonstrates the same
database mechanism for a unique unit, district, and improvement.

## Verification

Use a new game or a save in which the unique object has never been completed.
An already-recorded Historic Moment does not trigger again merely because its
illustration was added.

Check each layer independently:

1. Confirm the SQL action appears in `Database.log` without constraint errors.
2. Query or print the `MomentIllustrations` row for the custom `GameDataType`.
3. Inspect the cooked BLP inventory for the texture resource name.
4. Complete the unique object for the first time and inspect `UI.log` for
   texture-resolution errors.
5. Open the Timeline after the popup and confirm the same illustration remains
   visible on the recorded Moment.

For an in-game Lua probe:

```lua
for row in GameInfo.MomentIllustrations() do
  if row.GameDataType == "BUILDING_CLUB_MAGIC_CIRCLE" then
    print(
      "Moment illustration:",
      row.MomentIllustrationType,
      row.MomentDataType,
      row.Texture
    )
  end
end
```

The expected texture is `MOMENT_BUILDING_CLUB_MAGIC_CIRCLE`. If the row prints
but the card is still blank, investigate the XLP/BLP resource. If the row does
not print, investigate the `UpdateDatabase` action and SQL load order.
