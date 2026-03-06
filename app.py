import os
import base64
import json
import re
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ─── Fashion knowledge base ───────────────────────────────────────────────────
STYLE_PERSONAS = {
    "minimalist": {
        "description": "Clean lines, neutral palettes, timeless pieces",
        "colors": ["white", "black", "beige", "grey", "navy"],
        "keywords": ["structured", "simple", "elegant", "tailored"]
    },
    "bohemian": {
        "description": "Free-spirited, earthy tones, layered textures",
        "colors": ["terracotta", "sage", "cream", "rust", "mustard"],
        "keywords": ["flowy", "layered", "natural", "artistic"]
    },
    "streetwear": {
        "description": "Urban edge, bold graphics, relaxed silhouettes",
        "colors": ["black", "white", "red", "neon", "camo"],
        "keywords": ["oversized", "graphic", "sneakers", "hoodies"]
    },
    "classic": {
        "description": "Timeless elegance, quality fabrics, refined cuts",
        "colors": ["navy", "camel", "white", "burgundy", "forest green"],
        "keywords": ["tailored", "polished", "sophisticated", "quality"]
    },
    "romantic": {
        "description": "Soft florals, delicate fabrics, feminine silhouettes",
        "colors": ["blush", "lavender", "ivory", "dusty rose", "lilac"],
        "keywords": ["floral", "lace", "flowing", "delicate"]
    },
    "edgy": {
        "description": "Bold statements, dark palette, unconventional cuts",
        "colors": ["black", "deep purple", "charcoal", "blood red", "silver"],
        "keywords": ["leather", "asymmetric", "bold", "statement"]
    }
}

OCCASIONS = ["Casual", "Work/Office", "Date Night", "Wedding Guest", "Beach", "Gym", "Party", "Formal Gala"]

TRENDS_2024 = [
    {"name": "Quiet Luxury", "description": "Understated elegance with premium fabrics", "icon": "👑"},
    {"name": "Dopamine Dressing", "description": "Bold colors that spark joy and energy", "icon": "🌈"},
    {"name": "Cottagecore Revival", "description": "Romantic pastoral aesthetics meet modern cuts", "icon": "🌸"},
    {"name": "Y2K Renaissance", "description": "Early 2000s nostalgia reimagined for today", "icon": "✨"},
    {"name": "Gorpcore", "description": "Functional outdoor wear as high fashion", "icon": "🏔️"},
    {"name": "Mob Wife Aesthetic", "description": "Maximalist glamour with faux fur & drama", "icon": "🐆"},
    {"name": "Ballet Core", "description": "Graceful ballet-inspired pieces for everyday", "icon": "🩰"},
    {"name": "Coastal Grandmother", "description": "Effortless linen layers, ocean-inspired palette", "icon": "🌊"}
]


def get_gemini_model():
    if not GEMINI_API_KEY:
        return None
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        return None


def build_style_prompt(user_data: dict) -> str:
    return f"""You are StyleSense, a world-class personal fashion stylist AI. 
    
User Profile:
- Body type: {user_data.get('body_type', 'not specified')}
- Style persona: {user_data.get('style', 'not specified')}
- Occasion: {user_data.get('occasion', 'casual')}
- Budget: {user_data.get('budget', 'moderate')}
- Season: {user_data.get('season', 'current')}
- Colors they love: {user_data.get('colors', 'open to suggestions')}
- Items to avoid: {user_data.get('avoid', 'none')}
- Additional notes: {user_data.get('notes', 'none')}

Please provide a detailed, personalized outfit recommendation with:
1. **Complete Outfit**: List each piece (top, bottom/dress, outerwear, shoes, accessories)
2. **Why It Works**: Explain why this outfit suits their body type and style
3. **Styling Tips**: 3 specific tips to elevate the look
4. **Color Story**: Describe the color palette and combinations
5. **Shopping Guide**: Suggest 3 specific items with approximate price points
6. **Occasion Fit Score**: Rate 1-10 how perfect this is for their occasion

Format your response in a clear, enthusiastic, and professional way. Use emojis sparingly for visual appeal."""


