import pandas as pd
from listing_7_5_fat_tail_scores import transform_fattail_columns, transform_skew_columns
from listing_8_4_rescore_metrics import score_current_data, group_current_data, reload_churn_data
from listing_10_4_dummy_variables import dummy_variables

def rescore_wcats(data_set_path,categories,groups):

    nocat_path = data_set_path.replace('.csv', '_nocat.csv')
    load_mat_df = reload_churn_data(nocat_path,'load_mat','6.4',is_customer_data=False)
    score_df = reload_churn_data(nocat_path,'score_params','7.5',is_customer_data=False)

    current_path = data_set_path.replace('.csv', '_current.csv')

    dummy_variables(current_path,groups, current=True)
    current_dummies = reload_churn_data(data_set_path,'current_dummies_groupscore','10.7',is_customer_data=True)
    align_dummies(current_dummies,data_set_path)

    current_nocat = reload_churn_data(data_set_path,'current_nocat','10.7',is_customer_data=True)
    assert set(score_df.index.values)==set(current_nocat.columns.values),"Data to re-score does not match transform params"
    assert set(load_mat_df.index.values)==set(current_nocat.columns.values),"Data to re-score does not match loading matrix"
    transform_skew_columns(current_nocat,score_df[score_df['skew_score']].index.values)
    transform_fattail_columns(current_nocat,score_df[score_df['fattail_score']].index.values)
    scaled_data = score_current_data(current_nocat,score_df,data_set_path)
    grouped_data = group_current_data(scaled_data, load_mat_df,data_set_path)

    groupscore_dummy_df = grouped_data.merge(current_dummies,left_index=True,right_index=True)
    groupscore_dummy_df.to_csv(data_set_path.replace('.csv','_current_groupscore.csv'),header=True)

    current_data_orig = reload_churn_data(data_set_path,'current','10.7',is_customer_data=True)
    save_segment_data_wcats(grouped_data,current_data_orig,load_mat_df,data_set_path, categories)


def align_dummies(current_data,data_set_path):
    new_dummies = set(pd.read_csv(data_set_path.replace('.csv','_current_dummies_groupmets.csv'),index_col=[0])['metrics'])
    old_dummies = set(pd.read_csv(data_set_path.replace('.csv','_dummies_groupmets.csv'),index_col=[0])['metrics'])

    missing_in_old = new_dummies.difference(old_dummies)
    missing_in_new = old_dummies.difference(new_dummies)
    for col in missing_in_new:
        current_data[col]=0.0
    for col in missing_in_old:
        current_data.drop(col,axis=1,inplace=True)


def save_segment_data_wcats(current_data_grouped, current_data, load_mat_df, data_set_path, categories):

    group_cols =  load_mat_df.columns[load_mat_df.astype(bool).sum(axis=0) > 1]
    no_group_cols = list(load_mat_df.columns[load_mat_df.astype(bool).sum(axis=0) == 1])
    no_group_cols.extend(categories)
    segment_df = current_data_grouped[group_cols].join(current_data[no_group_cols])
    segment_df.to_csv(data_set_path.replace('.csv','_current_groupmets_segment.csv'),header=True)