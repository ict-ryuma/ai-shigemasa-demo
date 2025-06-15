# ml/train.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def train_model():
    """
    データからAIモデルを学習し、models/ フォルダに保存する関数
    """
    print("モデルの学習を開始します...")

    # --- データの準備 ---
    base_data = {
        '申込番号': [3, 4, 5, 6, 7, 28, 35, 41, 48, 51, 55, 60, 65, 70],
        'Age': [46, 48, 51, 34, 54, 30, 40, 25, 50, 60, 28, 39, 45, 58],
        'Residence_Type': ['Own_House', 'Own_House', 'Own_House', 'Rental', 'Own_House', 'Rental', 'Family_House', 'Rental', 'Company_House', 'Own_House', 'Rental', 'Own_House', 'Rental', 'Family_House'],
        'Years_at_Work': [10, 25, 15, 1, 30, 5, 12, 2, 20, 35, 3, 15, 8, 25],
        'Annual_Income_JPY_10k': [600, 600, 800, 400, 1000, 450, 700, 300, 900, 1200, 350, 800, 550, 950],
        'Other_Debt_JPY_10k': [0, 0, 0, 100, 100, 200, 50, 150, 0, 30, 80, 20, 120, 0],
        'Guarantor': ['No', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No']
    }
    df = pd.DataFrame(base_data)
    new_data = {
        '申込番号': [3, 4, 5, 6, 7, 28, 35, 41, 48, 51, 55, 60, 65, 70],
        'Medical_History': ['なし', '高血圧', 'なし', 'なし', '糖尿病', '高血圧', 'なし', 'なし', '高血圧', '糖尿病', 'なし', 'なし', '高血圧', 'なし'],
        'Claim_Count': [24, 12, 36, 12, 24, 48, 12, 6, 24, 36, 12, 12, 48, 24],
        'Payment_Count': [24, 12, 36, 12, 20, 40, 12, 5, 22, 30, 10, 12, 42, 24]
    }
    df_new = pd.DataFrame(new_data)
    df_full = pd.merge(df, df_new, on='申込番号')
    delayed_ids = [7, 28, 41, 48, 51, 55, 65]
    df_full['is_delayed'] = df_full['申込番号'].apply(lambda x: 1 if x in delayed_ids else 0)

    # --- 特徴量の作成 ---
    df_full['Payment_Rate'] = (df_full['Payment_Count'] / df_full['Claim_Count']).fillna(1.0)
    
    X = df_full.drop(columns=['申込番号', 'is_delayed', 'Claim_Count', 'Payment_Count'])
    y = df_full['is_delayed']
    
    X_dummies = pd.get_dummies(X, columns=['Residence_Type', 'Guarantor', 'Medical_History'], drop_first=True)
    
    # --- モデル学習 ---
    model = RandomForestClassifier(random_state=42)
    model.fit(X_dummies, y)
    
    # --- モデルの保存 ---
    # modelsフォルダがなければ作成
    if not os.path.exists('models'):
        os.makedirs('models')
        
    joblib.dump(model, 'models/atlas_model_v2.pkl')
    joblib.dump(X_dummies.columns, 'models/model_columns_v2.pkl')
    
    print("モデル『atlas_model_v2.pkl』が models/ フォルダに保存されました。")

if __name__ == '__main__':
    train_model()