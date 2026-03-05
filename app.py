import numpy as np
from scipy import stats

def one_sample_t_test(data, pop_mean, hypothesis):
    # Perform 1-sample t-test
    # hypothesis arg maps to 'alternative': 'two-sided', 'less', 'greater'
    t_stat, p_val = stats.ttest_1samp(data, pop_mean, alternative=hypothesis)
   
    return {'t_statistic': t_stat, 'p_value': p_val}

# Test Data
data = [102, 98, 101, 105, 97, 99, 103]
pop_mean_h0 = 108

# H0: mu <= 108 means Ha: mu > 108 -> 'greater'
result = one_sample_t_test(data, pop_mean_h0, 'greater')

print(result)
