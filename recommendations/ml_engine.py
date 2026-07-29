import pandas as pd
import numpy as np
import json
import os
import urllib.parse
import random
import re
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator
from django.conf import settings

class MLEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLEngine, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        print("--- [BRAIN] INITIALIZING AI CHEF (V21.1 - ERROR FREE) ---")
        base_path = os.path.join(settings.BASE_DIR, 'recommendations', 'data')
        
        self.df = pd.DataFrame()
        self.diet_df = pd.DataFrame()
        self.ex_df = pd.DataFrame()
        self.steps_map = {}
        self.vectorizer = None
        self.tfidf_matrix = None
        self.vocabulary = set()

        files = {
            'main': ['indian_recipes.csv', 'world_recipes.csv', 'indian_recipes (1).csv', 'world_recipes (1).csv'],
            'steps': ['steps.json', 'steps (1).json'],
            'diet': ['diet_planner_beauty_ml_dataset.csv'],
            'exercise': ['exercise_nutrition_daywise_dataset.csv']
        }

        try:
            # 1. LOAD RECIPES
            dfs = []
            for fname in files['main']:
                fpath = os.path.join(base_path, fname)
                if os.path.exists(fpath):
                    try:
                        temp = pd.read_csv(fpath)
                        temp.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in temp.columns]
                        rename_map = {
                            'recipename': 'recipe_name', 'name': 'recipe_name', 'title': 'recipe_name',
                            'instructions': 'steps', 'guide': 'steps', 'method': 'steps',
                            'ingredients': 'ingredients', 'image_url': 'image_url', 'imageurl': 'image_url',
                            'calories': 'calories', 'protein': 'protein_g', 'fat': 'fat_g', 'sugar': 'sugar_g'
                        }
                        temp.rename(columns=rename_map, inplace=True)
                        dfs.append(temp)
                    except: pass

            if dfs:
                self.df = pd.concat(dfs, ignore_index=True)
                for col in ['recipe_name', 'ingredients', 'cuisine', 'image_url', 'steps']:
                    if col not in self.df.columns: self.df[col] = ""
                
                for col in ['calories', 'protein_g', 'fat_g', 'sugar_g']:
                    if col not in self.df.columns: self.df[col] = 0.0
                    else: self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0.0)

                self.df['recipe_name'] = self.df['recipe_name'].astype(str).fillna("Unknown Recipe")
                self.df['ingredients'] = self.df['ingredients'].astype(str).fillna("")
                self.df['cuisine'] = self.df['cuisine'].astype(str).fillna("Global")
                self.df['steps'] = self.df['steps'].astype(str).fillna("")
                
                # 🧠 BUILD VOCABULARY
                combined_text = (
                    self.df['recipe_name'] + " " + 
                    self.df['ingredients'] + " " + 
                    self.df['cuisine']
                ).fillna('')

                full_text_blob = combined_text.str.lower().str.cat(sep=' ')
                self.vocabulary = set(re.findall(r'\b[a-z]{3,}\b', full_text_blob))
                
                chat_words = {'yes', 'no', 'ok', 'okay', 'hi', 'hello', 'hey', 'menu', 'thanks', 'thank', 'bye', 'good', 'bad', 'cool', 'sure', 'ready', 'surprise', 'spicy', 'sweet', 'dessert', 'dinner', 'lunch', 'breakfast'}
                self.vocabulary.update(chat_words)

                # Vectorizer
                self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
                self.tfidf_matrix = self.vectorizer.fit_transform(combined_text)

                non_veg_keywords = ['chicken', 'fish', 'meat', 'beef', 'pork', 'lamb', 'egg', 'prawn']
                def classify_veg(row):
                    text = (str(row.get('ingredients', '')) + " " + str(row.get('recipe_name', ''))).lower()
                    for word in non_veg_keywords:
                        if word in text: return 0 
                    return 1 
                self.df['is_veg'] = self.df.apply(classify_veg, axis=1)
                
                print(f"[OK] Loaded Recipes: {len(self.df)} | Vocabulary Size: {len(self.vocabulary)}")

            # 2. LOAD DIET
            diet_path = next((os.path.join(base_path, f) for f in files['diet'] if os.path.exists(os.path.join(base_path, f))), None)
            if diet_path:
                self.diet_df = pd.read_csv(diet_path)
                self.diet_df.columns = [c.strip() for c in self.diet_df.columns]
                self.diet_image_col = next((c for c in self.diet_df.columns if c.lower() in ['image', 'image url', 'url', 'photo']), None)

            # 3. LOAD EXERCISE
            ex_path = next((os.path.join(base_path, f) for f in files['exercise'] if os.path.exists(os.path.join(base_path, f))), None)
            if ex_path:
                self.ex_df = pd.read_csv(ex_path)
                self.ex_df.columns = [c.strip() for c in self.ex_df.columns]
                self.ex_col_name = next((c for c in self.ex_df.columns if c.lower() in ['exercises', 'exercise', 'step', 'steps']), 'Exercises')

            # 4. LOAD STEPS
            steps_path = next((os.path.join(base_path, f) for f in files['steps'] if os.path.exists(os.path.join(base_path, f))), None)
            if steps_path:
                try:
                    with open(steps_path, 'r', encoding='utf-8') as f:
                        self.steps_map = json.load(f)
                except: pass

        except Exception as e:
            print(f"[ERROR] DATA ERROR: {e}")

    # --- 🛠️ HELPER FUNCTIONS ---
    def get_steps(self, row):
        csv_steps = str(row.get('steps', '')).strip()
        if len(csv_steps) > 15 and csv_steps.lower() != 'nan': return csv_steps
        rec_id = str(row.get('recipe_id', ''))
        if rec_id in self.steps_map:
            raw = self.steps_map[rec_id]
            if isinstance(raw, list): return "\n".join([f"• {s}" for s in raw])
            return str(raw)
        return f"1. Prepare ingredients for {row['recipe_name']}.\n2. Cook thoroughly.\n3. Serve hot."

    def get_image(self, row): 
        csv_link = str(row.get('image_url', '')).strip()
        if len(csv_link) > 5: return csv_link
        return f"https://placehold.co/600x400/orange/white?text={urllib.parse.quote(row['recipe_name'])}"

    def get_recipe_details(self, recipe_name):
        details = {
            "image": self.search_wikipedia_image(recipe_name), 
            "steps": f"1. Prepare {recipe_name}.\n2. Cook and enjoy.", 
            "ingredients": "Not listed", 
            "cuisine": "Global"
        }
        if self.df.empty: return details

        match = self.df[self.df['recipe_name'].str.contains(recipe_name, case=False, na=False)]
        if not match.empty:
            row = match.iloc[0]
            details['steps'] = self.get_steps(row)
            details['ingredients'] = str(row.get('ingredients', ''))
            details['cuisine'] = str(row.get('cuisine', 'Global'))
            details['image'] = self.get_image(row)
            
        return details

    def search_wikipedia_image(self, recipe_name):
        clean = urllib.parse.quote(recipe_name)
        return f"https://placehold.co/600x400/orange/white?text={clean}"

    def translate_text(self, text, target_lang):
        if not text or target_lang == 'en': return text
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text[:4500])
        except: return text

    def _normalize_query(self, query):
        words = query.lower().split()
        fixed_words = []
        for w in words:
            if w.endswith('es'): w_sing = w[:-2]
            elif w.endswith('s') and not w.endswith('ss'): w_sing = w[:-1]
            else: w_sing = w
            
            if self.vocabulary:
                matches = get_close_matches(w_sing, self.vocabulary, n=1, cutoff=0.85)
                fixed_words.append(matches[0] if matches else w_sing)
            else:
                fixed_words.append(w_sing)
        return " ".join(fixed_words)

    # --- 🎯 DIET PLANNER ---
    def recommend_diet(self, current_weight, target_weight, duration, workout_type, age, sugar_issue, diet_style, food_type, language):
        try:
            # 1. SAFETY CHECKS
            try:
                cw = float(current_weight) if current_weight and str(current_weight).strip() else 0
                tw = float(target_weight) if target_weight and str(target_weight).strip() else 0
                days = int(duration) if duration and str(duration).strip() else 30
                
                if cw < 20 or cw > 400: return self.error_plan("Please enter a realistic weight (20kg - 400kg).", language)
                if tw <= 5: return self.error_plan("Target weight cannot be near zero.", language)
                if days < 1: return self.error_plan("Duration must be at least 1 day.", language)
                
                if abs(cw - tw) / days > 1.0:
                    return self.error_plan(f"Losing {abs(cw-tw)}kg in {days} days is not safe. Increase duration.", language)

                diff = tw - cw
                if diff < -0.5: dataset_goal = 'Weight Loss'
                elif diff > 0.5: dataset_goal = 'Weight Gain'
                else: dataset_goal = 'Weight Maintain'
                
                if dataset_goal == 'Weight Maintain':
                    advice_text = f"Goal: Maintain {cw}kg. Balanced nutrition."
                else:
                    daily_change = int((abs(diff) * 7700) / days)
                    direction = "Deficit" if diff < 0 else "Surplus"
                    advice_text = f"Goal: {cw}kg → {tw}kg. Daily {direction}: ~{daily_change} kcal."
            except:
                return self.error_plan("Please enter valid numbers.", language)

            # 2. PLAN GENERATION
            plan = []
            target_calories = 0
            beauty_tip = {}
            exercise_plan = {}
            selected_day = "Day 1"
            
            if not self.diet_df.empty:
                candidates = self.diet_df[self.diet_df['Goal'] == dataset_goal]
                
                if food_type == 'Veg': 
                    temp = candidates[candidates['Diet Type'].isin(['Vegetarian', 'Vegan'])]
                    if not temp.empty: candidates = temp
                elif food_type == 'Non-Veg': 
                    temp = candidates[candidates['Diet Type'] == 'Non-Vegetarian']
                    if not temp.empty: candidates = temp
                
                if workout_type:
                    match_type = 'Home' if 'Home' in workout_type else 'Gym'
                    temp = candidates[candidates['Workout Type'].str.contains(match_type, case=False, na=False)]
                    if not temp.empty: candidates = temp

                if not candidates.empty:
                    selected_day = random.choice(candidates['Day'].unique())
                    day_plan = candidates[candidates['Day'] == selected_day]
                    if len(day_plan) < 3: day_plan = candidates.sample(min(4, len(candidates)))

                    if not day_plan.empty:
                        row = day_plan.iloc[0]
                        beauty_tip = {
                            "goal": self.translate_text(str(row.get('Beauty Goal', 'Wellness')), language),
                            "drink": self.translate_text(str(row.get('Beauty Drink Recommendation', 'Water')), language),
                            "instruction": self.translate_text(str(row.get('Beauty Care Instruction', 'Sleep well')), language)
                        }
                        
                        seen = set()
                        for m_type in ['Breakfast', 'Lunch', 'Snack', 'Dinner']:
                            rows = day_plan[day_plan['Meal Type'] == m_type]
                            if rows.empty: rows = day_plan 
                            valid_rows = rows[~rows.index.isin(seen)]
                            if valid_rows.empty: valid_rows = rows
                            if not valid_rows.empty:
                                choice = valid_rows.iloc[0]
                                seen.add(choice.name)
                                img_url = ""
                                if self.diet_image_col: img_url = str(choice.get(self.diet_image_col, '')).strip()
                                details = self.get_recipe_details(choice['Recipe'])
                                if not img_url or len(img_url) < 5: img_url = details['image']
                                
                                plan.append({
                                    "meal": self.translate_text(m_type, language),
                                    "name": self.translate_text(choice['Recipe'], language),
                                    "calories": int(choice.get('Calories (kcal)', 0)),
                                    "protein": int(choice.get('Protein (g)', 0)),
                                    "image": img_url,
                                    "steps": self.translate_text(details['steps'], language),
                                    "ingredients": self.translate_text(details['ingredients'], language),
                                    "cuisine": self.translate_text(details['cuisine'], language)
                                })
                                target_calories += int(choice.get('Calories (kcal)', 0))

            if not self.ex_df.empty:
                ex_cands = self.ex_df[self.ex_df['Goal'] == dataset_goal]
                loc = 'Gym' if workout_type and 'Gym' in workout_type else 'Home'
                temp = ex_cands[ex_cands['Location'] == loc]
                if not temp.empty: ex_cands = temp
                day_match = ex_cands[ex_cands['Day'] == selected_day]
                if not day_match.empty: ex_row = day_match.iloc[0]
                elif not ex_cands.empty: ex_row = ex_cands.sample(1).iloc[0]
                else: ex_row = None
                
                if ex_row is not None:
                    raw_ex = str(ex_row.get(self.ex_col_name, 'General Activity'))
                    ex_list = [self.translate_text(e.strip(), language) for e in raw_ex.split(',')]
                    exercise_plan = {
                        "name": self.translate_text(str(ex_row.get('Workout_Type', 'Workout')), language),
                        "exercises": ex_list,
                        "duration": str(ex_row.get('Duration_Minutes', '30')),
                        "intensity": self.translate_text(str(ex_row.get('Intensity', 'Medium')), language),
                        "calories": str(ex_row.get('Calories_Burned', '200')),
                        "benefits": self.translate_text(str(ex_row.get('Benefits', 'Health')), language)
                    }

            if not plan: return self.recommend_diet_fallback(dataset_goal, food_type, language)

            return {"advice": self.translate_text(advice_text, language), "target_calories": target_calories, "plan": plan, "beauty_tip": beauty_tip, "exercise_plan": exercise_plan}
        except Exception as e:
            return self.recommend_diet_fallback("Weight Maintain", "All", language)

    def error_plan(self, message, language):
        return {"advice": self.translate_text(f"⚠️ {message}", language), "target_calories": 0, "plan": [], "beauty_tip": {}, "exercise_plan": {}}

    def recommend_diet_fallback(self, goal, food_type, language):
        if self.df.empty: return self.error_plan("Database not loaded.", language)
        filtered_df = self.df.copy()
        if food_type == 'Veg': filtered_df = filtered_df[filtered_df['is_veg'] == 1]
        elif food_type == 'Non-Veg': filtered_df = filtered_df[filtered_df['is_veg'] == 0]
        
        plan = []
        for meal in ['Breakfast', 'Lunch', 'Snack', 'Dinner']:
            if not filtered_df.empty:
                row = filtered_df.sample(1).iloc[0]
                details = self.get_recipe_details(row['recipe_name'])
                plan.append({
                    "meal": self.translate_text(meal, language),
                    "name": self.translate_text(row['recipe_name'], language),
                    "calories": int(row['calories']),
                    "protein": int(row['protein_g']),
                    "image": details['image'],
                    "steps": self.translate_text(details['steps'], language),
                    "ingredients": self.translate_text(details['ingredients'], language),
                    "cuisine": self.translate_text(details['cuisine'], language)
                })
        beauty = {"goal": "Hydration", "drink": "Water", "instruction": "Drink 8 glasses daily."}
        exercise_plan = {"name": "Active Walk", "exercises": ["30 min brisk walking"], "duration": "30", "intensity": "Low", "calories": "150"}
        return {"advice": self.translate_text("Generated a healthy standard plan.", language), "target_calories": 2000, "plan": plan, "beauty_tip": beauty, "exercise_plan": exercise_plan}

    # --- 🍔 INTELLIGENT WAITER ---
    def recommend_food(self, query, allergies, region, food_type, language, user_history=[]):
        try:
            if self.df.empty: return {"message": "Kitchen is opening...", "results": []}
            
            # 1. CLEAN INPUT
            q_clean = re.sub(r'[^\w\s]', '', query).lower().strip()
            
            # 2. PRIORITY CONTEXT
            force_search = False
            priority_terms = ['chinese', 'italian', 'indian', 'mexican', 'thai', 'dessert', 'sweet', 'dinner', 'lunch', 'breakfast']
            if any(p in q_clean for p in priority_terms): 
                force_search = True
            
            if not force_search:
                # 🧠 VOCABULARY GUARD
                user_words = re.findall(r'\b[a-z]{3,}\b', q_clean)
                if user_words:
                    is_valid = False
                    for w in user_words:
                        if w in self.vocabulary or get_close_matches(w, self.vocabulary, n=1, cutoff=0.85):
                            is_valid = True
                            break
                    if not is_valid:
                        return {"message": self.translate_text("I don't recognize that word. Try 'Paneer', 'Chicken', or 'Chinese'.", language), "results": [], "is_chat": True}

                # CHAT INTENTS
                chat_triggers = {
                    'yes': "Great! What ingredient? (e.g. Paneer)",
                    'sure': "Awesome! What flavor? (Spicy, Sweet)",
                    'ok': "Ready! Type a dish name.",
                    'no': "No problem. Tell me what you want.",
                    'thanks': "Happy Cooking! 👨‍🍳"
                }
                if q_clean in chat_triggers:
                     return {"message": self.translate_text(chat_triggers[q_clean], language), "results": [], "is_chat": True}

                intents = {
                    'menu': "I specialize in Indian, Chinese, Italian, and Mexican! What's your mood?",
                    'surprise': "SURPRISE_ME",
                    'hello': "Namaste! Tell me what you crave.",
                    'hi': "Hello! Ready to cook?"
                }
                for key, response in intents.items():
                    if key in q_clean:
                        if response == "SURPRISE_ME":
                            candidates = self.df.sample(3)
                            results = [self._format_recipe(r, language) for _, r in candidates.iterrows()]
                            return {"message": self.translate_text("Here are 3 Chef's Specials!", language), "results": results, "is_chat": False}
                        return {"message": self.translate_text(response, language), "results": [], "is_chat": True}

            # 3. SEARCH PREP
            q_nlp = self._normalize_query(q_clean)
            
            temp = self.df.copy()
            if food_type == 'Veg': temp = temp[temp['is_veg'] == 1]
            elif food_type == 'Non-Veg': temp = temp[temp['is_veg'] == 0]
            
            if region and region != 'All':
                temp['region_score'] = temp['cuisine'].astype(str).str.contains(region, case=False).astype(int) * 0.5
            else: temp['region_score'] = 0
            
            if allergies:
                for a in [x.strip().lower() for x in allergies.split(',')]:
                    if a: temp = temp[~temp['ingredients'].astype(str).str.lower().str.contains(a, na=False)]

            # 🍭 SWEET TOOTH LOGIC
            if 'sweet' in q_clean or 'dessert' in q_clean:
                dessert_keywords = ['cake', 'halwa', 'kheer', 'barfi', 'laddu', 'payasam', 'mousse', 'chocolate', 'cookie', 'ice cream', 'pudding', 'jamun', 'rasgulla', 'mysore pak', 'peda', 'jalebi', 'gulab', 'mitai', 'sugar']
                def dessert_score(row):
                    txt = (str(row['recipe_name']) + " " + str(row['cuisine'])).lower()
                    if any(k in txt for k in dessert_keywords): return 2.0
                    return 0
                temp['sweet_score'] = temp.apply(dessert_score, axis=1)
                
                savory_keywords = ['chicken', 'garlic', 'onion', 'curry', 'masala', 'chilli', 'fish', 'prawn', 'egg', 'fry', 'salt']
                def savory_penalty(row):
                    txt = (str(row['recipe_name']) + " " + str(row['ingredients'])).lower()
                    if any(k in txt for k in savory_keywords): return -5.0
                    return 0
                temp['score'] = temp['sweet_score'] + temp.apply(savory_penalty, axis=1)
            else:
                temp['score'] = 0

            # 4. VECTOR SEARCH
            flavor_map = {'spicy': 'chilli pepper masala hot', 'healthy': 'salad boiled soup'}
            boost = ""
            for k, v in flavor_map.items():
                if k in q_clean: boost += " " + v

            final_q = f"{q_nlp} {boost}"
            if self.vectorizer:
                vec = self.vectorizer.transform([final_q])
                sim = cosine_similarity(vec, self.tfidf_matrix[temp.index]).flatten()
                temp['score'] += sim + temp['region_score']
                
                temp.loc[temp['recipe_name'].str.contains(q_nlp, case=False), 'score'] += 0.5
                temp.loc[temp['cuisine'].str.contains(q_nlp, case=False), 'score'] += 0.5

                if user_history:
                    history_text = " ".join(user_history).lower()
                    def get_personal_score(row):
                        score = 0
                        if row['recipe_name'].lower() in history_text: score += 0.5
                        row_words = set(str(row['ingredients']).lower().split())
                        hist_words = set(history_text.split())
                        if len(row_words.intersection(hist_words)) > 0: score += 0.2
                        return score
                    temp['personal_score'] = temp.apply(get_personal_score, axis=1)
                    temp['score'] += temp['personal_score']

                candidates = temp.sort_values('score', ascending=False).head(15)
                candidates = candidates[candidates['score'] > 0.15]
            else:
                candidates = temp.head(10)

            results = [self._format_recipe(r, language) for _, r in candidates.iterrows()]
            
            if not results:
                return {"message": self.translate_text(f"No good matches for '{q_clean}'. Try a simpler ingredient.", language), "results": [], "is_chat": True}

            msg = self.translate_text(f"Here are the best matches for {q_clean}.", language)
            return {"message": msg, "results": results, "is_chat": False}

        except Exception as e:
            print(f"SEARCH ERROR: {e}")
            return {"message": "Error searching.", "results": []}

    def _format_recipe(self, row, language):
        return {
            "name": self.translate_text(row['recipe_name'], language),
            "cuisine": self.translate_text(str(row.get('cuisine', 'Global')), language),
            "calories": int(row.get('calories', 0)),
            "ingredients": self.translate_text(str(row.get('ingredients', '')), language),
            "steps": self.translate_text(self.get_steps(row), language),
            "image": self.get_image(row)
        }