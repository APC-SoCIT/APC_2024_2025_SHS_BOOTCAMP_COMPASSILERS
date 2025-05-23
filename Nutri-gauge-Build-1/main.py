from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ListProperty, StringProperty
import os

store_path = os.path.join(os.getcwd(), "user_data.json")
store = JsonStore(store_path)

# Screen for inputting nutrition goals
class NutritionInputScreen(BoxLayout):
    def save_data(self):
        data = {
            "calories": self.ids.calories_input.text,
            "protein": self.ids.protein_input.text,
            "calcium": self.ids.calcium_input.text,
            "fats": self.ids.fats_input.text,
            "trans_fats": self.ids.trans_fats_input.text,
            "cholesterol": self.ids.cholesterol_input.text,
            "carbohydrates": self.ids.carbohydrates_input.text,
            "fiber": self.ids.fiber_input.text,
            "iron": self.ids.iron_input.text,
            "sodium": self.ids.sodium_input.text,
        }
        store.put("nutrition_goals", **data)
        print("Nutrition goals saved:", data)

# Screen for logging food items
class FoodLogScreen(BoxLayout):
    def log_food(self):
        food_name = self.ids.food_name_input.text
        data = {
            "calories": self.ids.food_calories_input.text,
            "protein": self.ids.food_protein_input.text,
            "calcium": self.ids.food_calcium_input.text,
            "fats": self.ids.food_fats_input.text,
            "trans_fats": self.ids.food_trans_fats_input.text,
            "cholesterol": self.ids.food_cholesterol_input.text,
            "carbohydrates": self.ids.food_carbohydrates_input.text,
            "fiber": self.ids.food_fiber_input.text,
            "iron": self.ids.food_iron_input.text,
            "sodium": self.ids.food_sodium_input.text,
        }
        store.put(f"food_{food_name}", **data)
        print(f"Food logged: {food_name}", data)

# Screen for Daily food intake tracking
class DailyIntakeScreen(BoxLayout):
    food_options = ListProperty([])


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_food_options()


    def refresh_food_options(self):
        self.food_options = [
            key.replace("food_", "") for key in store.keys() if key.startswith("food_")
        ]
        if hasattr(self, 'ids') and 'food_spinner' in self.ids:
            self.ids.food_spinner.values = self.food_options


    def add_consumed_food(self):
        selected_food = self.ids.food_spinner.text
        if selected_food and selected_food in self.food_options:
            consumed = store.get("consumed_today") if store.exists("consumed_today") else {"foods": []}
            consumed["foods"].append(selected_food)
            store.put("consumed_today", **consumed)
            print(f"Added {selected_food} to today's intake")
            if hasattr(self.parent.parent, 'progress_screen'):
                self.parent.parent.progress_screen.update_progress()

# Screen for Progress tracking
class ProgressScreen(BoxLayout):
    progress_text = StringProperty("")

    def update_progress(self):
        goals = store.get("nutrition_goals") if store.exists("nutrition_goals") else {}
        consumed = store.get("consumed_today")["foods"] if store.exists("consumed_today") else []
       
        totals = {k: 0 for k in goals.keys()}
        for food_name in consumed:
            if store.exists(f"food_{food_name}"):
                food_data = store.get(f"food_{food_name}")
                for k in totals:
                    try:
                        totals[k] += float(food_data.get(k, 0))
                    except ValueError:
                        pass

        progress_lines = []
        for k in goals:
            try:
                goal_val = float(goals[k])
                current = totals[k]
                progress_lines.append(f"{k.capitalize()}: {current:.1f} / {goal_val:.1f}")
            except ValueError:
                pass
               
        self.progress_text = "\n".join(progress_lines)

# Screen manager 
class MainScreenManager(ScreenManager):
    pass

class GoalScreen(Screen):
    pass

class NewScreen(Screen):
    pass

class DailyIntakeScreenWrapper(Screen):
    pass

class ProgressScreenWrapper(Screen):
    pass

class NutritionApp(App):
    def load_kv(self, filename=None):
        # Explicitly tell Kivy which kv file to load
        return super().load_kv("main.kv")
   
    def build(self):
        return MainScreenManager()

if __name__ == "__main__":
    NutritionApp().run()