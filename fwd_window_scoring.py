
import pandas as pd
def scoreandrank(modelsmetrics, w_r2=0.35, w_rmse=0.2, w_precision=0.35, w_recall=0.1):
    
    metrics_df = pd.DataFrame.from_dict(
    modelsmetrics,
    orient='index',
    columns=['R2', 'RMSE', 'Precision', 'Recall', 'F1']
)


    # by = 'R2'
    # metrics_df_sorted = metrics_df.sort_values(by=by, ascending=False)
    # metrics_df_sorted = metrics_df_sorted.reset_index().rename(columns={'index': 'Forward_Window'})
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    # print('By {by}')
    # print(metrics_df_sorted)
    by='Precision'
    metrics_df_sorted = metrics_df.sort_values(by=by, ascending=False)
    metrics_df_sorted = metrics_df_sorted.reset_index().rename(columns={'index': 'Forward_Window'})
    print(f'By {by}')
    print(metrics_df_sorted)
    #model parameter / lookahead choosing
    #NEED NO false positives = NEED HI precision
    #want dece magnitude est = want high R^2 and Low RMSE
    #optional: dont want to miss winners = want hi recall
    # Higher is better overall score:
    # score = (
    #     w_r2 * normalized_r2
    #     - w_rmse * normalized_rmse   # lower RMSE is better, so subtract
    #     + w_precision * normalized_precision
    #     + w_recall * normalized_recall  # optional
    # )
    w_r2 = w_r2
    w_rmse = w_rmse
    w_precision = w_precision
    w_recall = w_recall
    #arb ish, see above. maybe inc precision wgt?
    def compute_model_composite_score(metrics_df, w_r2=0.35, w_rmse=0.2, w_precision=0.35, w_recall=0.1):
        df = metrics_df.copy()
        # Normalize metrics (0-1) using min-max scaling
        def normalize(col, higher_is_better=True):
            col_min, col_max = col.min(), col.max()
            if col_max == col_min:
                return [0.5] * len(col)
            if higher_is_better:
                return (col - col_min) / (col_max - col_min)
            else:
                return (col_max - col) / (col_max - col_min)

        df['norm_r2'] = normalize(df['R2'], higher_is_better=True)
        df['norm_rmse'] = normalize(df['RMSE'], higher_is_better=False) #NOTE!
        df['norm_precision'] = normalize(df['Precision'], higher_is_better=True)
        df['norm_recall'] = normalize(df['Recall'], higher_is_better=True)
        # Weighted score
        df['composite_score'] = (
            w_r2 * df['norm_r2'] +
            w_rmse * df['norm_rmse'] +
            w_precision * df['norm_precision'] +
            w_recall * df['norm_recall']
        )
        # Sort for convenience
        df_sorted = df.sort_values(by='composite_score', ascending=False).reset_index(drop=True)
        return df_sorted
    ranked_models_df = compute_model_composite_score(metrics_df_sorted)
    # print(ranked_models_df[['Forward_Window', 'R2', 'RMSE', 'Precision', 'Recall', 'composite_score']])
    #^og cmd in colab was display(...)
    # okay r_p5_td seems best
    return ranked_models_df[['Forward_Window', 'R2', 'RMSE', 'Precision', 'Recall', 'composite_score']]
