def MC_Call(S,K,T,r,sigma,n_sim=100000):
    import numpy as np
    # 난수 생성 (표준 정규분포)
    np.random.seed(11)
    Z = np.random.randn(n_sim)
    # 만기가격 도출
    ST = S * np.exp((r - 0.5 * sigma**2) * T\
                     + sigma * np.sqrt(T) * Z)
    # 콜옵션의 페이오프 계산
    payoff = np.maximum(ST - K, 0)
    # 현재가치 할인 적용 (할인율: e^(-rT))
    call_price = np.exp(-r * T) * np.mean(payoff)
    return call_price

def MC_Put(S,K,T,r,sigma,n_sim=100000):
    import numpy as np
    # 난수 생성 (표준 정규분포)
    np.random.seed(11)
    Z = np.random.randn(n_sim)
    # 만기가격 도출
    ST = S * np.exp((r - 0.5 * sigma**2) * T\
                     + sigma * np.sqrt(T) * Z)
    # 풋옵션의 페이오프 계산
    payoff = np.maximum(K-ST, 0)
    # 현재가치 할인 적용 (할인율: e^(-rT))
    put_price = np.exp(-r * T) * np.mean(payoff)
    return put_price

def MC_Greeks(fun, S, K, T, r, sigma):
    # MC_Greeks(MC_Put, 100, 100, 1, 0.05, 0.3)
    # Delta (Δ)
    eps=S*sigma*0.01
    C_plus = fun(S + eps, K, T, r, sigma)
    C_minus = fun(S - eps, K, T, r, sigma)
    Delta = (C_plus - C_minus) / (2 * eps)
    # Gamma (Γ)
    C_0 = fun(S, K, T, r, sigma)
    Gamma = (C_plus - 2 * C_0 + C_minus) / (eps ** 2)
    # Vega (V)
    eps=sigma*0.01
    C_sigma_plus = fun(S, K, T, r, sigma + eps)
    C_sigma_minus = fun(S, K, T, r, sigma - eps)
    Vega = (C_sigma_plus - C_sigma_minus) / (2 * eps)
    Vega = 0.01*Vega # 1% 베가로 변환
    # 1day Theta (Θ)
    eps=0.01
    C_t = fun(S, K, T - eps, r, sigma)
    Theta = (1/365)*(C_t - C_0) / eps
    # 1bp Rho (ρ)
    C_r_plus = fun(S, K, T, r + eps, sigma)
    C_r_minus = fun(S, K, T, r - eps, sigma)
    Rho = 0.0001* (C_r_plus - C_r_minus) / (2 * eps)
    return {
        "Price": C_0,
        "Delta (Δ)": Delta,
        "Gamma (Γ)": Gamma,
        "Theta (Θ)": Theta,
        "Vega (V)": Vega,
        "Rho (ρ)": Rho,
    }

