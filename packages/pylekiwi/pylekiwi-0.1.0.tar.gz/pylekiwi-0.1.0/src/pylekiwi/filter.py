

class Filter:
    def __init__(self, dt: float, tau: float, current_command):
        self.k = tau / dt
        self.current_command = current_command

    def filter(self, command):
        filtered_command = self.current_command + self.k * (command - self.current_command)
        self.current_command = filtered_command
        return filtered_command
