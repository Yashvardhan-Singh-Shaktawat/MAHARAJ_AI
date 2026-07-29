from django.db import models

# Create your models here.
import pandas as pd
import numpy as np
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
class MLEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLEngine, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        print("--- Loading ML Data Models ---")
        base_path = os.path.join(settings.BASE_DIR, 'recommendations', 'data')
        
        # Load CSVs
        ind = pd.read_csv(os.path.join(base_path, 'indian_recipes.csv'))
        world = pd.read_csv(os.path.join(base_path, 'world_recipes.csv'))
        self.df = pd.concat([ind, world], ignore_index=True)
        
        # Fill NaN steps for world recipes
        self.df['steps'] = self.df['steps'].fillna("Steps not available in dataset.")

        # Load Steps JSON
        with open(os.path.join(base_path, 'steps.json')) as f:
            self.steps_map = json.load(f)
            
        # Create Embeddings (Simplified for startup speed)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=2000)
        self.tfidf_matrix = self.vectorizer.fit_transform(
            (self.df['recipe_name'] + " " + self.df['ingredients'] + " " + self.df['diet_type']).fillna('')
        )
        print("--- Data Loaded Successfully ---")

    def translate_response(self, text, target_lang):
        if target_lang == 'en': return text
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except:
            return text

    # --- MODEL 1: DIET PLANNER ---
    def recommend_diet(self, goal, age, weight, sugar_issue, language):
        # Logic: Filter recipes based on nutritional needs
        
        filtered_df = self.df.copy()
        
        # Sugar Logic
        if sugar_issue == 'yes':
            filtered_df = filtered_df[filtered_df['sugar_g'] < 5]
            filtered_df = filtered_df[filtered_df['carbs_g'] < 40]

        # Goal Logic
        if goal == 'loss':
            # Low Calorie, High Protein
            filtered_df = filtered_df[(filtered_df['calories'] < 350) & (filtered_df['protein_g'] > 10)]
        elif goal == 'gain':
            # High Calorie, High Protein
            filtered_df = filtered_df[(filtered_df['calories'] > 400) & (filtered_df['protein_g'] > 15)]
        
        # Get 3 random samples
        if filtered_df.empty:
            recs = self.df.sample(3) # Fallback
        else:
            recs = filtered_df.sample(min(3, len(filtered_df)))
        
        response_text = f"Based on your goal ({goal}), here is a recommended plan:\n\n"
        for _, row in recs.iterrows():
            response_text += f"🍲 {row['recipe_name']}\n   - Calories: {row['calories']} | Protein: {row['protein_g']}g\n\n"
            
        return self.translate_response(response_text, language)

    # --- MODEL 2: FOOD/RECIPE RECOMMENDER ---
    def recommend_food(self, query, allergies, language):
        # 1. Filter out Allergies
        temp_df = self.df.copy()
        if allergies:
            allergy_list = [x.strip().lower() for x in allergies.split(',')]
            for allergen in allergy_list:
                # Remove rows where ingredients contain the allergen
                temp_df = temp_df[~temp_df['ingredients'].str.lower().str.contains(allergen, na=False)]

        # 2. Find Similarity
        query_vec = self.vectorizer.transform([query])
        # We must index the matrix to match the filtered dataframe
        subset_indices = temp_df.index
        if len(subset_indices) == 0:
            return self.translate_response("Sorry, no recipes found matching your strict criteria.", language)
            
        subset_matrix = self.tfidf_matrix[subset_indices]
        
        scores = cosine_similarity(query_vec, subset_matrix).flatten()
        top_indices = scores.argsort()[-1:][::-1] # Get top 1 best match
        
        best_match_idx = subset_indices[top_indices[0]]
        recipe = self.df.iloc[best_match_idx]
        
        # Format Instructions
        steps_text = recipe['steps']
        
        response = f"🍽️ Recommended: {recipe['recipe_name']}\n"
        response += f"🌍 Cuisine: {recipe['cuisine']}\n"
        response += f"🥕 Ingredients: {recipe['ingredients']}\n"
        response += f"🔥 Calories: {recipe['calories']}\n\n"
        response += f"👨‍🍳 Cooking Steps:\n{steps_text}"
        
        return self.translate_response(response, language)


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_ingredients = models.TextField(default="")   # e.g., "paneer, chicken"
    disliked_ingredients = models.TextField(default="") # e.g., "mushroom"
    allergies = models.TextField(default="")

    def __str__(self):
        return self.user.username

class RecipeFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_name = models.CharField(max_length=200)
    action = models.CharField(max_length=10) # 'like'
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.username} - {self.recipe_name}"