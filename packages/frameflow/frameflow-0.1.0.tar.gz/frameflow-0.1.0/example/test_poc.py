import pandas as pd
import pandera as pa
from pandera.typing import DataFrame as PADataFrame
from pandera.typing import Series


class User(pa.DataFrameModel):
    id: Series[int]
    name: Series[str]


# Raw DataFrame (pandas-only): constructor seeding infers Literal['id'|'name'] now
df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})

# 1) Either pandas-only seeding (above) or Pandera bridge (below)
_ = df["id"]  # OK
_ = df["age"]  # E: column not found: 'age' (plugin)

# 2) assign adds columns to the type
df2 = df.assign(age=df["id"] + 1)
_ = df2["age"]  # OK

# 3) select narrows (pandas-native list literal supported)
df3 = df2[["id", "name"]]
_ = df3["age"]  # E: column not found: 'age'

# 4) drop removes (pandas-native)
df4 = df2.drop(columns=["id"])
_ = df4["id"]  # E: column not found: 'id'
# Demonstrate error on dropping a missing column
df2.drop(
    columns=["not_a_col"]
)  # E: drop(columns=...): unknown column(s): ['not_a_col']

# 5) rename (pandas-native)
df5 = df4.rename(columns={"name": "username"})
_ = df5["username"]  # OK
_ = df5["name"]  # E: column not found: 'name'

# Note: dynamic lists don't narrow; only list/tuple of literal strings does.


# 6) Native Pandera annotation (no validate) — plugin seeds columns from the schema
def expects_user_df(df_in: PADataFrame[User]) -> None:
    _ = df_in["id"]  # OK (seeded from User schema via annotation)
    _ = df_in["age"]  # E: column not found: 'age'


expects_user_df(df)
