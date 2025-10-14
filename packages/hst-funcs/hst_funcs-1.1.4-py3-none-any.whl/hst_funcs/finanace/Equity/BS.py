from math import log, sqrt, pi, exp
from scipy.stats import norm
import numpy as np

def d1(S, K, T, r, sigma):
    return (log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt(T))

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * sqrt(T)

def bs_call(S, K, T, r, sigma):
    return S * norm.cdf(d1(S, K, T, r, sigma)) - K * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))

def call_delta(S, K, T, r, sigma):
    return norm.cdf(d1(S, K, T, r, sigma))

def call_gamma(S, K, T, r, sigma):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * sqrt(T))

def call_vega(S, K, T, r, sigma): # 1% 변동성 민감도
    return 0.01 * (S * norm.pdf(d1(S, K, T, r, sigma)) * sqrt(T))

def call_theta(S, K, T, r, sigma): # 1 day 감소에 대한 민감도
    return (1/365) * (- (S * norm.pdf(d1(S, K, T, r, sigma)) * sigma) / (2 * sqrt(T)) \
                   - r * K * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma)))

def call_rho(S, K, T, r, sigma): # 1bp 변화에 대한 민감도
    return 0.0001 * ((K * T * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))))

def bs_put(S, K, T, r, sigma):
    return K * exp(-r * T) - S + bs_call(S, K, T, r, sigma)

def put_delta(S, K, T, r, sigma):
    return -norm.cdf(-d1(S, K, T, r, sigma))

def put_gamma(S, K, T, r, sigma):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * sqrt(T))

def put_vega(S, K, T, r, sigma): # 1% 변동성 민감도
    return 0.01 * (S * norm.pdf(d1(S, K, T, r, sigma)) * sqrt(T))

def put_theta(S, K, T, r, sigma):  # 1 day 감소에 대한 민감도
    return (1/365) * (
        - (S * norm.pdf(d1(S, K, T, r, sigma)) * sigma) / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma)))



def put_rho(S, K, T, r, sigma):
    return -0.0001 * (K * T * exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma)))