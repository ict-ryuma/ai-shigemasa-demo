# app/services/prediction_service.py

import pandas as pd
import joblib
import os # osライブラリをインポート

class PredictionService:
    def __init__(self):
        # --- パス指定を修正 ---
        # このファイル自身の場所を基準に、モデルファイルへの絶対パスを構築
        _service_dir = os.path.dirname(__file__)
        _model_path = os.path.join(_service_dir, '..', '..', 'models', 'atlas_model_v2.pkl')
        _columns_path = os.path.join(_service_dir, '..', '..', 'models', 'model_columns_v2.pkl')
        
        # 学習済みモデルとカラム情報を、絶対パスで読み込む
        self.model = joblib.load(_model_path)
        self.model_columns = joblib.load(_columns_path)

    def get_atlas_score(self, customer_data):
        """ 単一の顧客データからATLASスコアを算出する """
        df_customer = pd.DataFrame([customer_data])
        df_customer_dummies = pd.get_dummies(df_customer, columns=['Residence_Type', 'Guarantor', 'Medical_History'], drop_first=True)
        df_customer_processed = df_customer_dummies.reindex(columns=self.model_columns, fill_value=0)
        
        probability_not_delayed = self.model.predict_proba(df_customer_processed)[:, 0]
        return int(probability_not_delayed[0] * 100)

    def run_simulations(self, base_customer_data):
        """ What-Ifシミュレーションを実行し、結果を辞書で返す """
        
        base_score = self.get_atlas_score(base_customer_data)
        results = {
            'base_case': {
                'score': base_score,
                'data': base_customer_data
            }
        }
        
        if base_customer_data.get('Guarantor') == 'No':
            sim1_data = base_customer_data.copy()
            sim1_data['Guarantor'] = 'Yes'
            sim1_score = self.get_atlas_score(sim1_data)
            results['simulation_guarantor'] = {'score': sim1_score, 'data': sim1_data}
            
        if base_customer_data.get('Other_Debt_JPY_10k', 0) > 0:
            sim2_data = base_customer_data.copy()
            sim2_data['Other_Debt_JPY_10k'] = 0
            sim2_score = self.get_atlas_score(sim2_data)
            results['simulation_no_debt'] = {'score': sim2_score, 'data': sim2_data}
            
        return results

# シングルトンインスタンスを作成
prediction_service = PredictionService()