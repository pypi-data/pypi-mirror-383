from typing import Annotated

from pydantic import AfterValidator, AnyUrl
from yarl import URL

ToYarlUrl = AfterValidator(lambda val: URL(str(val)))
YarlUrl = Annotated[AnyUrl, ToYarlUrl]
