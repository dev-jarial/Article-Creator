class ToolWorker:
    def __init__(self, tool=None) -> None:
        self.resource = {}
        self.config = {}
        self.tool = tool

    def add_config(self, key, value):
        self.config[key] = value

    def add_resource(self, key, value):
        self.resource[key] = value
    
    def set_tool(self, tool):
        self.tool = tool

    def check_status(self):
        return self.tool.check_status(self.resource, self.config)

    def process(self):
        return self.tool.process(self.resource, self.config)
    
    def apply(self):
        return self.tool.apply(self.resource, self.config)