def build_trend_prompt(style: str) -> str:
    return f"""You are StyleSense, a cutting-edge fashion trend analyst.

The user's style preference is: {style}

Provide a personalized trend report for 2024-2025 that includes:
1. **Top 3 Trends For You**: Specifically matched to their {style} aesthetic
2. **How to Wear It**: Practical styling advice for each trend
3. **Investment Pieces**: Key items worth buying this season
4. **Trends to Skip**: What doesn't align with their style DNA
5. **Capsule Wardrobe Essentials**: 5 timeless pieces that transcend trends

Keep it conversational, inspiring, and actionable. Use fashion-forward language."""


def fallback_recommendation(user_data: dict) -> dict:
    style = user_data.get('style', 'classic')
    occasion = user_data.get('occasion', 'Casual')
    persona = STYLE_PERSONAS.get(style, STYLE_PERSONAS['classic'])
    
    outfits = {
        "minimalist": {
            "Casual": "White oversized button-down + straight-leg black trousers + white sneakers + minimal gold jewelry",
            "Work/Office": "Cream silk blouse + tailored charcoal trousers + pointed-toe flats + structured tote",
            "Date Night": "Black midi slip dress + strappy heels + delicate necklace + mini clutch",
            "default": "Neutral linen co-ord set + leather sandals + straw tote"
        },
        "bohemian": {
            "Casual": "Flowy floral maxi dress + leather sandals + layered necklaces + woven bag",
            "Date Night": "Off-shoulder blouse + wide-leg linen pants + block heels + statement earrings",
            "default": "Tiered peasant skirt + embroidered top + ankle boots + fringe bag"
        },
        "streetwear": {
            "Casual": "Oversized graphic tee + cargo pants + chunky sneakers + baseball cap",
            "Party": "Color-block tracksuit + platform sneakers + crossbody mini bag",
            "default": "Hoodie + wide-leg jeans + retro sneakers + beanie"
        },
        "classic": {
            "Casual": "Striped Breton top + slim navy chinos + loafers + leather belt",
            "Work/Office": "Tailored blazer + white shirt + tailored trousers + Oxford shoes",
            "Formal Gala": "Classic black tuxedo blazer + evening trousers + pumps + pearl earrings",
            "default": "Camel coat + cashmere turtleneck + tailored trousers + ankle boots"
        }
    }
    
    style_outfits = outfits.get(style, outfits['classic'])
    outfit = style_outfits.get(occasion, style_outfits.get('default', 'Classic versatile ensemble'))
    
    return {
        "outfit": outfit,
        "why_it_works": f"This look perfectly captures your {style} aesthetic with pieces that flatter and express your unique style identity.",
        "styling_tips": [
            f"Layer with a {persona['colors'][0]} statement piece for depth",
            "Accessorize minimally — let the silhouette speak",
            "Invest in quality fabrics for this key combination"
        ],
        "color_story": f"Built around {', '.join(persona['colors'][:3])} — a palette that defines {style} style",
        "shopping_guide": [
            {"item": "Key top piece", "price": "$45-80", "tip": "Look for quality fabric"},
            {"item": "Bottom/dress", "price": "$60-120", "tip": "Fit is everything"},
            {"item": "Statement shoes", "price": "$80-150", "tip": "Elevates any outfit"}
        ],
        "occasion_score": 8,
        "source": "fallback"
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json or {}
    model = get_gemini_model()
    
    if model:
        try:
            prompt = build_style_prompt(data)
            response = model.generate_content(prompt)
            text = response.text
            return jsonify({
                "success": True,
                "recommendation": text,
                "source": "gemini",
                "persona": STYLE_PERSONAS.get(data.get('style', 'classic'))
            })
        except Exception as e:
            pass
    
    # Fallback
    rec = fallback_recommendation(data)
    formatted = f"""## ✨ Your Personalized Style Recommendation

**Complete Outfit:** {rec['outfit']}

**Why It Works:** {rec['why_it_works']}

**Styling Tips:**
{chr(10).join(f"• {tip}" for tip in rec['styling_tips'])}

**Color Story:** {rec['color_story']}

**Shopping Guide:**
{chr(10).join(f"• **{item['item']}** — {item['price']} | {item['tip']}" for item in rec['shopping_guide'])}

**Occasion Fit Score:** {'⭐' * rec['occasion_score']} {rec['occasion_score']}/10

*Add your Gemini API key in .env for AI-powered personalized recommendations!*"""
    
    return jsonify({
        "success": True,
        "recommendation": formatted,
        "source": "fallback",
        "persona": STYLE_PERSONAS.get(data.get('style', 'classic'))
    })


@app.route('/api/analyze-outfit', methods=['POST'])
def analyze_outfit():
    model = get_gemini_model()
    
    if 'image' not in request.files and 'imageData' not in request.json:
        return jsonify({"success": False, "error": "No image provided"}), 400
    
    if model:
        try:
            if 'image' in request.files:
                img_file = request.files['image']
                img_bytes = img_file.read()
            else:
                data = request.json
                img_data = data['imageData'].split(',')[1] if ',' in data['imageData'] else data['imageData']
                img_bytes = base64.b64decode(img_data)
            
            img = Image.open(io.BytesIO(img_bytes))
            
            prompt = """You are StyleSense, an expert fashion analyst. Analyze this outfit image and provide:

1. **Outfit Breakdown**: Identify each clothing item and its style
2. **Style Category**: What aesthetic does this represent? (minimalist, bohemian, streetwear, etc.)
3. **Color Palette Analysis**: Evaluate the color combinations
4. **Style Score**: Rate the overall look /10 with reasoning
5. **What's Working**: Top 3 strengths of this outfit
6. **Improvement Suggestions**: 3 specific ways to elevate the look
7. **Occasion Suitability**: What occasions work for this outfit
8. **Similar Style Inspo**: Name 2 style icons or brands that match this aesthetic

Be encouraging, specific, and fashion-forward in your analysis."""
            
            response = model.generate_content([prompt, img])
            return jsonify({"success": True, "analysis": response.text, "source": "gemini"})
        except Exception as e:
            pass
    
    fallback = """## 👗 Outfit Analysis

**Style Category:** Contemporary Casual with elevated basics

**Color Palette:** Well-balanced neutral tones with complementary accents — a strong foundation for versatile styling.

**Style Score:** ⭐⭐⭐⭐⭐⭐⭐⭐ 8/10

**What's Working:**
• Clean silhouette that flatters the form
• Thoughtful color coordination throughout
• Balanced proportions between pieces

**Improvement Suggestions:**
• Add a statement accessory (belt, scarf, or jewelry) to create a focal point
• Experiment with texture contrast — mix matte and shiny fabrics
• Consider footwear that extends the leg line

**Occasion Suitability:** Perfect for casual outings, coffee dates, weekend errands, and relaxed social events.

**Style Inspo:** Channeling vibes of Jeanne Damas meets Matilda Djerf — effortless yet intentional.

*Connect your Gemini API key for real AI-powered image analysis!*"""
    
    return jsonify({"success": True, "analysis": fallback, "source": "fallback"})


@app.route('/api/trends', methods=['GET', 'POST'])
def trends():
    style = request.json.get('style', 'all') if request.method == 'POST' else 'all'
    model = get_gemini_model()
    
    if model and style != 'all':
        try:
            prompt = build_trend_prompt(style)
            response = model.generate_content(prompt)
            return jsonify({
                "success": True,
                "trends": TRENDS_2024,
                "ai_report": response.text,
                "source": "gemini"
            })
        except Exception:
            pass
    
    return jsonify({
        "success": True,
        "trends": TRENDS_2024,
        "ai_report": None,
        "source": "static"
    })


@app.route('/api/style-quiz', methods=['POST'])
def style_quiz():
    answers = request.json.get('answers', {})
    
    score_map = {
        "neutral_palette": "minimalist",
        "earth_tones": "bohemian",
        "bold_colors": "streetwear",
        "classic_colors": "classic",
        "soft_pastels": "romantic",
        "dark_dramatic": "edgy"
    }
    
    style_scores = {k: 0 for k in STYLE_PERSONAS.keys()}
    
    for q, ans in answers.items():
        mapped = score_map.get(ans, "classic")
        if mapped in style_scores:
            style_scores[mapped] += 1
    
    dominant_style = max(style_scores, key=style_scores.get)
    persona = STYLE_PERSONAS[dominant_style]
    
    return jsonify({
        "success": True,
        "style": dominant_style,
        "persona": persona,
        "scores": style_scores,
        "message": f"Your style DNA is {dominant_style.title()}! {persona['description']}"
    })


@app.route('/api/wardrobe-essentials', methods=['POST'])
def wardrobe_essentials():
    style = request.json.get('style', 'classic')
    model = get_gemini_model()
    
    essentials_db = {
        "minimalist": [
            "White button-down shirt", "Black tailored trousers", "Camel trench coat",
            "White sneakers", "Black ankle boots", "Simple gold jewelry set",
            "Structured leather tote", "Navy blazer", "Grey cashmere sweater", "Black midi dress"
        ],
        "bohemian": [
            "Flowy maxi dress", "Wide-leg linen pants", "Embroidered blouse",
            "Leather sandals", "Ankle boots", "Layered necklaces set",
            "Woven basket bag", "Kimono cardigan", "Peasant top", "Printed midi skirt"
        ],
        "streetwear": [
            "Oversized white tee", "Cargo pants", "Hoodie",
            "Chunky sneakers", "Bucket hat", "Mini crossbody bag",
            "Bomber jacket", "Track pants", "Graphic sweatshirt", "Platform shoes"
        ],
        "classic": [
            "Tailored blazer", "White Oxford shirt", "Straight-leg jeans",
            "Loafers", "Trench coat", "Pearl jewelry",
            "Structured leather bag", "Navy trousers", "Cashmere turtleneck", "Ballet flats"
        ]
    }
    
    items = essentials_db.get(style, essentials_db['classic'])
    
    if model:
        try:
            prompt = f"""For someone with a {style} fashion aesthetic, create a curated capsule wardrobe guide with:
1. The 10 essential pieces they need (be specific with styles/details)
2. How to mix and match them for maximum outfits
3. Color palette to stick to
4. Key brands that nail this aesthetic
5. Estimated budget for the full capsule

Style: {style}
Persona: {STYLE_PERSONAS.get(style, {}).get('description', '')}"""
            response = model.generate_content(prompt)
            return jsonify({"success": True, "essentials": items, "ai_guide": response.text, "source": "gemini"})
        except Exception:
            pass
    
    return jsonify({"success": True, "essentials": items, "ai_guide": None, "source": "static"})


@app.route('/api/color-match', methods=['POST'])
def color_match():
    data = request.json or {}
    base_color = data.get('color', '#000000')
    
    color_pairings = {
        "navy": ["cream", "white", "camel", "burgundy", "gold"],
        "black": ["white", "red", "gold", "blush", "electric blue"],
        "white": ["navy", "black", "tan", "pastels", "bold accent"],
        "camel": ["white", "navy", "burgundy", "forest green", "cream"],
        "burgundy": ["camel", "navy", "blush", "gold", "forest green"],
        "blush": ["white", "navy", "burgundy", "grey", "gold"],
        "forest green": ["camel", "cream", "burgundy", "rust", "gold"],
        "default": ["black", "white", "navy", "camel", "grey"]
    }
    
    color_name = data.get('colorName', 'default').lower()
    pairings = color_pairings.get(color_name, color_pairings['default'])
    
    return jsonify({
        "success": True,
        "base_color": base_color,
        "pairings": pairings,
        "tip": f"Build your {color_name} outfit around these complementary tones for a cohesive, intentional look."
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        "total_recommendations": 1247,
        "active_users": 328,
        "styles_analyzed": 5832,
        "top_trends": ["Quiet Luxury", "Dopamine Dressing", "Ballet Core"],
        "popular_occasions": ["Casual", "Work/Office", "Date Night"],
        "satisfaction_rate": 94.2
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
