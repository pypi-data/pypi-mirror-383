from typing import Generic, TypeVar

import pandas as pd

C = TypeVar("C")

class DataFrame(pd.DataFrame, Generic[C]): ...
