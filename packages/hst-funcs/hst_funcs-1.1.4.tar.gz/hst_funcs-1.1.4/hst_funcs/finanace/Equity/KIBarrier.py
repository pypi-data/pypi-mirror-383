def UpInCallRebate(S,K, r,sig,T,Barrier,rebate,sim):
    # S: 현재가
    # K: 행사가격
    # T: 만기(in years)
    # r: 이자율 (연 1%면 0.01로)
    # sig: 연변동성 (30%라면 0.3으로)
    # Barrier: 배리어 level
    # rebate: Barrier를 치지 못했을 때 주는 금액

    import cupy as cp
    from scipy.stats import norm
    import matplotlib.pyplot as plt
    # 랜덤 시드 설정
    cp.random.seed(77)
    N_intervals=352 # 1년을 352로 세팅
    N = int(T * N_intervals)  # 만기를 감안한 시간간격의 갯수
    dt=T/N # 시간간격
    s = cp.sqrt(1 / N_intervals)  # 분산을 표준편차화

    # N(0,s)을 따르는 [N, sim] 크기의 정규난수 생성
    dW = cp.random.normal(0, s, size=(N, sim))
    pars=(r-0.5*sig*sig)*dt+sig*dW
    exp_pars=cp.exp(pars)

    # 추가할 행 생성
    S0 = S*cp.ones((1, dW.shape[1]), dtype=dW.dtype)
    W = cp.vstack([S0, exp_pars]) # (N+1,sim)의 행렬로 만든다.

    # 시간에 따른 주가행렬 완성
    S=cp.cumprod(W,axis=0) # 행으로 계속 누적곱셈으로 행렬 생성

    ################## 옵션 payoff##################
    # 칼럼별로 배리어를 넘어선 주가가 있는지 확인한다.
    max_values = cp.max(S, axis=0) # 열에서의 최대값을 구함
    # Barrier 보다 작은 경우의 인덱스 찾기
    # 끝에 0은 인덱스를 추출하기 위함
    indices = cp.where(max_values >= Barrier)[0]
    # 모든 값에 rebate 설정하고 현가화
    option = cp.exp(-r*T)*rebate*cp.ones(sim)

    # Barrier를 터지하지 않은 경우, European call 적용
    option[indices]=cp.exp(-r*T)*cp.maximum(S[-1,indices]-K,0) # 콜옵션
    price=cp.mean(option)
    return price

def UpInCallRebate_GreeksGreeks(S,K, r,sig,T,Barrier,rebate,sim):
    dp=S*0.01
    P0=UpInCallRebate(S,K, r,sig,T,Barrier,rebate,sim)
    Pup=UpInCallRebate(S+dp,K, r,sig,T,Barrier,rebate,sim)
    Pdn=UpInCallRebate(S-dp,K, r,sig,T,Barrier,rebate,sim)
    delta= (Pup-Pdn)/(2*dp)
    gamma=(Pup-2*P0+Pdn)/(dp*dp)
    Pv=UpInCallRebate(S,K, r,sig+0.01,T,Barrier,rebate,sim)
    vega=Pv-P0
    Pr=UpInCallRebate(S,K, r+0.0001,sig,T,Barrier,rebate,sim)
    rho=Pr-P0
    Pt=UpInCallRebate(S,K, r,sig,T-1/365,Barrier,rebate,sim)
    theta=Pt-P0
    print('가격:',P0)
    print('델타:',delta)
    print('감마:',gamma)
    print('1% 베가:',vega)
    print('1bp 르호:',rho)
    print('1Day 세타:',theta)
