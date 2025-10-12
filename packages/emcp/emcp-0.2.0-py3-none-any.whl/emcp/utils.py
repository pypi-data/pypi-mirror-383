
class ToolError(Exception):
    message = ""

    def __init__(self, **kwargs):
        self.details = kwargs
        super().__init__("Error: " + self.message.format(**kwargs))

class PathDoesNotExist(ToolError):
    message = "path '{path}' does not exist"

class PathIsNotDirectory(ToolError):
    message = "path '{path}' is not a directory"

class PathIsNotFile(ToolError):
    message = "path '{path}' is not a file"

class PathOutsideWorkDir(ToolError):
    message = "path '{path}' is outside working directory '{wd}'"

class InvalidUrl(ToolError):
    message = "url {url} is not valid"

class MissingOrEmpty(ToolError):
    message = "{name} cannot be missing or empty"

class CommandDenied(ToolError):
    message = "command '{command}' denied"

class CommandForbidden(ToolError):
    message = "command '{command}' is forbidden"

class FailedReplace(Exception):
    pass

class PathAlreadyExists(ToolError):
    message = "path '{path}' already exists"
