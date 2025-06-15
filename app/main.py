# app/main.py

from flask import Flask, request, jsonify
from services.prediction_service import prediction_service # サービス部品をインポート

# Flaskアプリケーションを初期化
app = Flask(__name__)
app.json.ensure_ascii = False # この行を追加

@app.route('/')
def index():
    return "ATLAS API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    """
    顧客データをJSONで受け取り、シミュレーション結果をJSONで返すエンドポイント
    """
    if not request.json:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    customer_data = request.json
    
    # 必須キーのチェック
    required_keys = ['Age', 'Residence_Type', 'Years_at_Work', 'Annual_Income_JPY_10k', 'Other_Debt_JPY_10k', 'Guarantor', 'Medical_History', 'Payment_Rate']
    if not all(key in customer_data for key in required_keys):
         return jsonify({"error": f"Missing required keys. Required: {required_keys}"}), 400

    try:
        # 予測サービスを使ってシミュレーションを実行
        results = prediction_service.run_simulations(customer_data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Webサーバーを起動
    app.run(debug=True, port=5000)