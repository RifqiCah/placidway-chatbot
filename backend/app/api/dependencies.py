from typing import Annotated

from fastapi import Depends

from backend.app.core.container import ApplicationContainer, get_container

ContainerDependency = Annotated[ApplicationContainer, Depends(get_container)]

