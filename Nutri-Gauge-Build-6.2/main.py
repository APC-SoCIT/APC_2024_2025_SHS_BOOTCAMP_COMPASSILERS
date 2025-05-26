from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ListProperty, StringProperty
import os
import requests
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

store_path = os.path.join(os.getcwd(), "user_data.json")
store = JsonStore(store_path)
Window.size =(500,700)

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
        for key in data:
            self.ids[f"{key}_input"].text = ""

# Screen for logging food items
class FoodLogScreen(BoxLayout):
    def log_food(self):
        food_name = self.ids.food_name_input.text
        data = {
            "name": food_name,
            "serving_size": self.ids.food_serving_size_input.text, 
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
        for key in data:
            if f"food_{key}_input" in self.ids:
                self.ids[f"food_{key}_input"].text = ""
        self.ids.food_name_input.text = ""
        self.ids.food_serving_size_input.text = ""  
        self.ids.food_calories_input.text = ""
        self.ids.food_protein_input.text = ""
        self.ids.food_calcium_input.text = ""
        self.ids.food_fats_input.text = ""
        self.ids.food_trans_fats_input.text = ""
        self.ids.food_cholesterol_input.text = ""
        self.ids.food_carbohydrates_input.text = ""
        self.ids.food_fiber_input.text = ""
        self.ids.food_iron_input.text = ""
        self.ids.food_sodium_input.text = ""


    def show_food_database(self):
        try:
            response = requests.get("http://localhost:5000/foods")  
            foods = response.json()
            print("Foods received from server:", foods)
        except Exception as e:
            Popup(title="Error", content=Label(text=str(e)), size_hint=(0.8, 0.4)).open()
            return

        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for food_key, food in foods.items():
            food_name = food.get('name', 'Unknown Food')
            food_calories = food.get('calories', 'N/A')
            btn = Button(text=f"{food_name} ({food_calories} kcal)", size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn, food=food: self.show_food_details_from_db(food))
            layout.add_widget(btn)
        popup = Popup(title="Food Database", content=layout, size_hint=(0.9, 0.9))
        popup.open()


    def show_food_details_from_db(self, food):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        if "serving_size" in food:
            layout.add_widget(Label(text=f"Serving Size: {food['serving_size']}"))
        for key, value in food.items():
            if key != "serving_size":
                layout.add_widget(Label(text=f"{key.capitalize()}: {value}"))
        add_btn = Button(text="Add to My Foods", size_hint_y=None, height=50)
        popup = Popup(title=f"{food.get('name', 'Food Details')}", content=layout, size_hint=(0.8, 0.8))
        add_btn.bind(on_release=lambda btn: self.add_food_from_db_and_close(food, popup))
        layout.add_widget(add_btn)
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        close_btn.bind(on_release=popup.dismiss)
        layout.add_widget(close_btn)

        popup.open()


    def add_food_from_db_and_close(self, food, popup):
        store.put(f"food_{food['name']}", **food)
        print(f"Added {food['name']} to your log.")
        popup.dismiss()
        Popup(title="Added!", content=Label(text=f"{food['name']} added to your log."), size_hint=(0.7, 0.3)).open()


    def show_logged_foods(self):
        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        logged_foods = [store.get(key) for key in store.keys() if key.startswith("food_")]
        for food in logged_foods:
            food_name = food.get('name', 'Unknown Food')
            btn = Button(text=food_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn, food=food: self.show_food_details(food))
            layout.add_widget(btn)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(layout)
        popup = Popup(title="Logged Foods", content=scroll_view, size_hint=(0.9, 0.9))
        popup.open()

    def show_food_details(self, food):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        if "serving_size" in food:
            layout.add_widget(Label(text=f"Serving Size: {food['serving_size']}"))
        for key, value in food.items():
            if key != "serving_size":
                layout.add_widget(Label(text=f"{key.capitalize()}: {value}"))
        remove_btn = Button(text="Remove", size_hint_y=None, height=50)
        remove_btn.bind(on_release=lambda btn: self.remove_logged_food(food))
        layout.add_widget(remove_btn)
        close_btn = Button(text="Close", size_hint_y=None, height=50)
        popup = Popup(title=f"{food.get('name', 'Food Details')}", content=layout, size_hint=(0.8, 0.8))
        close_btn.bind(on_release=popup.dismiss)
        layout.add_widget(close_btn)
        popup.open()

    def remove_logged_food(self, food):
        food_key = f"food_{food['name']}"
        if store.exists(food_key):
            store.delete(food_key)
            print(f"Removed {food['name']} from logged foods.")
        self.show_logged_foods()

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
            self.ids.food_spinner.text = "Select Food"
            if hasattr(self.parent.parent, 'progress_screen'):
                self.parent.parent.progress_screen.update_progress()

    def show_todays_intake(self, parent_popup=None):
        consumed = store.get("consumed_today")["foods"] if store.exists("consumed_today") else []
        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        btns = []
        if not consumed:
            layout.add_widget(Label(text="No foods added today."))
        else:
            for food_name in consumed:
                btn = Button(text=food_name, size_hint_y=None, height=40)
                btns.append((btn, food_name))
                layout.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)
        popup = Popup(title="Today's Intake", content=scroll, size_hint=(0.9, 0.9))

        for btn, food_name in btns:
            btn.bind(on_release=self._make_show_food_details_today(food_name, popup))

        popup.open()
        return popup

    def _make_show_food_details_today(self, food_name, parent_popup=None):
        def show_food_details_today(btn):
            self.show_food_details_today(food_name, parent_popup)
        return show_food_details_today

    def show_food_details_today(self, food_name, parent_popup=None):
        food_key = f"food_{food_name}"
        if not store.exists(food_key):
            Popup(title="Error", content=Label(text="Food not found."), size_hint=(0.7, 0.3)).open()
            return
        food = store.get(food_key)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        if "serving_size" in food:
            layout.add_widget(Label(text=f"Serving Size: {food['serving_size']}"))
        for key, value in food.items():
            if key != "serving_size":
                layout.add_widget(Label(text=f"{key.capitalize()}: {value}"))

        remove_btn = Button(text="Remove from Today's Intake", size_hint_y=None, height=50)
        remove_btn.bind(on_release=lambda btn: self.remove_from_today_popup(food_name, btn, parent_popup))
        layout.add_widget(remove_btn)

        close_btn = Button(text="Close", size_hint_y=None, height=50)
        layout.add_widget(close_btn)

        popup = Popup(title=food_name, content=layout, size_hint=(0.8, 0.8))
        remove_btn.popup = popup
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def remove_from_today_popup(self, food_name, btn, parent_popup=None):
        if store.exists("consumed_today"):
            consumed_data = store.get("consumed_today")
            foods = consumed_data.get("foods", [])
            if food_name in foods:
                foods.remove(food_name)
                store.put("consumed_today", **consumed_data)
        btn.popup.dismiss()
        if parent_popup:
            parent_popup.dismiss()
            self.show_todays_intake()


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


