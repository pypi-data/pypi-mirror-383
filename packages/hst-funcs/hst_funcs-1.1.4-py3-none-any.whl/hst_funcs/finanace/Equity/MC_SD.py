def SD_lstar_CPU(S, kijun, K, T, c, r, q, sigma, barrier, dummy, sim):
    import numpy as np
    from scipy.stats import norm
    
    """
    ELS (Equity-Linked Securities) 조기상환 및 만기상환 시뮬레이션
    
    Parameters:
    - S: 초기 주가
    - kijun: 기준 가격
    - K: 행사가격
    - T: 옵션 만기 (일 단위)
    - c: 조기상환 행사가 (0.01 이상)
    - r: 무위험 이자율
    - q: 배당률
    - sigma: 변동성
    - barrier: 배리어 (예: 65% 미만일 경우 지급)
    - dummy: 배리어 이벤트 여부 (0 또는 1)
    - sim: 시뮬레이션 횟수
    
    Returns:
    - mu: 최종 가격의 정규분포 적합 결과 (평균, 표준편차)
    """

 
    
    # 주가 경로 생성
    N=T[-1] # 만기까지의 날짜수
    np.random.seed(111)
    W = np.random.randn(N,sim)  # 표준 정규분포 난수

    # log(S) 행렬 만들기
    lnS=(r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * W

    # 앞에 붙이기
    lnS = np.insert(lnS,0,np.log(S), axis=0)
    # 누적합 구하기
    S=np.exp(np.cumsum(lnS,axis=0))

     # 수익률 행렬 변환
    R = S / kijun

    Price = np.zeros(sim)  # 최종 옵션 가격 배열

    EN=len(K) # 조기상환 회차수 
    for i in range(EN):
        out = np.where((Price == 0) & (R[T[i], :] >= K[i]))  # 아직 상환되지 않은 경우만 선택
        # 조기상환된 경우 가격 업데이트
        Price[out] = 10000 * (1 + c[i]) * np.exp(-r * (T[i]) / 365)
   
    # 만기상환 테스트
    check = np.where(Price == 0) # 아직 상환되지 않은 경우의 인덱스 추출

    # 만기 손실 체크 
    for idx in check:
        if np.min(R[:,idx]) < barrier: # 해당 sim 회차의 최소값이 배리어 미만이면?
            # 배리어 하외 하면 R값으로 리턴
            Price[idx] = 10000 * (R[-1, idx]) * np.exp(-r * T[-1]/365)
        else: # 배리어를 한번도 친적이 없으면 마지막 쿠폰 지급
            Price[idx] = 10000 * (1 + dummy) * np.exp(-r * T[-1]/365)
    
    # 정규분포 적합
    mu, s = norm.fit(Price)

    return mu

def SD_lstar_GPU(S, kijun, K, T, c, r, q, sigma, barrier, dummy, sim):
    import cupy as cp
    from scipy.stats import norm  # 정규분포 적합은 여전히 CPU에서 수행

    """
    ELS (Equity-Linked Securities) 조기상환 및 만기상환 시뮬레이션 (GPU 버전)
    """

    N = T[-1]  # 전체 만기까지의 날짜 수
    dt = 1 / 365  # 하루 단위
    cp.random.seed(111)
    W = cp.random.randn(N, sim)  # 표준 정규분포 난수 생성

    # 로그 수익률 경로 생성
    lnS = (r - 0.5 * sigma**2) * dt + sigma * cp.sqrt(dt) * W

    # 시작값 log(S)를 앞에 추가
    lnS = cp.concatenate([cp.full((1, sim), cp.log(S)), lnS], axis=0)

    # 누적합 후 지수화하여 주가 경로 생성
    S_path = cp.exp(cp.cumsum(lnS, axis=0))

    # 수익률 행렬 계산
    R = S_path / kijun

    # 초기 옵션 가격 배열
    Price = cp.zeros(sim)

    EN = len(K)
    for i in range(EN):
        cond = (Price == 0) & (R[T[i], :] >= K[i])
        Price = cp.where(cond, 10000 * (1 + c[i]) * cp.exp(-r * T[i] / 365), Price)

    # 아직 상환되지 않은 시뮬레이션 찾기
    check = (Price == 0)

    # 배리어 하회 여부 확인
    min_R = cp.min(R, axis=0)
    barrier_hit = (min_R < barrier) & check
    no_barrier_hit = ~barrier_hit & check

    # 배리어 하회한 경우
    Price = cp.where(barrier_hit, 10000 * R[-1, :] * cp.exp(-r * T[-1] / 365), Price)

    # 배리어를 한 번도 안 맞은 경우
    Price = cp.where(no_barrier_hit, 10000 * (1 + dummy) * cp.exp(-r * T[-1] / 365), Price)

    # GPU에서 CPU로 데이터 이동하여 정규분포 적합
    Price_cpu = cp.asnumpy(Price)
    mu, s = norm.fit(Price_cpu)

    return mu

def MC_Greeks_SD1(fun, S, kijun, K, T, c, r, q, sigma, barrier, dummy, sim):
    # Delta (Δ)
    eps=S*sigma*0.01
    C_plus = fun(S + eps, kijun, K, T, c, r, q, sigma, barrier, dummy, sim)
    C_minus = fun(S - eps, kijun, K, T, c, r, q, sigma, barrier, dummy, sim)
    Delta = (C_plus - C_minus) / (2 * eps)
    # Gamma (Γ)
    C_0 = fun(S,kijun, K, T, c, r, q, sigma, barrier, dummy, sim)
    Gamma = (C_plus - 2 * C_0 + C_minus) / (eps ** 2)
    # Vega (V)
    eps=sigma*0.01
    C_sigma_plus = fun(S, kijun, K, T, c, r, q, sigma+eps, barrier, dummy, sim)
    C_sigma_minus = fun(S, kijun, K, T, c, r, q, sigma-eps, barrier, dummy, sim)
    Vega = (C_sigma_plus - C_sigma_minus) / (2 * eps)
    Vega = 0.01*Vega # 1% 베가로 변환
    # 1day Theta (Θ)
    eps=1 # T가 날짜 수임으로 수정
    C_t = fun(S, kijun, K, T-eps, c, r, q, sigma, barrier, dummy, sim)
    Theta = (C_t - C_0) # 날짜가 하루 줄어든 것이므로 그대로 
    # 1bp Rho (ρ)
    C_r_plus = fun(S, kijun, K, T, c, r+eps, q, sigma+eps, barrier, dummy, sim)
    C_r_minus = fun(S, kijun, K, T, c, r-eps, q, sigma+eps, barrier, dummy, sim)
    Rho = 0.0001* (C_r_plus - C_r_minus) / (2 * eps)
    return {
        "Price": C_0,
        "Delta (Δ)": Delta,
        "Gamma (Γ)": Gamma,
        "Theta (Θ)": Theta,
        "Vega (V)": Vega,
        "Rho (ρ)": Rho,
    }
