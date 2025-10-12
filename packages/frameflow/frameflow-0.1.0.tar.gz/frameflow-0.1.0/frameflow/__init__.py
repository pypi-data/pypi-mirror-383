# Runtime module for frameflow
# The actual type logic lives in .pyi stubs and the mypy plugin


from mypy.plugin import Plugin


def plugin(version: str) -> type[Plugin]:
    from mypy_frameflow.plugin import FrameFlowPlugin

    return FrameFlowPlugin
