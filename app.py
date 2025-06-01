
from flask import Flask, request, jsonify
from pricing_bot import score_ugc_questionnaire, calculate_ugc_price, estimate_brand_details, UserProfile

app = Flask(__name__)

@app.route("/")
def home():
    return "Creatrate Pricing Bot is running!"

@app.route("/score-ugc-questionnaire", methods=["POST"])
def score_ugc():
    data = request.json
    score = score_ugc_questionnaire(
        skill_level=data.get("skill_level", ""),
        editing=data.get("editing", ""),
        complexity=data.get("complexity", ""),
        content_type=data.get("content_type", ""),
        equipment=data.get("equipment", "")
    )
    return jsonify({"ugc_score": score})

@app.route("/calculate-ugc-price", methods=["POST"])
def calculate_price():
    data = request.json
    user = UserProfile(
        followers=0, avg_engagements=0, avg_views=0, engagement_rate=0,
        base_deliverable_price=data.get("base_price", 100),
        ugc_score=data.get("ugc_score", 5),
        brand_size=data.get("brand_size", "startup"),
        niche_multiplier=data.get("niche_multiplier", 1.0)
    )
    price = calculate_ugc_price(user)
    return jsonify({"price": round(price, 2)})

@app.route("/estimate-brand", methods=["POST"])
def estimate_brand():
    data = request.json
    size, niche = estimate_brand_details(data.get("brand_name", ""))
    return jsonify({"brand_size": size, "niche": niche})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