# Screen for generating meal plans
class GenerateScreen(BoxLayout):
    meal_plan_text = StringProperty("")


    def safe_float(self, val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0


    def generate_meal_plan(self):
        foods = [store.get(key) for key in store.keys() if key.startswith("food_")]
        if not foods:
            self.meal_plan_text = "No foods logged yet."
            return

        goals = store.get("nutrition_goals") if store.exists("nutrition_goals") else {}
        if not goals:
            self.meal_plan_text = "No nutrition goals set."
            return

        meals = [[], [], []]
        for idx, food in enumerate(foods):
            meals[idx % 3].append(food)

        meal_summaries = []
        for i, meal in enumerate(meals):
            summary = f"Meal {i+1}:\n"
            for food in meal:
                summary += f"  {food.get('name', 'Food')}\n"
            summary += "  (Nutrients: "
            summary += ", ".join([
                f"{k}: {sum(self.safe_float(f.get(k, 0)) for f in meal):.1f}"
                for k in goals.keys()
            ])
            summary += ")\n"
            meal_summaries.append(summary)
        self.meal_plan_text = "\n".join(meal_summaries)

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

class GenerateScreenWrapper(Screen):
    pass

class LoginScreen(Screen):
    def login(self):
        username = self.ids.login_username.text.strip()
        password = self.ids.login_password.text.strip()
        if not username or not password:
            Popup(title="Error", content=Label(text="Please enter both username and password."), size_hint=(0.7, 0.3)).open()
            return
        if store.exists(f"user_{username}"):
            user = store.get(f"user_{username}")
            if user.get("password") == password:
                self.manager.current = "goal"  
            else:
                Popup(title="Error", content=Label(text="Incorrect password."), size_hint=(0.7, 0.3)).open()
        else:
            Popup(title="Error", content=Label(text="User does not exist."), size_hint=(0.7, 0.3)).open()

    def signup(self):
        username = self.ids.login_username.text.strip()
        password = self.ids.login_password.text.strip()
        if not username or not password:
            Popup(title="Error", content=Label(text="Please enter both username and password."), size_hint=(0.7, 0.3)).open()
            return
        if store.exists(f"user_{username}"):
            Popup(title="Error", content=Label(text="User already exists."), size_hint=(0.7, 0.3)).open()
        else:
            store.put(f"user_{username}", password=password)
            Popup(title="Success", content=Label(text="Account created! Please log in."), size_hint=(0.7, 0.3)).open()

class NutritionApp(App):
    def build(self):
        from kivy.lang import Builder
        return Builder.load_file("main.kv")

if __name__ == "__main__":
    NutritionApp().run()
