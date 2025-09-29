import pygame

class Manager:
    def __init__(self):
        self.widgets = {}

    def new_widget(self, widget_id, widget_class, *args, **kwargs):
        widget_instance = widget_class(*args, **kwargs)
        self.widgets[widget_id] = widget_instance

    def update(self, events):
        for widget in self.widgets.values():
            widget.update(events)

    def render(self):
        for widget in self.widgets.values():
            widget.render()


class BaseWidget:
    def __init__(self, screen: pygame.Surface, data: dict):
        self.screen = screen
        self.data = data
        self.states = {}
        self.currentstate = "Default"
        self.style = None
        self.texture = None
        self.rect = pygame.Rect(0, 0, 0, 0)

        self._update_visuals()

    def _resolve(self, value, *args, **kwargs):
        return value(*args, **kwargs) if callable(value) else value

    def _update_visuals(self):
        self.style = self.data["States"][self.currentstate]
        pos = (self._resolve(self.style["Pos"][0]), self._resolve(self.style["Pos"][1]))
        self.texture = self.style.get("Texture")
        if self.texture: self.rect = self.texture.get_rect(topleft=pos)
        else: self.rect.topleft = pos

    def update(self, events):
        previous_state = self.currentstate
        for state_key in self.data.get("StateOrder", ["Default"]):
            substates = state_key.split('&')
            if all(self.states.get(sub, 0) == 1 for sub in substates if sub != "Default"):
                self.currentstate = state_key
                break
        else:
            self.currentstate = "Default"
        if self.currentstate != previous_state:
            self._update_visuals()

    def render(self):
        if self.texture:
            self.screen.blit(self.texture, self.rect)


class ToggleButton(BaseWidget):
    def __init__(self, screen: pygame.Surface, data: dict):
        super().__init__(screen, data)
        self.correct_data()
        self._update_visuals()

    def correct_data(self):
        self.states = {"Hovered": 0, "Pressed": 0}
        if "StateOrder" not in self.data:
            self.data["StateOrder"] = ["Pressed&Hovered", "Pressed", "Hovered", "Default"]
        self.data["StateOrder"] = [
            s for s in self.data["StateOrder"] if s in self.data["States"]
        ]
        if not self.data["StateOrder"]:
             self.data["StateOrder"].append("Default")
        for key, value in self.data["States"].items():
            self.data["States"][key] = self.data["States"]["Default"] | value 

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.states["Hovered"] = 1 if self.rect.collidepoint(mouse_pos) else 0
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                if self.states["Hovered"]:
                    self.states["Pressed"] = 1 - self.states["Pressed"]
        super().update(events)



class Button(BaseWidget):
    def __init__(self, screen: pygame.Surface, data: dict):
        super().__init__(screen, data)
        self.correct_data()
        self._update_visuals()

    def correct_data(self):
        self.states = {"Hovered": 0, "Pressed": 0}
        if "StateOrder" not in self.data:
            self.data["StateOrder"] = ["Pressed&Hovered", "Pressed", "Hovered", "Default"]
        self.data["StateOrder"] = [
            s for s in self.data["StateOrder"] if s in self.data["States"]
        ]
        if not self.data["StateOrder"]:
             self.data["StateOrder"].append("Default")
        for key, value in self.data["States"].items():
            self.data["States"][key] = self.data["States"]["Default"] | value 

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.states["Hovered"] = 1 if self.rect.collidepoint(mouse_pos) else 0
        if self.states["Hovered"]:
            self.states["Pressed"] = pygame.mouse.get_pressed()[0]
        super().update(events)
