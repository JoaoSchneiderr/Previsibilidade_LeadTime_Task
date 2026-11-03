"""
Etapa 4: treinamento e comparação dos modelos.
- Divisão temporal: 80% mais antigas = treino, 20% mais recentes = teste
- Ajuste de hiperparâmetros: busca em grade + validação walk-forward (TimeSeriesSplit, 5 blocos) no treino
- Alvo treinado em escala log (log1p) e convertido de volta para horas na previsão
- Métricas no teste, em horas: MAE, RMSE, R²
- Baseline: média histórica do treino por Tipo de item x Complexidade
"""
import json, time, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from modelos_tcc import CatBoostCategorico

warnings.filterwarnings('ignore')
SEED = 42
X_all = pd.read_pickle('atributos.pkl').sort_values('Criado_dt').reset_index(drop=True)

CAT = ['tipo_item', 'projeto', 'modulo', 'complexidade', 'vertical', 'origem_bug', 'desenvolvedor', 'analista_requisitos']
NUM = ['prioridade_ord', 'complexidade_ord', 'eh_subtarefa', 'vinculada_epic', 'titulo_caracteres', 'titulo_palavras',
       'mes_criacao', 'dia_semana_criacao', 'hora_criacao', 'carga_dev_abertas', 'backlog_projeto_abertas',
       'dev_tasks_concluidas_antes', 'dev_lead_time_mediano_passado', 'tipo_lead_time_mediano_passado']
FEATS = CAT + NUM

corte = int(len(X_all) * 0.8)
tr, te = X_all.iloc[:corte], X_all.iloc[corte:]
Xtr, ytr, Xte, yte = tr[FEATS], tr['lead_time_horas'], te[FEATS], te['lead_time_horas']
info = dict(n_treino=len(tr), n_teste=len(te),
            treino_de=str(tr['Criado_dt'].min()), treino_ate=str(tr['Criado_dt'].max()),
            teste_de=str(te['Criado_dt'].min()), teste_ate=str(te['Criado_dt'].max()))
print(info)

ohe = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='infrequent_if_exist', min_frequency=10, sparse_output=False), CAT),
    ('num', SimpleImputer(strategy='median', add_indicator=True), NUM)])

modelos = {
    'Gradient Boosting': (GradientBoostingRegressor(random_state=SEED),
                          {'n_estimators': [200, 400], 'learning_rate': [0.03, 0.1], 'max_depth': [3, 5]}, True),
    'Random Forest': (RandomForestRegressor(random_state=SEED, n_jobs=2),
                      {'n_estimators': [300], 'max_depth': [None, 12], 'min_samples_leaf': [1, 5, 10]}, True),
    'XGBoost': (XGBRegressor(random_state=SEED, n_jobs=2, subsample=0.8, colsample_bytree=0.8),
                {'n_estimators': [300, 600], 'learning_rate': [0.03, 0.1], 'max_depth': [4, 6]}, True),
    'LightGBM': (LGBMRegressor(random_state=SEED, n_jobs=2, verbose=-1, subsample=0.8, subsample_freq=1, colsample_bytree=0.8),
                 {'n_estimators': [300, 600], 'learning_rate': [0.03, 0.1], 'num_leaves': [15, 31]}, True),
    'CatBoost': (CatBoostCategorico(cat_features=tuple(CAT), random_seed=SEED),
                 {'iterations': [500, 1000], 'learning_rate': [0.03, 0.1], 'depth': [4, 6]}, False),
}

def metricas(y, p):
    return dict(MAE=mean_absolute_error(y, p), RMSE=mean_squared_error(y, p) ** 0.5, R2=r2_score(y, p),
                MdAE=median_absolute_error(y, p), R2_log=r2_score(np.log1p(y), np.log1p(np.clip(p, 0, None))))

# janela de sensibilidade: teste sem as tasks criadas nos 90 dias anteriores à extração
EXTRACAO = pd.Timestamp('2026-09-22')
maduras = (te['Criado_dt'] <= EXTRACAO - pd.Timedelta(days=90)).values

# ---------------- baseline ----------------
g2 = tr.groupby(['tipo_item', 'complexidade'])['lead_time_horas'].mean()
g1 = tr.groupby('tipo_item')['lead_time_horas'].mean()
glob = ytr.mean()
p_base = np.array([g2.get((a, b), g1.get(a, glob)) for a, b in zip(te['tipo_item'], te['complexidade'])])
resultados = [dict(Modelo='Baseline (média por tipo x complexidade)', **metricas(yte, p_base),
                   MAE_maduras=mean_absolute_error(yte[maduras], p_base[maduras]), melhores_parametros='-', tempo_s=0)]
previsoes = {'Baseline': p_base}

# ---------------- modelos ----------------
cv = TimeSeriesSplit(n_splits=5)
ajustados = {}
for nome, (est, grade, usa_ohe) in modelos.items():
    t0 = time.time()
    pipe = Pipeline([('prep', ohe), ('model', est)]) if usa_ohe else Pipeline([('model', est)])
    ttr = TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1, check_inverse=False)
    grid = {f'regressor__model__{k}': v for k, v in grade.items()}
    gs = GridSearchCV(ttr, grid, cv=cv, scoring='neg_mean_absolute_error', n_jobs=1, refit=True)
    gs.fit(Xtr, ytr)
    p = np.clip(gs.predict(Xte), 0, None)
    previsoes[nome] = p
    ajustados[nome] = gs.best_estimator_
    bp = {k.replace('regressor__model__', ''): v for k, v in gs.best_params_.items()}
    resultados.append(dict(Modelo=nome, **metricas(yte, p), MAE_maduras=mean_absolute_error(yte[maduras], p[maduras]),
                           MAE_validacao=-gs.best_score_, melhores_parametros=json.dumps(bp), tempo_s=round(time.time() - t0)))
    print(nome, {k: round(v, 3) if isinstance(v, float) else v for k, v in resultados[-1].items()}, flush=True)

res = pd.DataFrame(resultados)
melhor = res.iloc[1:].sort_values('MAE').iloc[0]['Modelo']
print('melhor:', melhor)

# ---------------- importância dos atributos (permutação, no teste, em MAE) ----------------
pi = permutation_importance(ajustados[melhor], Xte, yte, scoring='neg_mean_absolute_error', n_repeats=10, random_state=SEED, n_jobs=1)
imp = pd.DataFrame({'atributo': FEATS, 'aumento_MAE_h': pi.importances_mean, 'desvio': pi.importances_std}).sort_values('aumento_MAE_h', ascending=False)

joblib.dump({'modelo': ajustados[melhor], 'nome': melhor, 'atributos': FEATS, 'categoricos': CAT, 'numericos': NUM},
            f'modelo_final.joblib')
res.to_pickle('resultados.pkl'); imp.to_pickle('importancia.pkl')
pd.DataFrame({'chave': te['chave'].values, 'Criado_dt': te['Criado_dt'].values, 'tipo_item': te['tipo_item'].values,
              'real_h': yte.values, **{k: v for k, v in previsoes.items()}}).to_pickle('previsoes_teste.pkl')
json.dump(dict(info, melhor=melhor, n_teste_maduras=int(maduras.sum())), open('treino_info.json', 'w'), ensure_ascii=False, indent=1)
print(res.drop(columns=['melhores_parametros']).round(3).to_string())
print(imp.round(2).to_string())
