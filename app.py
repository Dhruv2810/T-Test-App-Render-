from flask import Flask, request, jsonify, render_template
import numpy as np
from scipy import stats

app = Flask(__name__)

def one_sample_t_test(data, pop_mean, hypothesis):
    t_stat, p_val = stats.ttest_1samp(data, pop_mean, alternative=hypothesis)
    return {'t_statistic': float(t_stat), 'p_value': float(p_val)}

@app.route("/")
def home():
    return "T-Test API Running"

@app.route("/ttest", methods=["POST"])
def ttest():
    data = request.json["data"]
    mean = float(request.json["mean"])
    hypothesis = request.json["hypothesis"]

    result = one_sample_t_test(data, mean, hypothesis)

    return jsonify(result)

if __name__ == "__main__":
    app.run()
