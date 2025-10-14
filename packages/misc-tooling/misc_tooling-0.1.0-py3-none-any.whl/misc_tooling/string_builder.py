class StringBuilder:
    def __init__(self, *inputs) -> None:
        self.input_memory = []
        self.output = ""
        self.push(*inputs)

    def push(self, *inputs):
        """Pushes new data into the string memory"""
        for input in inputs:
            if isinstance(input, str):
                self.input_memory.append(input + " ")

    def render(self) -> str:
        """Returns the string"""
        self.output = ""
        for word in self.input_memory:
            self.output += word
        return self.output.strip()

    def reset(self):
        """Clears the memory"""
        self.output = ""
        self.input_memory = []

    def drop_string(self, dropped):
        """Drops string from memorys"""
        if not "." in dropped:
            dropped += " " 
        if dropped in self.input_memory:
            self.input_memory.remove(dropped)

    def scrub_string(self, value):
        """Drops all instances of value in the array"""
        self.input_memory = [item for item in self.input_memory if item != value]
        self.output = self.render()

    def replace(self, value_replaced, replacement):
        """Replaces a string"""
        if isinstance(replacement, str):
            self.input_memory = [
                replacement if value_replaced in value else value
                for value in self.input_memory
            ]

    def replace_at_index(self, index, value):
        """Replace string at index"""
        if 0 <= index < len(self.input_memory) and isinstance(value, str):
            self.input_memory[index] = value + " " if not "." in value else value
    
    def __str__(self) -> str:
        """Returns as a string"""
        return self.render()

    

