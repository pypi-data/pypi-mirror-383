############################################################################
###########################################################################
# 20240720 수정: worstoff analysis 추가
# 20240729: get_close_price(), vol_corr() 수정
# uname2yahoo()에서 기초자산 추가
# 20241106: yfinance.download() 수행시 Colab의 UTC 타임존 문제로 pptout_colab() 함수 추가
# 20241107: resample('ME')로 수정, bfill(),ffill()로 수정, df_daily_stats_05.rename() 관련 warning 수정, LLY, ARM 기초자산 2개 추가
############################################################################

def kr_codes_for_alives(df_Daily_NAV,date0):
    import pandas as pd
    kr_cols= df_Daily_NAV.loc[date0].filter(regex=r'^KR')
    # 해당 칼럼에서 값이 0이 아닌 칼럼을 추출
    DD = kr_cols[kr_cols != 0] # 살아있는 넘들의 NAV
    if not DD.empty:
      return DD.index
    else:
      return None



def underlyings_for_ELS(file):
    # 20240720: 리턴개수 수정

    # 모든 발행 ELS의 기초자산 분석
    import pandas as pd
    import numpy as np

    df=pd.read_excel(file,skiprows=7,usecols=None)
    KR_Code=df.iloc[0,2:] # 발행코드 정보를 읽어옴
    # 특정행만 추출
    selected_rows = df.iloc[[5] + list(range(17, 21))]

    # 새로운 데이터프레임으로 저장
    UA_df = selected_rows.iloc[:,2:].copy()
    UA_df.columns=KR_Code
    UA_df.columns.name='KR code'

    # 기초자산 개수 구하기
    nan_counts = UA_df.iloc[1:5].notna().sum()
    # 새로운 행에 NaN이 아닌 값의 개수를 추가
    nan_counts_df = pd.DataFrame([nan_counts], index=['기초자산갯수'])

    # 기존 데이터프레임에 새로운 행 추가
    UA_df = pd.concat([UA_df.iloc[:5], nan_counts_df])
    UA_df.index=['발행금액','기초자산1','기초자산2','기초자산3','기초자산4','기초자산갯수']

    # '발행금액' 행을 numeric으로 변환
    UA_df.loc['발행금액'] = pd.to_numeric(UA_df.loc['발행금액'], errors='coerce')

    # 첫 번째 행의 값 / 마지막 행의 값 계산
    first_row = UA_df.iloc[0]
    last_row = UA_df.iloc[-1]
    values = first_row / last_row

    # UA_df의 2행부터 5행까지의 값 추출하여 1차원 배열로 변환
    unique_assets = pd.unique(UA_df.iloc[1:5].values.ravel('K'))

    # NaN 값을 제거하여 고유한 값만 남김
    unique_assets = unique_assets[~pd.isna(unique_assets)]

    df_ua = pd.DataFrame(index=unique_assets, columns=UA_df.columns)

    # 각 칼럼의 값 설정
    for col in UA_df.columns:
        for asset in unique_assets:
            if asset not in UA_df[col].values:
                df_ua.loc[asset, col] = 0
            else:
                df_ua.loc[asset, col] = values[col]
    # 종목수 게산하기

    total_code_num=len(KR_Code) # total

    # 각 행에서 0이 아닌 값의 개수를 세고, 이들의 합을 구함
    non_zero_counts = (df_ua != 0).sum(axis=1)  # 각 행에서 0이 아닌 값의 개수
    non_zero_counts_ratio=non_zero_counts/total_code_num
    non_zero_sums = df_ua[df_ua != 0].sum(axis=1)/1e+9  # 각 행에서 0이 아닌 값의 합
    total_issued_sum=np.sum(non_zero_sums)
    non_zero_sums_ratio=non_zero_sums/total_issued_sum

    df_ua_summary=pd.DataFrame(data={'종목수':non_zero_counts,'총 종목수 대비 비율':non_zero_counts_ratio,
                                     '발행총액(10억)':non_zero_sums,'총 발행총액 대비 비율':non_zero_sums_ratio})
    # '종목수' 칼럼을 큰 순서로 정렬하고 상위 19개 행을 출력
    top_19 = df_ua_summary.sort_values(by='종목수', ascending=False).head(19)

    # 상위 19개행을 제거한 데이터프레임
    other_df = df_ua_summary.drop(top_19.index)
    sum_row=other_df.sum()
    # 19개행과 기타행의 합으로 재구성
    top_19.loc['기타'] = sum_row
    df_ua_summary_out=top_19
    return df_ua,df_ua_summary_out


def underlyings_for_ELS_alives(df_ua,df_Daily_NAV,Biz_Dates):
    # 20240720: 리턴개수 수정
    import numpy as np
    import pandas as pd

    alived_codes=kr_codes_for_alives(df_Daily_NAV,Biz_Dates.iloc[-1])
    # 살아있는 칼럼들만 추출하여 새로운 데이터프레임 생성
    df_ua_alives = df_ua[alived_codes]
    # 종목수 게산하기
    total_code_num=len(alived_codes)

    # 각 행에서 0이 아닌 값의 개수를 세고, 이들의 합을 구함
    non_zero_counts = (df_ua_alives != 0).sum(axis=1)  # 각 행에서 0이 아닌 값의 개수
    non_zero_counts_ratio=non_zero_counts/total_code_num
    non_zero_sums = df_ua_alives[df_ua_alives != 0].sum(axis=1)/1e+9  # 각 행에서 0이 아닌 값의 합
    total_issued_sum=np.sum(non_zero_sums)
    non_zero_sums_ratio=non_zero_sums/total_issued_sum

    df_ua_alives_summary=pd.DataFrame(data={'종목수':non_zero_counts,'총 종목수 대비 비율':non_zero_counts_ratio,
                                     '발행총액(10억)':non_zero_sums,'총 발행총액 대비 비율':non_zero_sums_ratio})
    # '종목수' 칼럼을 큰 순서로 정렬하고 상위 19개 행을 출력
    top_19_alives = df_ua_alives_summary.sort_values(by='종목수', ascending=False).head(19)
    # 상위 19개행을 제거한 데이터프레임
    other_alives_df = df_ua_alives_summary.drop(top_19_alives.index)
    sum_row=other_alives_df.sum()
    # 19개행과 기타행의 합으로 재구성
    top_19_alives.loc['기타'] = sum_row
    df_ua_alives_summary_out=top_19_alives
    return df_ua_alives,df_ua_alives_summary_out,alived_codes



def remove_consecutive_zeros(df):
    import pandas as pd
    # 첫 번째 행이 모두 0인 경우 삭제
    if (df.iloc[0] == 0).all():
        df.drop(df.index[0], inplace=True)
        # 재귀적으로 함수 호출하여 다음 첫 번째 행이 모두 0인 경우도 확인하고 삭제
        remove_consecutive_zeros(df)


def stats_for_alives(df_Daily_NAV,date0):
    import pandas as pd
    kr_cols= df_Daily_NAV.loc[date0].filter(regex=r'^KR')
    # 해당 칼럼에서 값이 0이 아닌 칼럼을 추출
    DD = kr_cols[kr_cols != 0] # 살아있는 넘들의 NAV
    if not DD.empty:
      Ret = (DD-10000)/100 # 리턴값(100% 환산값)
      Ret = Ret.astype('float64')
      # Ret_D 시리즈에서 최소값과 최대값에 해당하는 인덱스 찾기
      min_Ret_index = Ret.idxmin()
      max_Ret_index = Ret.idxmax()
      return Ret.describe(),min_Ret_index,max_Ret_index

    else:
      return None,None,None


def pa_return_for_alives(df_Daily_NAV,final_date):
  # 2024년 7월16일 duration zero 에러 수정
  # 2024년 7월26일 NAV 칼럼이름수정
    import pandas as pd
    kr_cols= df_Daily_NAV.loc[final_date].filter(regex=r'^KR')
    # 해당 칼럼에서 값이 0이 아닌 칼럼을 추출
    DD = kr_cols[kr_cols != 0] # 살아있는 넘들의 NAV
    df_alives=pd.DataFrame(DD)
    df_alives.rename(columns={},inplace=True) # 칼럼이름 지우기
    df_alives.columns=['NAV'] # 이름 새로 짓기

    for code in df_alives.index:
      first_date = df_Daily_NAV[code][df_Daily_NAV[code] != 0].first_valid_index()
      duration = (pd.to_datetime(final_date) - first_date).days
      df_alives.at[code,'발행일']=first_date
      df_alives.at[code,'Duration']=duration
      Ret= (df_alives.at[code,'NAV']-10000)/10000
      if duration==0:
        Ret_pa=None
      else:
        Ret_pa=(1+Ret)**(365/duration)-1
      df_alives.at[code,'절대수익율']=Ret
      df_alives.at[code,'연환산수익율']=Ret_pa

    return df_alives


def stats_for_redeemed(df_Daily_NAV,input_date):
    import pandas as pd

    # date가 인덱스에 있는지 확인
    if input_date not in df_Daily_NAV.index: # 인덱스에 없는 날짜라면
        input_date=df_Daily_NAV.index[df_Daily_NAV.index < input_date].max() # 가장 가까운 앞 날짜 추출
    else: # 인덱스에 있다면 그냥 날짜객체로 반환
        input_date=pd.Timestamp(input_date)

    # 특정일을 나타내는 행에서 그 값이 0인 것들중 칼럼 이름이 KR로 시작하는 것들을 Series로 추출함
    zeros=df_Daily_NAV.loc[input_date][df_Daily_NAV.loc[input_date] == 0].filter(regex='^KR')

    # 빈 데이터프레임 생성
    df_redeemed = pd.DataFrame(columns=zeros.index)

    for col in zeros.index:
        non_zero_values = df_Daily_NAV.loc[df_Daily_NAV[col] != 0, col]
        last_non_zero_index = non_zero_values.index[-1]
        # 만일 최종일의 날짜가 입력값보다 크면 상환된 종목이 아님을 의미한다.
        # 추가로 len(non_zero_values)이 0이어도 대상이 아니다.
        if (last_non_zero_index > input_date) or (len(non_zero_values)==0):
            df_redeemed.drop(columns=[col],inplace=True) # 해당 코드 삭제
            continue # 다음 칼럼으로 이동

        first_non_zero_index = non_zero_values.index[0]
        first_non_zero_value = 10000 # 10000으로 통일
        last_non_zero_value = non_zero_values.iloc[-1]
        duration = (last_non_zero_index - first_non_zero_index).days
        Ret_abs=last_non_zero_value/first_non_zero_value-1
        Ret_pa=(1+Ret_abs)**(365/duration)-1
        df_redeemed[df_redeemed.columns[df_redeemed.columns.get_loc(col)]] =\
        [first_non_zero_value, last_non_zero_value, duration, Ret_abs, Ret_pa]

    if not df_redeemed.empty:
        ret_abs=df_redeemed.iloc[3] # abs return의 정보
        ret_abs=pd.Series(ret_abs)

        ret_pa=df_redeemed.iloc[4] # per annum return의 정보
        ret_pa=pd.Series(ret_pa)

        durations=df_redeemed.iloc[2]
        durations=pd.Series(durations)

        # 양수와 음수의 경우를 따로 집계
        pos_ret_abs = ret_abs[ret_abs > 0]
        neg_ret_abs = ret_abs[ret_abs < 0]

        pos_ret_pa = ret_pa[ret_pa > 0]
        neg_ret_pa = ret_pa[ret_pa < 0]

        # durations 시리즈에서 최솟값과 최댓값에 해당하는 인덱스 찾기
        min_duration_index = durations.idxmin()
        max_duration_index = durations.idxmax()

        # ret_pa 시리즈에서 최솟값과 최댓값에 해당하는 인덱스 찾기
        min_ret_pa_index = ret_pa.idxmin()
        max_ret_pa_index = ret_pa.idxmax()

    else: # df_redeemed가 비어있다면 아무것도 출력하지 않음
        return None,None,None, None, None,None,None,None,None,None,None

    return (durations.describe()[['count', 'mean', 'std','50%']],
            ret_abs.describe()[['mean', 'std','50%']],
            ret_pa.describe()[['mean', 'std','50%']],
            pos_ret_abs.describe()[['count','mean', 'std']],
            neg_ret_abs.describe()[['count','mean', 'std']],
            pos_ret_pa.describe()[['count','mean', 'std']],
            neg_ret_pa.describe()[['count','mean', 'std']],
            min_duration_index,
            max_duration_index,
            min_ret_pa_index,
            max_ret_pa_index)

# 함수 작성
def stats_for_redeemed_old(df_Daily_NAV,input_date):
    import pandas as pd
    # date가 인덱스에 있는지 확인
    if input_date not in df_Daily_NAV.index: # 인덱스에 없는 날짜라면
        input_date=df_Daily_NAV.index[df_Daily_NAV.index < input_date].max() # 가장 가까운 앞 날짜 추출
    else: # 인덱스에 있다면 그냥 날짜객체로 반환
        input_date=pd.Timestamp(input_date)

    # 특정일을 나타내는 행에서 그 값이 0인 것들중 칼럼 이름이 KR로 시작하는 것들을 Series로 추출함
    zeros=df_Daily_NAV.loc[input_date][df_Daily_NAV.loc[input_date] == 0].filter(regex='^KR')

    # 빈 데이터프레임 생성
    df_redeemed = pd.DataFrame(columns=zeros.index)

    for col in zeros.index:
        non_zero_values = df_Daily_NAV.loc[df_Daily_NAV[col] != 0, col]
        last_non_zero_index = non_zero_values.index[-1]
        # 만일 최종일의 날짜가 입력값보다 크면 상환된 종목이 아님을 의미한다.
        # 추가로 len(non_zero_values)이 0이어도 대상이 아니다.
        if (last_non_zero_index > input_date) or (len(non_zero_values)==0):
            df_redeemed.drop(columns=[col],inplace=True) # 해당 코드 삭제
            continue # 다음 칼럼으로 이동

        first_non_zero_index = non_zero_values.index[0]
        first_non_zero_value = 10000 # 10000으로 통일
        last_non_zero_value = non_zero_values.iloc[-1]
        duration = (last_non_zero_index - first_non_zero_index).days
        Ret_abs=last_non_zero_value/first_non_zero_value-1
        Ret_pa=(1+Ret_abs)**(365/duration)-1
        df_redeemed[df_redeemed.columns[df_redeemed.columns.get_loc(col)]] =\
        [first_non_zero_value, last_non_zero_value, duration, Ret_abs, Ret_pa]

    if not df_redeemed.empty:
        ret_abs=df_redeemed.iloc[3] # abs return의 정보
        ret_abs=pd.Series(ret_abs)

        ret_pa=df_redeemed.iloc[4] # per annum return의 정보
        ret_pa=pd.Series(ret_pa)

        durations=df_redeemed.iloc[2]
        durations=pd.Series(durations)

        # 양수와 음수의 경우를 따로 집계
        pos_ret_abs = ret_abs[ret_abs > 0]
        neg_ret_abs = ret_abs[ret_abs < 0]

        pos_ret_pa = ret_pa[ret_pa > 0]
        neg_ret_pa = ret_pa[ret_pa < 0]

        # durations 시리즈에서 최솟값과 최댓값에 해당하는 인덱스 찾기
        min_duration_index = durations.idxmin()
        max_duration_index = durations.idxmax()

        # ret_abs 시리즈에서 최솟값과 최댓값에 해당하는 인덱스 찾기
        min_ret_abs_index = ret_abs.idxmin()
        max_ret_abs_index = ret_abs.idxmax()

    else: # df_redeemed가 비어있다면 아무것도 출력하지 않음
        return None,None,None, None, None,None,None,None,None,None,None

    return (durations.describe()[['count', 'mean', 'std','50%']],
            ret_abs.describe()[['mean', 'std','50%']],
            ret_pa.describe()[['mean', 'std','50%']],
            pos_ret_abs.describe()[['count','mean', 'std']],
            neg_ret_abs.describe()[['count','mean', 'std']],
            pos_ret_pa.describe()[['count','mean', 'std']],
            neg_ret_pa.describe()[['count','mean', 'std']],
            min_duration_index,
            max_duration_index,
            min_ret_abs_index,
            max_ret_abs_index)


def hist_for_redeemded(df_Daily_NAV,input_date):
  import matplotlib.pyplot as plt
  import pandas as pd

  # date가 인덱스에 있는지 확인
  if input_date not in df_Daily_NAV.index: # 인덱스에 없는 날짜라면
      input_date=df_Daily_NAV.index[df_Daily_NAV.index < input_date].max() # 가장 가까운 앞 날짜 추출
  else: # 인덱스에 있다면 그냥 날짜객체로 반환
      input_date=pd.Timestamp(input_date)

  # 특정일을 나타내는 행에서 그 값이 0인 것들중 칼럼 이름이 KR로 시작하는 것들을 Series로 추출함
  zeros=df_Daily_NAV.loc[input_date][df_Daily_NAV.loc[input_date] == 0].filter(regex='^KR')

  # 빈 데이터프레임 생성
  df_redeemed = pd.DataFrame(columns=zeros.index)

  for col in zeros.index:
      non_zero_values = df_Daily_NAV.loc[df_Daily_NAV[col] != 0, col]
      last_non_zero_index = non_zero_values.index[-1]
      # 만일 최종일의 날짜가 입력값보다 크면 상환된 종목이 아님을 의미한다.
      # 추가로 len(non_zero_values)이 0이어도 대상이 아니다.
      if (last_non_zero_index > input_date) or (len(non_zero_values)==0):
          df_redeemed.drop(columns=[col],inplace=True) # 해당 코드 삭제
          continue # 다음 칼럼으로 이동

      first_non_zero_index = non_zero_values.index[0]
      first_non_zero_value = 10000 # 10000으로 통일
      last_non_zero_value = non_zero_values.iloc[-1]
      duration = (last_non_zero_index - first_non_zero_index).days
      Ret_abs=last_non_zero_value/first_non_zero_value-1
      Ret_pa=(1+Ret_abs)**(365/duration)-1
      df_redeemed[df_redeemed.columns[df_redeemed.columns.get_loc(col)]] =\
      [first_non_zero_value, last_non_zero_value, duration, Ret_abs, Ret_pa]

  ror_for_redeemed=df_redeemed.iloc[4,:]
  ror_for_redeemed.name='p.a.return'

  return ror_for_redeemed


def get_issue_amount(df, date):
    import pandas as pd
    # date가 문자열이라면 datetime 객체로 변환
    if isinstance(date, str):
        date = pd.to_datetime(date)
    # date가 datetime 객체가 아니라면 에러 메시지 출력
    elif not isinstance(date, pd.Timestamp):
        print("Error: 입력된 날짜가 올바르지 않습니다.")
        return None

    # 입력된 날짜 이전 또는 같은 발행일을 가진 행의 인덱스 가져오기
    idx = df[df['발행일'] <= date].index.tolist()

    # 발행금액 합계 초기화
    total_amount = 0
    total_sum = 0

    # 발행금액 합계와 계수 계산
    for i in idx:
        total_amount += df.at[i, '발행총액']
        total_sum += 1
    return total_sum,total_amount

def info_for_redeemed(df,df_issued_summary,input_date):
    import pandas as pd
    # date가 인덱스에 있는지 확인
    if input_date not in df.index: # 인덱스에 없는 날짜라면
        input_date=df.index[df.index < input_date].max() # 가장 가까운 앞 날짜 추출
    else: # 인덱스에 있다면 그냥 날짜객체로 반환
        input_date=pd.Timestamp(input_date)
    # 특정일을 나타내는 행에서 그 값이 0인 것들중 칼럼 이름이 KR로 시작하는 것들을 Series로 추출함
    zeros=df.loc[input_date][df.loc[input_date] == 0].filter(regex='^KR')

    # 빈 데이터프레임 생성
    df_redeemed = pd.DataFrame(columns=zeros.index)

    redeemed_amount=0
    redeemed_num=0

    for col in zeros.index:
        non_zero_values = df.loc[df[col] != 0, col]
        last_non_zero_index = non_zero_values.index[-1]
        # 만일 최종일의 날짜가 입력값보다 크면 상환된 종목이 아님을 의미한다.
        # 추가로 len(non_zero_values)이 0이어도 대상이 아니다.
        if (last_non_zero_index > input_date) or (len(non_zero_values)==0):
            df_redeemed.drop(columns=[col],inplace=True) # 해당 코드 삭제
            continue # 다음 칼럼으로 이동
        redeemed_amount += df_issued_summary.at[col,'발행총액'] # 해당 종목의 발행총액을 더해줌
        redeemed_num += 1

    return redeemed_num,redeemed_amount/1e+9

def sharpe_ratio_for_redeemed(df,rf, input_date):
    import pandas as pd
    import numpy as np
    # date가 인덱스에 있는지 확인
    if input_date not in df.index: # 인덱스에 없는 날짜라면
        input_date=df.index[df.index < input_date].max() # 가장 가까운 앞 날짜 추출
    else: # 인덱스에 있다면 그냥 날짜객체로 반환
        input_date=pd.Timestamp(input_date)

    # 특정일을 나타내는 행에서 그 값이 0인 것들중 칼럼 이름이 KR로 시작하는 것들을 Series로 추출함
    zeros=df.loc[input_date][df.loc[input_date] == 0].filter(regex='^KR')

    # 빈 데이터프레임 생성
    Sharpe_redeemed = pd.Series(index=zeros.index)

    for col in zeros.index:
        non_zero_values = df.loc[df[col] != 0, col]
        last_non_zero_index = non_zero_values.index[-1]
        # 만일 최종일의 날짜가 입력값보다 크면 상환된 종목이 아님을 의미한다.
        # 추가로 len(non_zero_values)이 0이어도 대상이 아니다.
        if (last_non_zero_index > input_date) or (len(non_zero_values)==0):
            Sharpe_redeemed.drop(index=col,inplace=True) # 해당 코드 삭제
            continue # 다음 칼럼으로 이동
        # 로그 수익률 계산
        log_returns = np.log(non_zero_values / non_zero_values.shift(1))

        # 연간 로그 수익률의 평균과 표준편차 계산
        annual_mean_log_return = log_returns.mean() * 252  # 252는 주식 거래일 수
        annual_std_log_return = log_returns.std() * np.sqrt(252)  # 연간 표준편차 계산

        # sharpe ratio 계산
        sr=(annual_mean_log_return-rf)/annual_std_log_return
        Sharpe_redeemed[col] = sr

    return Sharpe_redeemed

# ticker로 종가 가져오는 함수 만들기
def get_close_price(ticker_tuple,date):
 # 20250206. timedelta를 5일에서 10일로 변경
  ticker, market = ticker_tuple
  # 20240727 새 함수 작성
  import yfinance as yf
  import pykrx.stock as krx
  import pandas as pd
  from datetime import datetime, timedelta
  import numpy as np

  original_date = datetime.strptime(date, '%Y-%m-%d')

  # 5일전 데이터부터 가져오기
  new_date = original_date - timedelta(days=10)

  # 새로운 날짜를 문자열로 변환
  prev_date = new_date.strftime('%Y-%m-%d')

  if market=='yahoo':
     # Yahoo Finance에서 데이터 가져오기
      try:
          stock = yf.Ticker(ticker)
          data = stock.history(start=prev_date, end=date)
          try:
              # 특정 날짜의 데이터를 가져오려고 시도
              close_price = data.loc[date]['Close']
              return close_price
          except KeyError:
              recent_data = data[data.index < date]
              most_recent_data = recent_data.iloc[-1]
              new_price = most_recent_data['Close']
              return new_price
      except KeyError: # 2024년 7월26일 수정
        print('현재가가 없는 종목입니다.')
        return np.nan
      except Exception as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return np.nan
  elif market=='krx':
        # pykrx로 데이터 가져오기 시도
        # 새로운 날짜를 문자열로 변환
        prev_date0 = new_date.strftime('%Y%m%d')
        date0 = original_date.strftime('%Y%m%d')
        data = krx.get_index_ohlcv(prev_date0, date0, ticker)
        try:
          # 특정 날짜의 데이터를 가져오려고 시도
          close_price = data.loc[date0]['종가']
          return close_price
        except KeyError:
          recent_data = data[data.index < date0]
          most_recent_data = recent_data.iloc[-1]
          new_price = most_recent_data['종가']
          return new_price
        except Exception as e:
          print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
          return np.nan

# ticker로 종가 가져오는 함수 만들기
def get_close_price_old(ticker,date):
    import yfinance as yf
    import pykrx.stock as krx
    import pandas as pd
    from datetime import datetime, timedelta
    import numpy as np

    original_date = datetime.strptime(date, '%Y-%m-%d')

    # 5일전 데이터부터 가져오기
    new_date = original_date - timedelta(days=5)

    # 새로운 날짜를 문자열로 변환
    prev_date = new_date.strftime('%Y-%m-%d')


    # Yahoo Finance에서 데이터 가져오기
    try:
      stock = yf.Ticker(ticker)
      data = stock.history(start=prev_date, end=date)
      try:
          # 특정 날짜의 데이터를 가져오려고 시도
          close_price = data.loc[date]['Close']
          return close_price
      except KeyError:
          recent_data = data[data.index < date]
          most_recent_data = recent_data.iloc[-1]
          new_price = most_recent_data['Close']
          return new_price
    except KeyError: # 2024년 7월26일 수정
      print('현재가가 없는 종목입니다.')
      return np.nan
    except Exception as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return np.nan

# ticker로 종가 가져오는 함수 만들기 두번째
def get_close_price_btn(ticker_tuple,date,duration):
  ticker, market = ticker_tuple
  # 20240727 새 함수 작성
  import yfinance as yf
  import pykrx.stock as krx
  import pandas as pd
  from datetime import datetime, timedelta
  import numpy as np
  import pykrx.stock as krx

  reference_date = datetime.strptime(date, '%Y-%m-%d')

  # duration 전후 데이터 가져오기
  start_date = (reference_date - timedelta(days=duration*365))
  end_date = (reference_date + timedelta(days=duration*365))

  if market=='yahoo':
    # Yahoo Finance에서 데이터 가져오기
    try:
      stock = yf.Ticker(ticker)
      data = stock.history(start=start_date, end=end_date)
      df=pd.DataFrame(data['Close'])

      # 인덱스 포맷 변경
      df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

      # 기준일의 종가(값이 없을 시 직전 영업일 값으로)
      ref_price = df['Close'].loc[:reference_date.strftime('%Y-%m-%d')].ffill().iloc[-1]

      # 정규화하여 수정주가 칼럼 추가
      df['Adjusted_Close'] = (df['Close'] / ref_price) * 100

      # 6개월 역사적 변동성 계산 (일간 수익률 기준, 연율화)
      df['Returns'] = df['Close'].pct_change()
      df['Volatility_6M'] = df['Returns'].rolling(window=126).std() * np.sqrt(252)

      # 칼럼 이름 변경
      df.columns = [ticker, ticker+'수정주가', '수익율', ticker+'변동성']

      return df

    except KeyError: # 2024년 7월26일 수정
      print('현재가가 없는 종목입니다.')
      return np.nan

  elif market=='krx':
    # pykrx로 데이터 가져오기 시도
    # pykrx로 데이터 가져오기 시도
    # 새로운 날짜를 문자열로 변환
    prev_date1 = start_date.strftime('%Y%m%d')
    date1 = end_date.strftime('%Y%m%d')
    data = krx.get_index_ohlcv(prev_date1, date1, ticker)
    df=pd.DataFrame(data['종가'])

    # 인덱스 포맷 변경
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

    # 기준일의 종가(값이 없을 시 직전 영업일 값으로)
    ref_price = df['종가'].loc[:reference_date.strftime('%Y-%m-%d')].ffill().iloc[-1]

    # 정규화하여 수정주가 칼럼 추가
    df['Adjusted_Close'] = (df['종가'] / ref_price) * 100

    # 6개월 역사적 변동성 계산 (일간 수익률 기준, 연율화)
    df['Returns'] = df['종가'].pct_change()
    df['Volatility_6M'] = df['Returns'].rolling(window=126).std() * np.sqrt(252)

    # 칼럼 이름 변경
    df.columns = [ticker, ticker+'수정주가', '수익율', ticker+'변동성']
    return df





# ticker로 종가 가져오는 함수 만들기 두번째
def get_close_price_btn_old(ticker,date,duration):
    # duration은 년 단위로 입력
    # 2024년 7월26일 데이터베이스 pykrx 추가

    import yfinance as yf
    import pandas as pd
    from datetime import datetime, timedelta
    import numpy as np
    import pykrx.stock as krx

    reference_date = datetime.strptime(date, '%Y-%m-%d')

    # duration 전후 데이터 가져오기
    start_date = (reference_date - timedelta(days=duration*365))
    end_date = (reference_date + timedelta(days=duration*365))

    # Yahoo Finance에서 데이터 가져오기
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        df=pd.DataFrame(data['Close'])

        # 인덱스 포맷 변경
        df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

        # 기준일의 종가(값이 없을 시 직전 영업일 값으로)
        ref_price = df['Close'].loc[:reference_date.strftime('%Y-%m-%d')].ffill().iloc[-1]

        # 정규화하여 수정주가 칼럼 추가
        df['Adjusted_Close'] = (df['Close'] / ref_price) * 100

        # 6개월 역사적 변동성 계산 (일간 수익률 기준, 연율화)
        df['Returns'] = df['Close'].pct_change()
        df['Volatility_6M'] = df['Returns'].rolling(window=126).std() * np.sqrt(252)

        # 칼럼 이름 변경
        df.columns = [ticker, ticker+'수정주가', '수익율', ticker+'변동성']

        return df

    except KeyError:        # 2024년 7월26일 수정
        print('현재가가 없는 종목입니다.')
        return np.nan
    except Exception as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return np.nan


# 2,3종목에 대한 상관계수 분석까지
def vol_corr(tickers,date,duration):
    # 20240727:기초자산가격함수 수정
    # 결측값을 이전 값으로

    import pandas as pd
    import numpy as np

    result_df = pd.DataFrame()

    for ticker in tickers:
        df = get_close_price_btn(uname2yahoo(ticker), date, duration)
        if df is not np.nan:
            result_df = pd.concat([result_df, df], axis=1)

    if len(tickers) >= 2:
        # 결측값을 이전 값으로 채우기
        result_df.ffill(inplace=True)


        # 6개월 상관계수 계산
        returns_df = result_df[[ticker for ticker in tickers]].pct_change()
        rolling_corr = returns_df.rolling(window=126).corr()

        # 상관계수 추출 및 칼럼 추가
        for i in range(len(tickers)):
            for j in range(i + 1, len(tickers)):
                corr = rolling_corr.loc[(slice(None), tickers[i]), tickers[j]].reset_index(level=1, drop=True)
                result_df[f'{tickers[i]}_{tickers[j]}_corr'] = corr

    return result_df

# 새로운 데이터프레임으로 정리하기
def create_combined_df(result_df, tickers):
    import pandas as pd
    combined_df = pd.DataFrame(index=result_df.index)

    # 종가 데이터 추가
    for ticker in tickers:
        combined_df[ticker] = result_df[ticker]

    # 수정주가 데이터 추가
    for ticker in tickers:
        combined_df[f'{ticker}_수정주가'] = result_df[f'{ticker}수정주가']

    # 변동성 데이터 추가
    for ticker in tickers:
        combined_df[f'{ticker}_변동성'] = result_df[f'{ticker}변동성']

        # 상관계수 칼럼 추가
    if len(tickers) == 2:
        combined_df[result_df.columns[-1]] = result_df.iloc[:, -1]
    elif len(tickers) == 3:
        combined_df[result_df.columns[-3]] = result_df.iloc[:, -3]
        combined_df[result_df.columns[-2]] = result_df.iloc[:, -2]
        combined_df[result_df.columns[-1]] = result_df.iloc[:, -1]


    return combined_df

############################################################
# KR code에 따른 발행일 정보 가져오기
############################################################

def krcode2issuedate(file,kr_code):
  import pandas as pd
  df_issue_date=pd.DataFrame()
  df=pd.read_excel(file,skiprows=7,usecols=None)
  KR_Code=df.iloc[0,2:] # 발행코드 정보를 읽어옴
  Issue_Dates=df.iloc[6,2:] # 발행일자 정보를 읽어옴
  Issue_Dates=pd.to_datetime(Issue_Dates, format='%Y%m%d') # 날짜 형식 변경
  df_issue_date['KR_Code']=KR_Code
  df_issue_date['Issue_Dates']=Issue_Dates
  return df_issue_date[df_issue_date['KR_Code']==kr_code]['Issue_Dates'].dt.strftime('%Y-%m-%d').tolist()[0]

# 함수로 처리하기
# 기초자산명을 yahoo ticker로 변환하는 함수
def uname2yahoo(name):
    # 2024년 7월28일 수정
    # 2025년 2월6일 KR7329180004 티커 추가
    # KOSDAQ 150 INDEX 추가(20240726)
    ticker_diction={'I.GSPC':'^GSPC',
                   'SX5E INDEX':'^STOXX50E',
                   'I.N225':'^N225', #Nikkei 225 Index
                   'I.101':'^KS200', # KOSPI200 지수
                   'I.HSCE':'^HSCE', #Hang Seng China Enterprises Index
                    'TSLA US EQUITY':'TSLA',
                    'NVDA US EQUITY':'NVDA', # NVIDIA Corporation의 주식
                    'AMD US EQUITY':'AMD', # Advanced Micro Devices
                    'AMZN US EQUITY':'AMZN',
                    'INTC US EQUITY':'INTC', # intel corportion
                    'MU US EQUITY':'MU', #micron technology
                    'NDX INDEX':'^NDX',# NASDAQ-100 Index
                    'NFLX US EQUITY':'NFLX', #Netflix, Inc
                    'KR7051910008':'051910.KS', # LG화학, 확인
                    'KR7000660001':'000660.KS', # SK 하이닉스, 확인
                    'KR7005930003':'005930.KS', # 삼성전자, 확인
                    'KR7035420009':'035420.KS', # 네이버, 확인
                    'KR7066570003':'066570.KS', # LG전자, 확인
                    'KR7005490008':'005490.KS', # 포스코 홀딩스, 확인
                    'KR7034220004':'034220.KS', # LG디스플레이, 확인
                    'SPXESUP INDEX':'^SPXESUP', # S&P 500 Equal Weight Utilities Index
                    'KR7028260008':'028260.KS', # 삼성 C&T corporation, 확인
                    'AAPL US EQUITY':'AAPL', # Apple
                    'FB US EQUITY':'META', # Meta Platforms, Inc. (이전에는 Facebook, Inc.)의 주식
                    'QCOM UW EQUITY':'QCOM', # Qualcomm Incorporated의 주식
                    'I.GDAXI':'^GDAXI', # DAX (Deutscher Aktienindex)
                    'I.HSI':'^HSI', # Hang Seng Index
                    'KR7105560007':'105560.KS', # KB금융그룹, 확인
                    'SBUX UW EQUITY':'SBUX', # 스타벅스
                    'KR7251270005':'251270.KS', # 넷마블, 확인
                    'KR7207940008':'207940.KS', # 삼성바이오로직스, 확인
                    'KR7086790003':'086790.KS', # 하나금융지주, 확인
                    'KR7015760002':'015760.KS', # 한국전력공사, 확인
                    'KR7316140003':'316140.KS', # 우리금융지주, 확인
                    'KR7012330007':'012330.KS', # 현대모비스, 확인
                    'KR7329180004':'329180.KS', # 현대중공업, 확인, 2025년 2월6일        
                    'BA US EQUITY':'BA', # The Boeing Company
                    'XOM US EQUITY':'XOM', # Exxon Mobil Corporation
                    'KR7005380001':'005380.KS', # 현대자동차, 확인
                    'KR7090430000':'090430.KS', # 아모레퍼시픽, 확인
                    'KR7055550008':'055550.KS', # 신한파이낸셜 그룹, 확인
                    'KR7068270008':'068270.KS', # 셀트리온, 확인
                    'HSTECH INDEX':'HSTECH.HK', # Hang Seng TECH Index, 기간데이터 미제공인듯
                    'MSFT US EQUITY':'MSFT', # Microsoft Corporation
                    'KR7035720002':'035720.KS', # 카카오, 확인
                    'KR7000270009':'000270.KS', # 기아, 확인
                    'KR7009150004':'009150.KS', # 삼성전기, 확인
                    'KOSPI2LG INDEX':'KOSPI2LG.KS', # KOSPI 200 Large Cap Index, 어떤 기초자산인지 미확인
                    'BSK-SKTELECOM':'017670.KS', # SK텔레콤
                    'KR7139480008':'139480.KS', # E마트,확인
                    'C US EQUITY':'C', # Citigroup Inc.
                    'DIS US EQUITY':'DIS', # The Walt Disney Company
                    'KR7034730002':'034730.KS', # (주)SK,확인
                    'KR7006400006':'006400.KS', # 삼성SDI, 확인
                    'KR7017670001':'017670.KS', # SK텔레콤,확인
                    'NKE UN EQUITY':'NKE', # Nike, Inc.의 주식
                    'SPESG INDEX':'^SPESG', # S&P 500 ESG Index, 기간 데이터 미제공인 듯
                    'SX5EESG INDEX':'SX5EESG.SW', # EURO STOXX 50 ESG Index
                    'GM UN EQUITY':'GM', # General Motors Company
                    'KR7036570000':'036570.KS', # 엔씨소프트, 확인
                    'KR7096770003':'096770.KS', # SK이노베이션, 확인
                    'KR7018260000':'018260.KS', # 삼성SDS, 확인
                    'XIN0I INDEX':'XIN0.FGI', # FTSE China 50 Index
                    'KR7033780008':'033780.KS', # KT&G, 확인
                    'AMAT US EQUITY':'AMAT', # Applied Materials, Inc.의 주식
                    'META US EQUITY':'META', # Meta Platforms, Inc. (이전 Facebook, Inc.)의 주식
                    'KR7032830002':'032830.KS', # 삼성생명, 확인
                    'KR7024110009':'024110.KS', # 산업은행, 확인
                    'NVDA UW EQUITY':'NVDA', # NVIDIA Corporation의 주식
                    'KR7000810002':'000810.KS', # 삼성화재, 확인
                    'KR7003550001':'003550.KS', # (주) LG, 확인
                    'GS US EQUITY':'GS', # Goldman Sachs Group, Inc.
                    'TSM US EQUITY':'TSM', # Taiwan Semiconductor Manufacturing Company Limited (TSMC) 주식
                    'BAC US EQUITY':'BAC', # Bank of America Corporation
                    'GOOGL US EQUITY':'GOOGL', #  Alphabet Inc.의 주식
                    'KR7003670007':'003670.KS', # Posco Future M Co., Ltd.
                    'UBER US EQUITY':'UBER', # UBER 미국 주식
                    'PYPL US EQUITY':'PYPL', # Paypal Inc.
                    'ADBE US EQUITY':'ADBE', # Adobe Inc.
                    'KR7373220003':'373220.KS', # LG 에너지 솔루션
                    'AVGO US EQUITY':'AVGO', # Broadcom Inc.
                    'ARM US EQUITY':'ARM', # ARM Holdings plc
                    'LLY US EQUITY':'LLY', # Eli Lilly and Company
                    'PLTR US EQUITY':'PLTR', #  Palantir 의 주식
                    'KR7036460004':'036460.KS', # Korea Gas의 주식
                    'KR7012450003':'012450.KS', # 한화에어로스페이스의 주식
                    'KR7042660001':'042660.KS', # 한화오션의 주식      
                   }
    ticker_diction_krx={'KOSDAQ 150 INDEX':'2203',# KOSDAQ 150 INDEX로서 pykrx의 티커로 대체
                        }
    if name in ticker_diction.keys():
        return ticker_diction[name],'yahoo'
    elif name in ticker_diction_krx.keys():
        return ticker_diction_krx[name],'krx'
    else:
        print(f'{name}라는 티커가 없어 기타로 분류합니다')
        return '기타','Need another DB'


# UA_df와 KR code가 주어지면 기초자산의 변동성과 상관계수 추이를 보여주는 함수 작성
def vol_corr_from_krcode(file,UA_df,krcode,duration):
  # 20240727: 변환전 tickers로 수정
  # 앞에서 만들어진 UA_df를 입력값을 가져옴
  import pandas as pd
  import numpy as np

  uas=UA_df[krcode].iloc[1:4]
  tickers=[]
  for ua in uas:
    tickers.append(ua) # 변환되기 전 기초자산 이름을 tickers로
  issued_date=krcode2issuedate(file,kr_code)
  result_df = vol_corr(tickers, issued_date, duration)
  return result_df,tickers,issued_date

def worst_off_alives_analysis(file,df_Daily_NAV,Biz_Dates):
   # 2024년 6월28일 코드 일부 수정
    import pandas as pd
    import numpy as np

    df=pd.read_excel(file,skiprows=7,usecols=None)
    KR_Code=df.iloc[0,2:] # 발행코드 정보를 읽어옴
    kijun_date=Biz_Dates.iloc[-1].strftime('%Y-%m-%d') # 자료의 마지막 날짜로 설정

    # 기준가 식별 데이터프레임
    # 특정행만 추출
    selected_rows = df.iloc[[5] + list(range(21, 25))]

    # 새로운 데이터프레임으로 저장
    kijun_df = selected_rows.iloc[:,2:].copy()
    kijun_df.columns=KR_Code
    kijun_df.columns.name='KR code'

    # 기초자산 개수 구하기
    nan_counts = kijun_df.iloc[1:5].notna().sum()
    # 새로운 행에 NaN이 아닌 값의 개수를 추가
    nan_counts_df = pd.DataFrame([nan_counts], index=['기초자산갯수'])
    # 기존 데이터프레임에 새로운 행 추가
    kijun_df = pd.concat([kijun_df.iloc[:5], nan_counts_df])
    kijun_df.index=['발행금액','기초자산1','기초자산2','기초자산3','기초자산4','기초자산갯수']

    # '발행금액' 행을 numeric으로 변환
    kijun_df.loc['발행금액'] = pd.to_numeric(kijun_df.loc['발행금액'], errors='coerce')
    kijun_df.loc['기초자산1'] = pd.to_numeric(kijun_df.loc['기초자산1'], errors='coerce')
    kijun_df.loc['기초자산2'] = pd.to_numeric(kijun_df.loc['기초자산2'], errors='coerce')
    kijun_df.loc['기초자산3'] = pd.to_numeric(kijun_df.loc['기초자산3'], errors='coerce')
    kijun_df.loc['기초자산4'] = pd.to_numeric(kijun_df.loc['기초자산4'], errors='coerce')

    # 특정행만 추출
    selected_rows = df.iloc[[5] + list(range(17, 21))]

    # 새로운 데이터프레임으로 저장
    UA_df = selected_rows.iloc[:,2:].copy()
    UA_df.columns=KR_Code
    UA_df.columns.name='KR code'

    # 기초자산 개수 구하기
    nan_counts = UA_df.iloc[1:5].notna().sum()
    # 새로운 행에 NaN이 아닌 값의 개수를 추가
    nan_counts_df = pd.DataFrame([nan_counts], index=['기초자산갯수'])

    # 기존 데이터프레임에 새로운 행 추가
    UA_df = pd.concat([UA_df.iloc[:5], nan_counts_df])
    UA_df.index=['발행금액','기초자산1','기초자산2','기초자산3','기초자산4','기초자산갯수']

    # '발행금액' 행을 numeric으로 변환
    UA_df.loc['발행금액'] = pd.to_numeric(UA_df.loc['발행금액'], errors='coerce')

    # 첫 번째 행의 값 / 마지막 행의 값 계산
    first_row = UA_df.iloc[0]
    last_row = UA_df.iloc[-1]
    values = first_row / last_row

    # UA_df의 2행부터 5행까지의 값 추출하여 1차원 배열로 변환
    unique_assets = pd.unique(UA_df.iloc[1:5].values.ravel('K'))

    # NaN 값을 제거하여 고유한 값만 남김
    unique_assets = unique_assets[~pd.isna(unique_assets)]

    # df_ua_worstoff의 columns는 KR_Code, index는 기초자산명
    df_ua_worstoff = pd.DataFrame(np.zeros((len(unique_assets), len(UA_df.columns))), index=unique_assets, columns=UA_df.columns)
    df_ua_worstoff_ratio = pd.DataFrame(np.zeros((len(unique_assets), len(UA_df.columns))), index=unique_assets, columns=UA_df.columns)

    tags=['기초자산1','기초자산2','기초자산3','기초자산4']

    for col in UA_df.columns.values:
        U_nums=UA_df.loc['기초자산갯수',col]
        worst_off=[]

        # KR code별로 반복실행
        # 기초자산 개수별로 기준가와 자료마지막날의 현재가를 불러와서 비율로 변환
        # for 문이 끝나면 각 코드별로 기준가 대비 비율값이 worst_off에 저장됨
        for u in range(U_nums): # 기초자산갯수 만큼 반복문 실행
            u=u+1 # 기초자산명 작성을 위해 1을 더해줌
            U_name=UA_df.loc['기초자산'+str(u),col] # fn가이드의 기초자산 이름 불러오기
            U_price=get_close_price(uname2yahoo(U_name),kijun_date)
            if U_price is not None and not np.isnan(float(U_price)):
                U_kijun=kijun_df.loc['기초자산'+str(u),col] # fn가이드의 기초자산 기준가 불러오기
                u_ratio=U_price/U_kijun
            else: # 기초자산 현재가를 알 수 없어서 기준가로 통일함
                u_ratio=1
            worst_off.append(u_ratio)

        # KR code 별로 기초자산 기준가 대비 최소값을 구함
        min_value = min(worst_off)

        # 최소값의 인덱스를 찾음
        # 최소값의 모든 인덱스를 찾기
        min_indices = [index for index, value in enumerate(worst_off) if value == min_value]
        if len(min_indices) == 1: # 최소값이 unique하면
            # worstoffing 작업
            tag_name=tags[min_indices[0]] # 기초자산1,2,3,4 중 하나로 리턴
            worstoff=UA_df.loc[tag_name,col] # fn가이드 기초자산명을 찾아서 worstoff 기초자산명 확인
            df_ua_worstoff.loc[worstoff, col] = UA_df.loc['발행금액',col] # 해당 기초자산의 KR code 발행금액 설정
            df_ua_worstoff_ratio.loc[worstoff, col]=min_value # 기초자산의 KR code 별 기준가대비 비율 저장
        else: # 최소값이 여러개 있다면
            min_num=len(min_indices) # 최소값의 갯수
            print(f'{col} 발행종목의 기초자산의 worst off는 {min_num}개 입니다.')

            for i in min_indices:
                tag_name=tags[min_indices[i-1]] # 기초자산1,2,3,4 중 하나로 리턴
                worstoff=UA_df.loc[tag_name,col] # fn가이드 기초자산명을 찾아서 worstoff 기초자산명 확인
                df_ua_worstoff.loc[worstoff, col] = UA_df.loc['발행금액',col]/min_num # 해당 기초자산의 KR code 발행금액을 기초자산 갯수로 나누어 줌
                df_ua_worstoff_ratio.loc[worstoff, col]=min_value # 기초자산의 KR code 별 기준가대비 비율 저장

    # 살아있는 종목들 추출
    alived_codes=kr_codes_for_alives(df_Daily_NAV,Biz_Dates.iloc[-1])
    df_ua_worstoff_alives=df_ua_worstoff[alived_codes]
    df_ua_worstoff_ratio_alives=df_ua_worstoff_ratio[alived_codes]


    return df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes

def calculate_row_stats(row):
    # 2024년 6월17일 수정
    import pandas as pd
    import numpy as np
    non_zero_values = row[row != 0] # 행에서 0인 아닌 것들의 개수를 셈
    if len(non_zero_values) == 0: # 행의 모든 것이 0이면
        return pd.Series({
            'min': 0,
            'avg': 0,
            'median': 0,
            'max': 0,
        })
    return pd.Series({
        'min': non_zero_values.min(),
        'avg': non_zero_values.mean(),
        'median': non_zero_values.median(),
        'max': non_zero_values.max(),
    })


def worst_off_alives_summary(df_ua_alives, df_ua_alives_summary_out,df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes):
    import pandas as pd
    import numpy as np
    # 2024년 6월17일 수정
    # df_ua_worstoff_alives에는 worst off 기초자산별 발행금액
    # df_ua_worstoff_ratio_alives에는 worst off 기초자산의 기준가대비 비율 정보가 있음.
    # df_ua_alives에는 기초자산-KR code의 발행금액 정보
    # df_ua_alives_summary_out 기초자산별 종목수	총 종목수 대비 비율	발행총액(10억)	총 발행총액 대비 비율 정보
    Issued_Num=len(alived_codes) # 살아있는 발행종목 수
    Issued_Notional=df_ua_alives_summary_out.sum().values[2] # 10억 기준임
    # Applying the function to each row
    df_summary = df_ua_worstoff_ratio_alives.apply(calculate_row_stats, axis=1)
    # 각 행에서 0이 아닌 값들의 개수를 세고 'A'라는 새로운 열로 추가
    df_summary['잔존종목수'] = df_ua_worstoff_alives.apply(lambda row: (row != 0).sum(), axis=1) # 0이 아닌 것들의 개수를 셈
    df_summary['잔존종목수대비 비율']=df_summary['잔존종목수']/Issued_Num
    df_summary['잔존총액(10억)']=df_ua_worstoff_alives.apply(lambda row: row[row != 0].sum(), axis=1)/1e+9 # 0인 아닌 것들의 총합을 구함
    df_summary['잔존총액대비 비율']=df_summary['잔존총액(10억)']/Issued_Notional


    # '종목수' 칼럼을 큰 순서로 정렬하고 상위 10개 행을 출력
    top_10 = df_summary.sort_values(by='잔존종목수', ascending=False).head(10)
    ascending_index=df_summary.sort_values(by='잔존종목수', ascending=False).index

    # 상위 10개행을 제거한 데이터프레임
    other_df = df_summary.drop(top_10.index)
    sum_row=other_df.sum()
    # 19개행과 기타행의 합으로 재구성
    top_10.loc['기타'] = sum_row
    worst_off_alives_summary_out=top_10

    df_ua_worstoff_ratio_alives_printing_ver=pd.DataFrame(df_ua_worstoff_ratio_alives,index=ascending_index)

    return worst_off_alives_summary_out,df_ua_worstoff_ratio_alives_printing_ver


# -*- coding: utf-8 -*-
"""
Created on 2024.06.23.
20240718 : 상환종목이 전혀 없을 경우 발생 문제 수정
20240720 : worstoff 분석 추가
@author: S.T.Hwang
"""


def pptout(file,file_out):

    file_out_ppt= file_out

    import pandas as pd
    import numpy as np

    df=pd.read_excel(file,skiprows=32,usecols=None)
    df_ua,df_ua_summary_out=underlyings_for_ELS(file)

    df_Daily_NAV=df.iloc[2:,2:] # Daily NAVs 만을 발췌
    df_Daily_NAV=df_Daily_NAV.fillna(0) # NaN을 0으로 바꾸기
    df_Daily_NAV = df_Daily_NAV.apply(pd.to_numeric, errors='coerce') # 모든 열을 숫자로 변환

    # 연속된 0인 행 삭제
    remove_consecutive_zeros(df_Daily_NAV)

    # 일자를 인덱스 정보로 불러오고 포맷변경
    Biz_Dates=df.iloc[-len(df_Daily_NAV):,1]
    Biz_Dates=pd.to_datetime(Biz_Dates, format='%Y%m%d')


    # ELS 발행정보 정보 읽어오기
    df_Issuance_Info=pd.read_excel(file, nrows=35) # 처음 35행만 읽어오기
    Notional_Amount = df_Issuance_Info.iloc[12,2:] # 발행총액 정보를 읽어옴
    Notional_Amount = Notional_Amount.apply(int) # 숫자 데이터로 변환
    # Series 이름제거
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    KR_Code=df_Issuance_Info.iloc[7,2:] # 발행코드 정보를 읽어옴

    # 날짜를 인덱스로 설정하기
    df_Daily_NAV = df_Daily_NAV.set_index(Biz_Dates)
    df_Daily_NAV.index.name = 'Biz_Dates'

    df_Daily_NAV = df_Daily_NAV.rename(columns=KR_Code) #칼럼 이름 주기

    # 기초자산정보 계산
    df_ua_alives_summary_out=underlyings_for_ELS_alives(df_ua,df_Daily_NAV,Biz_Dates)

    # 발행 정보를 분석하기 위한 새로운 데이터프레임 만들기
    issued_date=df_Issuance_Info.iloc[13,2:] # 각 종목의 발행일자가 저장됨
    issued_date = pd.to_datetime(issued_date) # 날짜형식으로 변환
    # 인덱스를 초기화하여 시리즈 재설정
    issued_date = issued_date.reset_index(drop=True)
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    df_issued_summary=pd.DataFrame(data={'발행일':issued_date,'발행총액':Notional_Amount})
    df_issued_summary.index=KR_Code
    df_issued_summary.index.name='KR code'

    # 발행 총액을 곱하여 Market Cap 계산
    # 발행 총액 연산을 위해 numpy array 포맷으로 변환

    np_Notional_Amount=np.array(Notional_Amount)
    np_df_Daily_NAV=np.array(df_Daily_NAV)
    df_Daily_NAV_Market_Cap=pd.DataFrame(data=np_df_Daily_NAV*np_Notional_Amount,index=Biz_Dates,columns=KR_Code)/10000
    df_Daily_NAV_Market_Cap.index.name = 'Biz_Dates' # 인덱스 이름지정
    df_Daily_NAV_Market_Cap.columns.name = 'KR_Code' # 칼럼 이름 지정
    # 날짜별 시장가치의 총합임
    df_Daily_NAV_Market_Cap['날짜별발행잔액'] = df_Daily_NAV_Market_Cap.sum(axis=1)
    # 행에서 0이 아닌 종목들의 수를 새로운 칼럼으로 만들어주기
    # 첫 번째 열에 0이 아닌 데이터의 개수를 계산하여 새로운 열 추가
    df_Daily_NAV.insert(0, 'non_zero_count', df_Daily_NAV.astype(bool).sum(axis=1))

    df_Num_ELS = df_Daily_NAV.iloc[0:,0]
    Max_Num_ELS = df_Num_ELS.max()

    ##########################################
    ########### EW indexing
    ###########################################
    # KR코드에 해당한 열만 추출하여 각 행의 총합을 A칼럼으로 추가...전체NAV합계
    df_Daily_NAV['A'] = df_Daily_NAV.filter(regex='^KR').sum(axis=1) #

    # 신규발행 합계 열(B) 만들기...신규발행NAV합계
    df_Daily_NAV['B'] = df_Daily_NAV[df_Daily_NAV.shift(1).eq(0)].filter(regex='^KR').sum(axis=1)

    # C칼럼 만들기...기존발행NAV합계
    df_Daily_NAV['C']=df_Daily_NAV.A-df_Daily_NAV.B

    # 상환종목합계 만들기...상환종목NAV합계
    df_Daily_NAV['D'] = df_Daily_NAV[df_Daily_NAV.shift(-1).eq(0)].filter(regex='^KR').sum(axis=1)

    # F 칼럼 만들기...전체빼기상환종목NAV합계
    df_Daily_NAV['F']=df_Daily_NAV.A-df_Daily_NAV.D

    # E 칼럼 만들기
    # C칼럼과 F칼럼의 데이터에 자연로그 취하기
    df_Daily_NAV['C_log'] = np.log(df_Daily_NAV['C'])
    df_Daily_NAV['F_log_shifted'] = np.log(df_Daily_NAV['F'].shift(1))
    # E칼럼 계산하기
    df_Daily_NAV['E'] = df_Daily_NAV['C_log'] - df_Daily_NAV['F_log_shifted']
    # 불필요한 열 제거하기
    df_Daily_NAV = df_Daily_NAV.drop(['C_log', 'F_log_shifted'], axis=1)

    # G칼럼 만들기...EW Index 값
    # 첫 번째 행의 G값을 1로 설정
    df_Daily_NAV.at[df_Daily_NAV.index[0], 'G'] = 1
    # G칼럼 계산하기
    for i in range(1, len(df_Daily_NAV)):
        df_Daily_NAV.at[df_Daily_NAV.index[i], 'G'] = df_Daily_NAV.at[df_Daily_NAV.index[i - 1], 'G'] + df_Daily_NAV.at[df_Daily_NAV.index[i], 'E']

    # 평균 NAV 수익율 칼럼(H) 작성
    df_Daily_NAV['H']=(df_Daily_NAV['A']/df_Daily_NAV['non_zero_count']-10000)/10000

    ##########################################
    ########### Market cap indexing
    ###########################################
    df_Daily_NAV_Market_Cap['A'] = df_Daily_NAV_Market_Cap.filter(regex='^KR').sum(axis=1)

    # 신규발행 합계 열(B) 만들기
    df_Daily_NAV_Market_Cap['B'] = df_Daily_NAV_Market_Cap[df_Daily_NAV_Market_Cap.shift(1).eq(0)].filter(regex='^KR').sum(axis=1)

    # C칼럼 만들기
    df_Daily_NAV_Market_Cap['C']=df_Daily_NAV_Market_Cap.A-df_Daily_NAV_Market_Cap.B

    # 상환종목합계 만들기
    df_Daily_NAV_Market_Cap['D'] = df_Daily_NAV_Market_Cap[df_Daily_NAV_Market_Cap.shift(-1).eq(0)].filter(regex='^KR').sum(axis=1)

    # F 칼럼 만들기
    df_Daily_NAV_Market_Cap['F']=df_Daily_NAV_Market_Cap.A-df_Daily_NAV_Market_Cap.D

    ######################## E 칼럼 만들기 #############################
    # C칼럼과 F칼럼의 데이터에 자연로그 취하기
    df_Daily_NAV_Market_Cap['C_log'] = np.log(df_Daily_NAV_Market_Cap['C'])
    df_Daily_NAV_Market_Cap['F_log_shifted'] = np.log(df_Daily_NAV_Market_Cap['F'].shift(1))
    # E칼럼 계산하기
    df_Daily_NAV_Market_Cap['E'] = df_Daily_NAV_Market_Cap['C_log'] - df_Daily_NAV_Market_Cap['F_log_shifted']
    # 불필요한 열 제거하기
    df_Daily_NAV_Market_Cap = df_Daily_NAV_Market_Cap.drop(['C_log', 'F_log_shifted'], axis=1)

    ######################## G 칼럼 만들기 #############################
    # 첫 번째 행의 G값을 1로 설정
    df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[0], 'G'] = 1
    # G칼럼 계산하기
    for i in range(1, len(df_Daily_NAV_Market_Cap)):
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i], 'G'] = \
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i - 1], 'G'] +\
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i], 'E']

     ##########################################
     ########### 산 자 분석
     ###########################################

     # 인덱스에 함수 적용하여 새로운 열들 추가
    for index, row in df_Daily_NAV.iterrows():
        result,min_Ret_index,max_Ret_index = stats_for_alives(df_Daily_NAV,index)  # 인덱스에 함수 적용
        for column_name, value in result.items():
            df_Daily_NAV.at[index, f'Alive_{column_name}'] = value  # 새로운 열들 추가
        df_Daily_NAV.at[index, 'min_Return_KR_code'] = min_Ret_index
        df_Daily_NAV.at[index, 'min_Return_issued_date']=df_issued_summary.at[min_Ret_index,'발행일'].strftime('%Y-%m-%d')
        df_Daily_NAV.at[index, 'max_Return_KR_code'] = max_Ret_index
        df_Daily_NAV.at[index, 'max_Return_issued_date']=df_issued_summary.at[max_Ret_index,'발행일'].strftime('%Y-%m-%d')

    # monthly data 추출
    df_alive_stats=df_Daily_NAV.resample('ME').last().iloc[:,-12:]
    # 날짜 포맷 변경
    df_alive_stats.index = pd.to_datetime(df_alive_stats.index)
    df_alive_stats.index = df_alive_stats.index.strftime('%Y-%m-%d')

     ##########################################
     ########### 죽은 자 분석
     ###########################################

    # 매월 말일의 인덱스 선택
    monthly_end_index = df_Daily_NAV.resample('ME').last().index

    # 빈 데이터프레임 생성
    df_for_redeemed = pd.DataFrame(index=monthly_end_index)

    for date in monthly_end_index:
        date_str = date.strftime('%Y-%m-%d')  # 날짜를 문자열로 변환
        D,ABS,PA,pos_ret_abs,neg_ret_abs,pos_ret_pa,neg_ret_pa,min_duration,max_duration,min_pa_return,max_pa_return = stats_for_redeemed(df_Daily_NAV,date_str)
        if D is not None:
            for column_name, value in D.items():
                df_for_redeemed.at[date, f'Durations_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in ABS.items():
                df_for_redeemed.at[date, f'abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in PA.items():
                df_for_redeemed.at[date, f'p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in pos_ret_abs.items():
                df_for_redeemed.at[date, f'(+)abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in neg_ret_abs.items():
                df_for_redeemed.at[date, f'(-)abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in pos_ret_pa.items():
                df_for_redeemed.at[date, f'(+)p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in neg_ret_pa.items():
                df_for_redeemed.at[date, f'(-)p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            df_for_redeemed.at[date, 'min_duration_KR_code'] = min_duration
            df_for_redeemed.at[date, 'min_duration_issued_date']=df_issued_summary.at[min_duration,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'max_duration_KR_code'] = max_duration
            df_for_redeemed.at[date, 'max_duration_issued_date']=df_issued_summary.at[max_duration,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'min_pareturn_KR_code'] = min_pa_return
            df_for_redeemed.at[date, 'min_pareturn_issued_date']=df_issued_summary.at[min_pa_return,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'max_pareturn_KR_code'] = max_pa_return
            df_for_redeemed.at[date, 'max_pareturn_issued_date']=df_issued_summary.at[max_pa_return,'발행일'].strftime('%Y-%m-%d')

    # 날짜 포맷 변경
    df_for_redeemed.index = pd.to_datetime(df_for_redeemed.index)
    df_for_redeemed.index = df_for_redeemed.index.strftime('%Y-%m-%d')


     ##########################################
     ########### 특정 날짜에서 발행된 종목수, 발행금액 보기
     ###########################################

    # 발행 정보를 분석하기 위한 새로운 데이터프레임 만들기
    issued_date=df_Issuance_Info.iloc[13,2:]
    issued_date = pd.to_datetime(issued_date) # 날짜형식으로 변환
    # 인덱스를 초기화하여 시리즈 재설정
    issued_date = issued_date.reset_index(drop=True)
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    df_issued_summary=pd.DataFrame(data={'발행일':issued_date,'발행총액':Notional_Amount})
    df_issued_summary.index=KR_Code
    df_issued_summary.index.name='KR code'

    # df_Daily_NAV의 날짜 인덱스를 기반으로 새로운 열 생성
    df_Daily_NAV[['발행된ELS종목수', '발행총액_합계']] = df_Daily_NAV.index.to_series().apply(
        lambda date: pd.Series(get_issue_amount(df_issued_summary, date)))
    df_Daily_NAV[['발행된ELS종목수', '발행총액_합계']]
    # 발행총액을 10억 단위로 변환
    df_Daily_NAV['발행총액(10억)'] = df_Daily_NAV['발행총액_합계'] / 1e+9

    ##########################################
    ########### 특정 날짜에서 상환된 종목수, 발행금액 보기
    ###########################################

    # df_Daily_NAV의 날짜 인덱스를 기반으로 새로운 열 생성
    # 날짜마다 상환되는 것을 계산하느라 시간 많이 걸림
    df_Daily_NAV[['상환된ELS종목수', '상환된발행액_합계(10억)']] = df_Daily_NAV.index.to_series().apply(
        lambda date: pd.Series(info_for_redeemed(df_Daily_NAV_Market_Cap,df_issued_summary,date)))
    df_Daily_NAV[['상환된ELS종목수', '상환된발행액_합계(10억)']]

    ##########################################
    ########### Sharpe Ratio
    ###########################################

    rf=0.05 # 금리 세팅

    # 매월 말일의 인덱스 선택
    monthly_end_index = df_Daily_NAV.resample('ME').last().index

    # 빈 데이터프레임 생성
    df_Sharpe_for_redeemed = pd.DataFrame(index=monthly_end_index)

    for date in monthly_end_index:
        date_str = date.strftime('%Y-%m-%d')  # 날짜를 문자열로 변환
        results=sharpe_ratio_for_redeemed(df_Daily_NAV,rf,date_str).describe()
        for column_name, value in results.items():
              df_Sharpe_for_redeemed.at[date, f'SharpeR_{column_name}'] = value  # 새로운 열들 추가


    ##########################################
    ########### PPT 자료 작성하기: Colab
    ###########################################
    from pandas_datareader import data as pdr
    import yfinance as yfin


    # Daily info 정리하기
    df_Daily_NAV_summary=df_Daily_NAV.iloc[:, [0] + list(range(-17, 0))] # 처음과 마지막 17개의 칼럼만 추출


    # 시장가치잔액(10억) 컬럼을 추가할 데이터프레임을 복사하여 변경
    df_Daily_NAV_summary = df_Daily_NAV_summary.copy()
    imsi=df_Daily_NAV_Market_Cap['날짜별발행잔액']/1e+9
    df_Daily_NAV_summary['시장가치잔액(10억)'] = imsi


    # 칼럼 위치 조정
    # 'non_zero_count' 칼럼을 삭제한 후, 맨 뒤에서 두 번째 위치에 다시 삽입
    cols = list(df_Daily_NAV_summary.columns)
    cols.remove('non_zero_count')  # non_zero_count 칼럼을 제외한 나머지 칼럼들의 순서를 정함
    cols.insert(-1, 'non_zero_count')  # non_zero_count 칼럼을 원하는 위치에 삽입
    df_Daily_NAV_summary = df_Daily_NAV_summary[cols]  # 새로운 칼럼 순서로 데이터프레임을 재구성

    # 중복칼럼 삭제
    df_Daily_NAV_summary.drop(columns=['발행총액_합계'],inplace=True)

    # Column Rename
    df_Daily_NAV_summary = df_Daily_NAV_summary.rename(columns={'non_zero_count': '잔존 ELS 종목수'})

    # 날짜 포맷 변경
    df_Daily_NAV_summary.index = pd.to_datetime(df_Daily_NAV_summary.index)
    df_Daily_NAV_summary.index = df_Daily_NAV_summary.index.strftime('%Y-%m-%d')
    df_daily_stats=df_Daily_NAV_summary.drop(columns=['Alive_25%','Alive_75%'])
    df_daily_stats['EW Index']=df_Daily_NAV['G']
    df_daily_stats['Market Cap Index']=df_Daily_NAV_Market_Cap['G']
    last_two_columns = df_daily_stats.iloc[:, -2:]  # 마지막 두 개의 칼럼 선택
    df_daily_stats.drop(df_daily_stats.columns[-2:], axis=1, inplace=True)  # 마지막 두 개의 칼럼 삭제
    df_daily_stats = pd.concat([last_two_columns, df_daily_stats], axis=1)  # 마지막 두 개의 칼럼을 맨 앞으로 이동
    last_six_columns = df_daily_stats.iloc[:, -6:]  # 마지막 여섯 개의 칼럼 선택
    df_daily_stats.drop(df_daily_stats.columns[-6:], axis=1, inplace=True)  # 마지막 여섯 개의 칼럼 삭제
    df_daily_stats = pd.concat([df_daily_stats.iloc[:, :2], last_six_columns, df_daily_stats.iloc[:, 2:]], axis=1)  # 칼럼 삽입

    # Monthly info 정리하기
    df_monthly_stats_for_redeemed=df_for_redeemed
    selected_columns = df_monthly_stats_for_redeemed.iloc[:, 22:26]
    df_monthly_stats_for_redeemed.drop(df_monthly_stats_for_redeemed.columns[22:26], axis=1, inplace=True)
    df_monthly_stats_for_redeemed = pd.concat([df_monthly_stats_for_redeemed.iloc[:, :4], selected_columns, df_monthly_stats_for_redeemed.iloc[:, 4:]], axis=1)
    selected_columns = df_monthly_stats_for_redeemed.iloc[:, -4:]
    df_monthly_stats_for_redeemed.drop(df_monthly_stats_for_redeemed.columns[-4:], axis=1, inplace=True)
    df_monthly_stats_for_redeemed = pd.concat([df_monthly_stats_for_redeemed.iloc[:, :11], selected_columns, df_monthly_stats_for_redeemed.iloc[:, 11:]], axis=1)
    df_monthly_stats_for_redeemed['SharpeR_mean']=df_Sharpe_for_redeemed['SharpeR_mean']
    df_monthly_stats_for_redeemed['SharpeR_std']=df_Sharpe_for_redeemed['SharpeR_std']


    df_ua_alives, df_ua_alives_summary_out,alived_codes=underlyings_for_ELS_alives(df_ua,df_Daily_NAV,Biz_Dates)

    with pd.ExcelWriter(file_out_ppt) as writer:

        final_date=df_daily_stats.index[-1]
        df_final_date = pd.DataFrame({'A':['기준일'],'B':[final_date]})


        #############################################################
        ############## #0.1 웍쉿 작성 #############################
        #############################################################

        df_final_date.to_excel(writer, sheet_name='#0.1 발행금액분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=df_ua_summary_out.sum().values[0]
        Issued_Notional=df_ua_summary_out.sum().values[2]
        df_ua_imsi = pd.DataFrame({'A':['총 종목수','총 발행총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.1 발행금액분석', startrow=1, startcol=0, index=False, header=None)
        df_ua_summary_out.to_excel(writer, sheet_name='#0.1 발행금액분석',startrow=7)

        #############################################################
        ############## #0.2 웍쉿 작성 #############################
        #############################################################

        df_final_date.to_excel(writer, sheet_name='#0.2 잔존금액분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=df_ua_alives_summary_out.sum().values[0]
        Issued_Notional=df_ua_alives_summary_out.sum().values[2]
        df_ua_imsi = pd.DataFrame({'A':['총 잔존 종목수','총 잔존 발행총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.2 잔존금액분석', startrow=1, startcol=0, index=False, header=None)
        df_ua_alives_summary_out.to_excel(writer, sheet_name='#0.2 잔존금액분석',startrow=7)

        #############################################################
        ############## #0.3웍쉿 작성: Worstoff 분석 #################
        #############################################################
        #  df_ua,df_ua_summary_out=underlyings_for_ELS(file) 을 본 함수 시작 부분에서 실행하였음
        df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes=worst_off_alives_analysis(file,df_Daily_NAV,Biz_Dates)
        worst_off_alives_summary_out,df_ua_worstoff_ratio_alives_printing_ver=worst_off_alives_summary(df_ua_alives, df_ua_alives_summary_out,df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes)
        df_final_date.to_excel(writer, sheet_name='#0.3 Worstoff분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=len(alived_codes) # 살아있는 발행종목 수
        Issued_Notional=df_ua_alives_summary_out.sum().values[2] # 10억 기준임
        df_ua_imsi = pd.DataFrame({'A':['총 잔존종목수','총 잔존총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.3 Worstoff분석', startrow=1, startcol=0, index=False, header=None)
        worst_off_alives_summary_out.iloc[:, 4:].to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7) # 마지막 4개 칼럼 출력
        worst_off_alives_summary_out.iloc[:, :4].to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7,startcol=6) # 처음 4개 칼럼 출력
        df_ua_worstoff_ratio_alives_printing_ver.to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7,startcol=12) # worstoff 기준가 출력 (기초자산별-KR코드별)


        #############################################################
        ################# #1번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_01=df_daily_stats[['발행된ELS종목수','발행총액(10억)']]
        df_daily_stats_01_summary=df_daily_stats_01.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_01_summary.to_excel(writer, sheet_name='#1. 발행종목수&금액')
        df_daily_stats_01.to_excel(writer, sheet_name='#1. 발행종목수&금액',startrow=10)

        #############################################################
        ################# #2번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_02=df_daily_stats[['EW Index','Market Cap Index']]
        df_daily_stats_02_summary=df_daily_stats_02.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_02_summary.to_excel(writer, sheet_name='#2. ELS Index')
        df_daily_stats_02.to_excel(writer, sheet_name='#2. ELS Index',startrow=10)

        #############################################################
        ################# #3번째 웍쉿 작성  ########################
        #############################################################
        import datetime
        # 조회날짜 설정
        start=df_daily_stats.index[0]
        date_str = final_date
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')  # 문자열을 datetime 객체로 변환합니다.
        date_obj_plus_one_day = date_obj + datetime.timedelta(days=1)  # 날짜에 하루를 더해줍니다.
        end=date_obj_plus_one_day.strftime('%Y-%m-%d')

        #yfin.pdr_override()
        tickers=['^KS200','^HSCE','^N225','^SPX','^STOXX50E','TSLA','AMD','NVDA','005930.KS','005380.KS']

        data = {}
        for t in tickers:
            data[t]=yfin.download(t,start=start,end=end,auto_adjust=False)['Close']
        df_underlyings=pd.DataFrame(data)

        # 없는 데이터 채우기
        #df_underlyings = df_underlyings.fillna(method='ffill') # 빈 데이터는 앞데이터로
        df_underlyings = df_underlyings.ffill() # 빈 데이터는 앞데이터로
        #df_underlyings = df_underlyings.fillna(method='bfill') # 앞에도 없으면 뒤데이터로
        df_underlyings = df_underlyings.bfill() # 앞에도 없으면 뒤데이터로

        # 날짜 포맷 변경
        df_underlyings.index = pd.to_datetime(df_underlyings.index)
        df_underlyings.index = df_underlyings.index.strftime('%Y-%m-%d')

        # 통계량 작성
        out_stats_underlying=df_underlyings.describe().loc[['min','mean', '50%','max']]
        df_out_stats_underlying=pd.DataFrame(out_stats_underlying)
        df_daily_stats_03=df_daily_stats[['EW Index']]
        df_daily_stats_03_summary=df_daily_stats_03.describe().loc[['min','mean', '50%','max']]

        # 데이터 타입 확인 및 변환
        df_daily_stats_03.index = df_daily_stats_03.index.astype(str)
        df_underlyings.index = df_underlyings.index.astype(str)

        # 인덱스 정렬
        df_daily_stats_03 = df_daily_stats_03.sort_index()
        df_underlyings = df_underlyings.sort_index()

        # 인덱스 이름 확인 및 변경
        df_daily_stats_03 = df_daily_stats_03.rename_axis('date')
        df_underlyings = df_underlyings.rename_axis('date')

        # 각 주가를 정규화시키기
        df_underlyings=df_underlyings.iloc[:, :5] #첫 5개의 칼럼만 발췌
        df_normalized = df_underlyings / df_underlyings.iloc[0,:]

        # 정규화된 주가의 통계량 구하기
        out_stats_underlying=df_normalized.describe().loc[['min','mean', '50%','max']]
        df_out_stats_underlying=pd.DataFrame(out_stats_underlying)

        # 통계량 병합
        df_daily_stats_03_summary=pd.concat([df_daily_stats_03_summary, df_out_stats_underlying], axis=1, join='inner')
        df_daily_stats_03_summary.to_excel(writer, sheet_name='#3. ELS&GEI')

        # 병합
        merged_df = df_daily_stats_03.merge(df_normalized, left_index=True, right_index=True, how='inner')
        merged_df.to_excel(writer, sheet_name='#3. ELS&GEI',startrow=10)

        #############################################################
        ################# #4번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_04=df_daily_stats[['EW Index','잔존 ELS 종목수']]
        df_daily_stats_04_summary=df_daily_stats_04.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_04_summary.to_excel(writer, sheet_name='#4. EW&해당ELS')
        df_daily_stats_04.to_excel(writer, sheet_name='#4. EW&해당ELS',startrow=10)

        #############################################################
        ################# #5~9번째 웍쉿 작성  ########################
        #############################################################
        # 데이터프레임 생성
        total_issued=df_daily_stats_01_summary.iloc[3,0]
        df_t_issued = pd.DataFrame({'A':['발행된ELS종목수'],'B':[total_issued]})
        df_t_issued.to_excel(writer, sheet_name='#5.상환비율', startrow=0, startcol=1, index=False, header=None)

        # try-except 블록을 사용하여 에러 발생시 코드를 스킵
        try:
            df_daily_stats_05 = df_monthly_stats_for_redeemed[['Durations_count']]
            #df_daily_stats_05.rename(columns={'Durations_count': '조기/만기상환갯수'}, inplace=True)
            #df_daily_stats_05['조기/만기상환비율'] = df_daily_stats_05['조기/만기상환갯수'] / total_issued
            df_daily_stats_05 = df_daily_stats_05.rename(columns={'Durations_count': '조기/만기상환갯수'}).copy()
            df_daily_stats_05.loc[:, '조기/만기상환비율'] = df_daily_stats_05['조기/만기상환갯수'] / total_issued
            df_daily_stats_05 = df_daily_stats_05.loc[:, ['조기/만기상환비율', '조기/만기상환갯수']]
            df_daily_stats_05.to_excel('output.xlsx', sheet_name='#5.상환비율', startrow=10)

            df_daily_stats_06=df_daily_stats_05['조기/만기상환비율']
            df_daily_stats_06 = pd.concat([df_daily_stats_06, df_monthly_stats_for_redeemed['p.a._ret_mean']], axis=1)
            df_daily_stats_06.rename(columns={'p.a._ret_mean':'평균 연환산 수익율'},inplace=True)
            df_t_issued.to_excel(writer, sheet_name='#6.상환비율&연환산수익율', startrow=0, startcol=1, index=False, header=None)
            df_daily_stats_06.to_excel(writer, sheet_name='#6.상환비율&연환산수익율',startrow=10)

            df_daily_stats_06_01 =pd.concat([df_daily_stats_06, df_monthly_stats_for_redeemed[['Durations_mean','(+)abs_ret_count']]], axis=1)
            df_daily_stats_06_01['+상환비율']=df_daily_stats_06_01['(+)abs_ret_count']/total_issued
            df_daily_stats_06_01.drop(columns=['(+)abs_ret_count'],inplace=True)
            df_daily_stats_06_01 =pd.concat([df_daily_stats_06_01, df_monthly_stats_for_redeemed[['min_pareturn_KR_code','max_pareturn_KR_code']]], axis=1)
            df_t_issued.to_excel(writer, sheet_name='#6.참고', startrow=0, startcol=1, index=False, header=None)
            df_daily_stats_06_01.to_excel(writer, sheet_name='#6.참고',startrow=10)

            ############## 상환된 자료 분석 #############################
            # 데이터의 마지막 인덱 날짜를 찾기

            out=hist_for_redeemded(df_Daily_NAV,final_date)
            out_stats=out.describe().loc[['min','mean', '50%','max']]
            df_out_stats=pd.DataFrame(out_stats)
            df_out_stats.rename(columns={'p.a.return':'연환산 수익율'},inplace=True)
            min_redeemed_code=out.idxmin()
            max_redeemed_code=out.idxmax()
            df_out_stats['해당 KR Code 값']=[min_redeemed_code,np.nan,np.nan,max_redeemed_code]
            df_stats_07=pd.DataFrame(out)
            df_stats_07.rename(columns={'p.a.return':'연환산 수익율'},inplace=True)

            df_final_date.to_excel(writer, sheet_name='#7.상환완료된 ELS 연환산수익율 분포', startrow=0, startcol=0, index=False, header=None)
            
            df_out_stats.to_excel(writer,sheet_name='#7.상환완료된 ELS 연환산수익율 분포',startrow=2)
            df_stats_07.to_excel(writer,sheet_name='#7.상환완료된 ELS 연환산수익율 분포',startrow=10)
            
            #2025년 7월12일 추가
            num_rows = df_stats_07.shape[0] # 데이터 프레임 행의 개수
            df_07_count = pd.DataFrame({'A':['상환완료된ELS개수'],'B':[num_rows]})
            df_final_date.to_excel(writer, sheet_name='#7.상환완료된 ELS 연환산수익율 분포', startrow=1, startcol=0, index=False, header=None)


            # Worst Performer 분석
            NAVs = df_Daily_NAV.loc[df_Daily_NAV[min_redeemed_code] != 0, min_redeemed_code]
            df_Worst=pd.DataFrame(NAVs)/10000
            df_Worst.rename(columns={ min_redeemed_code:'ELS % NAV'},inplace=True)
            # 날짜 포맷 변경
            df_Worst.index = pd.to_datetime(df_Worst.index)
            df_Worst.index = df_Worst.index.strftime('%Y-%m-%d')

            df_Issuance_Info.columns=df_Issuance_Info.iloc[7,:] # 칼럼 네이밍
            Issuers=df_Issuance_Info.iloc[9][min_redeemed_code] #발행사 정보
            Underlyings=list(df_Issuance_Info.iloc[24:28][min_redeemed_code]) #기초자산 정보
            Worst_info=[]
            Worst_info.append(min_redeemed_code)
            Worst_info.append(Issuers)
            Worst_info.extend(Underlyings) # 리스트 병합
            df_Worst_info=pd.DataFrame(data=Worst_info)
            df_Worst_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
            df_final_date.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=0, startcol=0, index=False, header=None)
            df_Worst_info.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=2,header=None)
            df_Worst.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=10)

            # Best Performer 분석
            NAVs = df_Daily_NAV.loc[df_Daily_NAV[max_redeemed_code] != 0, max_redeemed_code]
            df_Best=pd.DataFrame(NAVs)/10000
            df_Best.rename(columns={ max_redeemed_code:'ELS % NAV'},inplace=True)
            # 날짜 포맷 변경
            df_Best.index = pd.to_datetime(df_Best.index)
            df_Best.index = df_Best.index.strftime('%Y-%m-%d')

            Issuers=df_Issuance_Info.iloc[9][max_redeemed_code] #발행사 정보
            Underlyings=list(df_Issuance_Info.iloc[24:28][max_redeemed_code]) #기초자산 정보
            Best_info=[]
            Best_info.append(max_redeemed_code)
            Best_info.append(Issuers)
            Best_info.extend(Underlyings) # 리스트 병합
            df_Best_info=pd.DataFrame(data=Best_info)
            df_Best_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
            df_final_date.to_excel(writer, sheet_name='#9.Best-Performer', startrow=0, startcol=0, index=False, header=None)
            df_Best_info.to_excel(writer, sheet_name='#9.Best-Performer', startrow=2,header=None)
            df_Best.to_excel(writer, sheet_name='#9.Best-Performer', startrow=10)

        except KeyError:
            df_Issuance_Info.columns=df_Issuance_Info.iloc[7,:] # 칼럼 네이밍
            print("상환된 종목이 없어서 #5~#9번 윅쉬트의 내용은 생략합니다")

        #############################################################
        ############## #10번째 웍쉿: Outstanding 자료 분석 ########################
        #############################################################
        df_Alives=pa_return_for_alives(df_Daily_NAV,final_date) # 새로 작성한 함수 호출

        out1=df_Alives['연환산수익율']
        out_stats1=out1.describe().loc[['min','mean', '50%','max']]
        df_out_stats_1=pd.DataFrame(out_stats1)
        min_code=out1.idxmin()
        max_code=out1.idxmax()
        df_out_stats_1['해당 KR Code 값']=[min_code,np.nan,np.nan,max_code]
        df_stats_10=pd.DataFrame(out1)
        df_final_date.to_excel(writer, sheet_name='#10.살아있는 ELS 수익율 분포', startrow=0, startcol=0, index=False, header=None)
        df_out_stats_1.to_excel(writer,sheet_name='#10.살아있는 ELS 수익율 분포',startrow=2)
        df_stats_10.to_excel(writer,sheet_name='#10.살아있는 ELS 수익율 분포',startrow=10)

        df_Alives['NAV']=pd.to_numeric(df_Alives['NAV'], errors='coerce')
        out2=df_Alives['NAV']/10000
        out_stats2=out2.describe().loc[['min','mean', '50%','max']]
        df_out_stats_2=pd.DataFrame(out_stats2)
        min_code=out2.idxmin()
        max_code=out2.idxmax()
        df_out_stats_2['해당 KR Code 값']=[min_code,np.nan,np.nan,max_code]
        df_stats_10_0=pd.DataFrame(out2)
        df_final_date.to_excel(writer, sheet_name='#10.0 살아있는 ELS NAV 분포', startrow=0, startcol=0, index=False, header=None)
        df_out_stats_2.to_excel(writer,sheet_name='#10.0 살아있는 ELS NAV 분포',startrow=2)
        df_stats_10_0.to_excel(writer,sheet_name='#10.0 살아있는 ELS NAV 분포',startrow=10)

        #############################################################
        ############## #11번째 웍쉿 작성 ########################
        #############################################################
        # Worst Performer 분석
        NAVs = df_Daily_NAV.loc[df_Daily_NAV[min_code] != 0, min_code]
        df_Worst_alive=pd.DataFrame(NAVs)/10000
        df_Worst_alive.rename(columns={ min_code:'ELS % NAV'},inplace=True)
        # 날짜 포맷 변경
        df_Worst_alive.index = pd.to_datetime(df_Worst_alive.index)
        df_Worst_alive.index = df_Worst_alive.index.strftime('%Y-%m-%d')

        Issuers=df_Issuance_Info.iloc[9][min_code] #발행사 정보
        Underlyings=list(df_Issuance_Info.iloc[24:28][min_code]) #기초자산 정보
        Worst_alive_info=[]
        Worst_alive_info.append(min_code)
        Worst_alive_info.append(Issuers)
        Worst_alive_info.extend(Underlyings) # 리스트 병합
        df_Worst_alive_info=pd.DataFrame(data=Worst_alive_info)
        df_Worst_alive_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
        df_final_date.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=0, startcol=0, index=False, header=None)
        df_Worst_alive_info.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=2,header=None)
        df_Worst_alive.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=10)


        #############################################################
        ############## #12번째 웍쉿 작성 ########################
        #############################################################
        # Best Performer 분석
        NAVs = df_Daily_NAV.loc[df_Daily_NAV[max_code] != 0, max_code]
        df_alive_Best=pd.DataFrame(NAVs)/10000
        df_alive_Best.rename(columns={ max_code:'ELS % NAV'},inplace=True)
        # 날짜 포맷 변경
        df_alive_Best.index = pd.to_datetime(df_alive_Best.index)
        df_alive_Best.index = df_alive_Best.index.strftime('%Y-%m-%d')

        Issuers=df_Issuance_Info.iloc[9][max_code] #발행사 정보
        Underlyings=list(df_Issuance_Info.iloc[24:28][max_code]) #기초자산 정보
        Best_alive_info=[]
        Best_alive_info.append(max_code)
        Best_alive_info.append(Issuers)
        Best_alive_info.extend(Underlyings) # 리스트 병합
        df_Best_alive_info=pd.DataFrame(data=Best_alive_info)
        df_Best_alive_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
        df_final_date.to_excel(writer, sheet_name='#12.Best-Performer', startrow=0, startcol=0, index=False, header=None)
        df_Best_alive_info.to_excel(writer, sheet_name='#12.Best-Performer', startrow=2,header=None)
        df_alive_Best.to_excel(writer, sheet_name='#12.Best-Performer', startrow=10)

        #############################################################
        ######### #13번째 웍쉿 작성 ##############
        #############################################################
        # 기본정보들은 #3번째 웍쉿 작성 중에 이미 만들어져 있음
        # 엑셀 쉬트에 집어넣기
        df_underlyings.to_excel(writer, sheet_name='#13.Underlyings', startrow=10)
        df_out_stats_underlying.to_excel(writer, sheet_name='#13.Underlyings')


def pptout_colab(file,file_out):

    file_out_ppt= file_out

    import pandas as pd
    import numpy as np

    df=pd.read_excel(file,skiprows=32,usecols=None)
    df_ua,df_ua_summary_out=underlyings_for_ELS(file)

    df_Daily_NAV=df.iloc[2:,2:] # Daily NAVs 만을 발췌
    df_Daily_NAV=df_Daily_NAV.fillna(0) # NaN을 0으로 바꾸기
    df_Daily_NAV = df_Daily_NAV.apply(pd.to_numeric, errors='coerce') # 모든 열을 숫자로 변환

    # 연속된 0인 행 삭제
    remove_consecutive_zeros(df_Daily_NAV)

    # 일자를 인덱스 정보로 불러오고 포맷변경
    Biz_Dates=df.iloc[-len(df_Daily_NAV):,1]
    Biz_Dates=pd.to_datetime(Biz_Dates, format='%Y%m%d')


    # ELS 발행정보 정보 읽어오기
    df_Issuance_Info=pd.read_excel(file, nrows=35) # 처음 35행만 읽어오기
    Notional_Amount = df_Issuance_Info.iloc[12,2:] # 발행총액 정보를 읽어옴
    Notional_Amount = Notional_Amount.apply(int) # 숫자 데이터로 변환
    # Series 이름제거
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    KR_Code=df_Issuance_Info.iloc[7,2:] # 발행코드 정보를 읽어옴

    # 날짜를 인덱스로 설정하기
    df_Daily_NAV = df_Daily_NAV.set_index(Biz_Dates)
    df_Daily_NAV.index.name = 'Biz_Dates'

    df_Daily_NAV = df_Daily_NAV.rename(columns=KR_Code) #칼럼 이름 주기

    # 기초자산정보 계산
    df_ua_alives_summary_out=underlyings_for_ELS_alives(df_ua,df_Daily_NAV,Biz_Dates)

    # 발행 정보를 분석하기 위한 새로운 데이터프레임 만들기
    issued_date=df_Issuance_Info.iloc[13,2:] # 각 종목의 발행일자가 저장됨
    issued_date = pd.to_datetime(issued_date) # 날짜형식으로 변환
    # 인덱스를 초기화하여 시리즈 재설정
    issued_date = issued_date.reset_index(drop=True)
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    df_issued_summary=pd.DataFrame(data={'발행일':issued_date,'발행총액':Notional_Amount})
    df_issued_summary.index=KR_Code
    df_issued_summary.index.name='KR code'

    # 발행 총액을 곱하여 Market Cap 계산
    # 발행 총액 연산을 위해 numpy array 포맷으로 변환

    np_Notional_Amount=np.array(Notional_Amount)
    np_df_Daily_NAV=np.array(df_Daily_NAV)
    df_Daily_NAV_Market_Cap=pd.DataFrame(data=np_df_Daily_NAV*np_Notional_Amount,index=Biz_Dates,columns=KR_Code)/10000
    df_Daily_NAV_Market_Cap.index.name = 'Biz_Dates' # 인덱스 이름지정
    df_Daily_NAV_Market_Cap.columns.name = 'KR_Code' # 칼럼 이름 지정
    # 날짜별 시장가치의 총합임
    df_Daily_NAV_Market_Cap['날짜별발행잔액'] = df_Daily_NAV_Market_Cap.sum(axis=1)
    # 행에서 0이 아닌 종목들의 수를 새로운 칼럼으로 만들어주기
    # 첫 번째 열에 0이 아닌 데이터의 개수를 계산하여 새로운 열 추가
    df_Daily_NAV.insert(0, 'non_zero_count', df_Daily_NAV.astype(bool).sum(axis=1))

    df_Num_ELS = df_Daily_NAV.iloc[0:,0]
    Max_Num_ELS = df_Num_ELS.max()

    ##########################################
    ########### EW indexing
    ###########################################
    # KR코드에 해당한 열만 추출하여 각 행의 총합을 A칼럼으로 추가...전체NAV합계
    df_Daily_NAV['A'] = df_Daily_NAV.filter(regex='^KR').sum(axis=1) #

    # 신규발행 합계 열(B) 만들기...신규발행NAV합계
    df_Daily_NAV['B'] = df_Daily_NAV[df_Daily_NAV.shift(1).eq(0)].filter(regex='^KR').sum(axis=1)

    # C칼럼 만들기...기존발행NAV합계
    df_Daily_NAV['C']=df_Daily_NAV.A-df_Daily_NAV.B

    # 상환종목합계 만들기...상환종목NAV합계
    df_Daily_NAV['D'] = df_Daily_NAV[df_Daily_NAV.shift(-1).eq(0)].filter(regex='^KR').sum(axis=1)

    # F 칼럼 만들기...전체빼기상환종목NAV합계
    df_Daily_NAV['F']=df_Daily_NAV.A-df_Daily_NAV.D

    # E 칼럼 만들기
    # C칼럼과 F칼럼의 데이터에 자연로그 취하기
    df_Daily_NAV['C_log'] = np.log(df_Daily_NAV['C'])
    df_Daily_NAV['F_log_shifted'] = np.log(df_Daily_NAV['F'].shift(1))
    # E칼럼 계산하기
    df_Daily_NAV['E'] = df_Daily_NAV['C_log'] - df_Daily_NAV['F_log_shifted']
    # 불필요한 열 제거하기
    df_Daily_NAV = df_Daily_NAV.drop(['C_log', 'F_log_shifted'], axis=1)

    # G칼럼 만들기...EW Index 값
    # 첫 번째 행의 G값을 1로 설정
    df_Daily_NAV.at[df_Daily_NAV.index[0], 'G'] = 1
    # G칼럼 계산하기
    for i in range(1, len(df_Daily_NAV)):
        df_Daily_NAV.at[df_Daily_NAV.index[i], 'G'] = df_Daily_NAV.at[df_Daily_NAV.index[i - 1], 'G'] + df_Daily_NAV.at[df_Daily_NAV.index[i], 'E']

    # 평균 NAV 수익율 칼럼(H) 작성
    df_Daily_NAV['H']=(df_Daily_NAV['A']/df_Daily_NAV['non_zero_count']-10000)/10000

    ##########################################
    ########### Market cap indexing
    ###########################################
    df_Daily_NAV_Market_Cap['A'] = df_Daily_NAV_Market_Cap.filter(regex='^KR').sum(axis=1)

    # 신규발행 합계 열(B) 만들기
    df_Daily_NAV_Market_Cap['B'] = df_Daily_NAV_Market_Cap[df_Daily_NAV_Market_Cap.shift(1).eq(0)].filter(regex='^KR').sum(axis=1)

    # C칼럼 만들기
    df_Daily_NAV_Market_Cap['C']=df_Daily_NAV_Market_Cap.A-df_Daily_NAV_Market_Cap.B

    # 상환종목합계 만들기
    df_Daily_NAV_Market_Cap['D'] = df_Daily_NAV_Market_Cap[df_Daily_NAV_Market_Cap.shift(-1).eq(0)].filter(regex='^KR').sum(axis=1)

    # F 칼럼 만들기
    df_Daily_NAV_Market_Cap['F']=df_Daily_NAV_Market_Cap.A-df_Daily_NAV_Market_Cap.D

    ######################## E 칼럼 만들기 #############################
    # C칼럼과 F칼럼의 데이터에 자연로그 취하기
    df_Daily_NAV_Market_Cap['C_log'] = np.log(df_Daily_NAV_Market_Cap['C'])
    df_Daily_NAV_Market_Cap['F_log_shifted'] = np.log(df_Daily_NAV_Market_Cap['F'].shift(1))
    # E칼럼 계산하기
    df_Daily_NAV_Market_Cap['E'] = df_Daily_NAV_Market_Cap['C_log'] - df_Daily_NAV_Market_Cap['F_log_shifted']
    # 불필요한 열 제거하기
    df_Daily_NAV_Market_Cap = df_Daily_NAV_Market_Cap.drop(['C_log', 'F_log_shifted'], axis=1)

    ######################## G 칼럼 만들기 #############################
    # 첫 번째 행의 G값을 1로 설정
    df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[0], 'G'] = 1
    # G칼럼 계산하기
    for i in range(1, len(df_Daily_NAV_Market_Cap)):
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i], 'G'] = \
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i - 1], 'G'] +\
        df_Daily_NAV_Market_Cap.at[df_Daily_NAV_Market_Cap.index[i], 'E']

     ##########################################
     ########### 산 자 분석
     ###########################################

     # 인덱스에 함수 적용하여 새로운 열들 추가
    for index, row in df_Daily_NAV.iterrows():
        result,min_Ret_index,max_Ret_index = stats_for_alives(df_Daily_NAV,index)  # 인덱스에 함수 적용
        for column_name, value in result.items():
            df_Daily_NAV.at[index, f'Alive_{column_name}'] = value  # 새로운 열들 추가
        df_Daily_NAV.at[index, 'min_Return_KR_code'] = min_Ret_index
        df_Daily_NAV.at[index, 'min_Return_issued_date']=df_issued_summary.at[min_Ret_index,'발행일'].strftime('%Y-%m-%d')
        df_Daily_NAV.at[index, 'max_Return_KR_code'] = max_Ret_index
        df_Daily_NAV.at[index, 'max_Return_issued_date']=df_issued_summary.at[max_Ret_index,'발행일'].strftime('%Y-%m-%d')

    # monthly data 추출
    df_alive_stats=df_Daily_NAV.resample('ME').last().iloc[:,-12:]
    # 날짜 포맷 변경
    df_alive_stats.index = pd.to_datetime(df_alive_stats.index)
    df_alive_stats.index = df_alive_stats.index.strftime('%Y-%m-%d')

     ##########################################
     ########### 죽은 자 분석
     ###########################################

    # 매월 말일의 인덱스 선택
    monthly_end_index = df_Daily_NAV.resample('ME').last().index

    # 빈 데이터프레임 생성
    df_for_redeemed = pd.DataFrame(index=monthly_end_index)

    for date in monthly_end_index:
        date_str = date.strftime('%Y-%m-%d')  # 날짜를 문자열로 변환
        D,ABS,PA,pos_ret_abs,neg_ret_abs,pos_ret_pa,neg_ret_pa,min_duration,max_duration,min_pa_return,max_pa_return = stats_for_redeemed(df_Daily_NAV,date_str)
        if D is not None:
            for column_name, value in D.items():
                df_for_redeemed.at[date, f'Durations_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in ABS.items():
                df_for_redeemed.at[date, f'abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in PA.items():
                df_for_redeemed.at[date, f'p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in pos_ret_abs.items():
                df_for_redeemed.at[date, f'(+)abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in neg_ret_abs.items():
                df_for_redeemed.at[date, f'(-)abs_ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in pos_ret_pa.items():
                df_for_redeemed.at[date, f'(+)p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            for column_name, value in neg_ret_pa.items():
                df_for_redeemed.at[date, f'(-)p.a._ret_{column_name}'] = value  # 새로운 열들 추가
            df_for_redeemed.at[date, 'min_duration_KR_code'] = min_duration
            df_for_redeemed.at[date, 'min_duration_issued_date']=df_issued_summary.at[min_duration,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'max_duration_KR_code'] = max_duration
            df_for_redeemed.at[date, 'max_duration_issued_date']=df_issued_summary.at[max_duration,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'min_pareturn_KR_code'] = min_pa_return
            df_for_redeemed.at[date, 'min_pareturn_issued_date']=df_issued_summary.at[min_pa_return,'발행일'].strftime('%Y-%m-%d')
            df_for_redeemed.at[date, 'max_pareturn_KR_code'] = max_pa_return
            df_for_redeemed.at[date, 'max_pareturn_issued_date']=df_issued_summary.at[max_pa_return,'발행일'].strftime('%Y-%m-%d')

    # 날짜 포맷 변경
    df_for_redeemed.index = pd.to_datetime(df_for_redeemed.index)
    df_for_redeemed.index = df_for_redeemed.index.strftime('%Y-%m-%d')


     ##########################################
     ########### 특정 날짜에서 발행된 종목수, 발행금액 보기
     ###########################################

    # 발행 정보를 분석하기 위한 새로운 데이터프레임 만들기
    issued_date=df_Issuance_Info.iloc[13,2:]
    issued_date = pd.to_datetime(issued_date) # 날짜형식으로 변환
    # 인덱스를 초기화하여 시리즈 재설정
    issued_date = issued_date.reset_index(drop=True)
    Notional_Amount = Notional_Amount.reset_index(drop=True)
    df_issued_summary=pd.DataFrame(data={'발행일':issued_date,'발행총액':Notional_Amount})
    df_issued_summary.index=KR_Code
    df_issued_summary.index.name='KR code'

    # df_Daily_NAV의 날짜 인덱스를 기반으로 새로운 열 생성
    df_Daily_NAV[['발행된ELS종목수', '발행총액_합계']] = df_Daily_NAV.index.to_series().apply(
        lambda date: pd.Series(get_issue_amount(df_issued_summary, date)))
    df_Daily_NAV[['발행된ELS종목수', '발행총액_합계']]
    # 발행총액을 10억 단위로 변환
    df_Daily_NAV['발행총액(10억)'] = df_Daily_NAV['발행총액_합계'] / 1e+9

    ##########################################
    ########### 특정 날짜에서 상환된 종목수, 발행금액 보기
    ###########################################

    # df_Daily_NAV의 날짜 인덱스를 기반으로 새로운 열 생성
    # 날짜마다 상환되는 것을 계산하느라 시간 많이 걸림
    df_Daily_NAV[['상환된ELS종목수', '상환된발행액_합계(10억)']] = df_Daily_NAV.index.to_series().apply(
        lambda date: pd.Series(info_for_redeemed(df_Daily_NAV_Market_Cap,df_issued_summary,date)))
    df_Daily_NAV[['상환된ELS종목수', '상환된발행액_합계(10억)']]

    ##########################################
    ########### Sharpe Ratio
    ###########################################

    rf=0.05 # 금리 세팅

    # 매월 말일의 인덱스 선택
    monthly_end_index = df_Daily_NAV.resample('ME').last().index

    # 빈 데이터프레임 생성
    df_Sharpe_for_redeemed = pd.DataFrame(index=monthly_end_index)

    for date in monthly_end_index:
        date_str = date.strftime('%Y-%m-%d')  # 날짜를 문자열로 변환
        results=sharpe_ratio_for_redeemed(df_Daily_NAV,rf,date_str).describe()
        for column_name, value in results.items():
              df_Sharpe_for_redeemed.at[date, f'SharpeR_{column_name}'] = value  # 새로운 열들 추가


    ##########################################
    ########### PPT 자료 작성하기: Colab
    ###########################################
    from pandas_datareader import data as pdr
    import yfinance as yfin


    # Daily info 정리하기
    df_Daily_NAV_summary=df_Daily_NAV.iloc[:, [0] + list(range(-17, 0))] # 처음과 마지막 17개의 칼럼만 추출


    # 시장가치잔액(10억) 컬럼을 추가할 데이터프레임을 복사하여 변경
    df_Daily_NAV_summary = df_Daily_NAV_summary.copy()
    imsi=df_Daily_NAV_Market_Cap['날짜별발행잔액']/1e+9
    df_Daily_NAV_summary['시장가치잔액(10억)'] = imsi


    # 칼럼 위치 조정
    # 'non_zero_count' 칼럼을 삭제한 후, 맨 뒤에서 두 번째 위치에 다시 삽입
    cols = list(df_Daily_NAV_summary.columns)
    cols.remove('non_zero_count')  # non_zero_count 칼럼을 제외한 나머지 칼럼들의 순서를 정함
    cols.insert(-1, 'non_zero_count')  # non_zero_count 칼럼을 원하는 위치에 삽입
    df_Daily_NAV_summary = df_Daily_NAV_summary[cols]  # 새로운 칼럼 순서로 데이터프레임을 재구성

    # 중복칼럼 삭제
    df_Daily_NAV_summary.drop(columns=['발행총액_합계'],inplace=True)

    # Column Rename
    df_Daily_NAV_summary = df_Daily_NAV_summary.rename(columns={'non_zero_count': '잔존 ELS 종목수'})

    # 날짜 포맷 변경
    df_Daily_NAV_summary.index = pd.to_datetime(df_Daily_NAV_summary.index)
    df_Daily_NAV_summary.index = df_Daily_NAV_summary.index.strftime('%Y-%m-%d')
    df_daily_stats=df_Daily_NAV_summary.drop(columns=['Alive_25%','Alive_75%'])
    df_daily_stats['EW Index']=df_Daily_NAV['G']
    df_daily_stats['Market Cap Index']=df_Daily_NAV_Market_Cap['G']
    last_two_columns = df_daily_stats.iloc[:, -2:]  # 마지막 두 개의 칼럼 선택
    df_daily_stats.drop(df_daily_stats.columns[-2:], axis=1, inplace=True)  # 마지막 두 개의 칼럼 삭제
    df_daily_stats = pd.concat([last_two_columns, df_daily_stats], axis=1)  # 마지막 두 개의 칼럼을 맨 앞으로 이동
    last_six_columns = df_daily_stats.iloc[:, -6:]  # 마지막 여섯 개의 칼럼 선택
    df_daily_stats.drop(df_daily_stats.columns[-6:], axis=1, inplace=True)  # 마지막 여섯 개의 칼럼 삭제
    df_daily_stats = pd.concat([df_daily_stats.iloc[:, :2], last_six_columns, df_daily_stats.iloc[:, 2:]], axis=1)  # 칼럼 삽입

    # Monthly info 정리하기
    df_monthly_stats_for_redeemed=df_for_redeemed
    selected_columns = df_monthly_stats_for_redeemed.iloc[:, 22:26]
    df_monthly_stats_for_redeemed.drop(df_monthly_stats_for_redeemed.columns[22:26], axis=1, inplace=True)
    df_monthly_stats_for_redeemed = pd.concat([df_monthly_stats_for_redeemed.iloc[:, :4], selected_columns, df_monthly_stats_for_redeemed.iloc[:, 4:]], axis=1)
    selected_columns = df_monthly_stats_for_redeemed.iloc[:, -4:]
    df_monthly_stats_for_redeemed.drop(df_monthly_stats_for_redeemed.columns[-4:], axis=1, inplace=True)
    df_monthly_stats_for_redeemed = pd.concat([df_monthly_stats_for_redeemed.iloc[:, :11], selected_columns, df_monthly_stats_for_redeemed.iloc[:, 11:]], axis=1)
    df_monthly_stats_for_redeemed['SharpeR_mean']=df_Sharpe_for_redeemed['SharpeR_mean']
    df_monthly_stats_for_redeemed['SharpeR_std']=df_Sharpe_for_redeemed['SharpeR_std']


    df_ua_alives, df_ua_alives_summary_out,alived_codes=underlyings_for_ELS_alives(df_ua,df_Daily_NAV,Biz_Dates)

    with pd.ExcelWriter(file_out_ppt) as writer:

        final_date=df_daily_stats.index[-1]
        df_final_date = pd.DataFrame({'A':['기준일'],'B':[final_date]})


        #############################################################
        ############## #0.1 웍쉿 작성 #############################
        #############################################################

        df_final_date.to_excel(writer, sheet_name='#0.1 발행금액분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=df_ua_summary_out.sum().values[0]
        Issued_Notional=df_ua_summary_out.sum().values[2]
        df_ua_imsi = pd.DataFrame({'A':['총 종목수','총 발행총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.1 발행금액분석', startrow=1, startcol=0, index=False, header=None)
        df_ua_summary_out.to_excel(writer, sheet_name='#0.1 발행금액분석',startrow=7)

        #############################################################
        ############## #0.2 웍쉿 작성 #############################
        #############################################################

        df_final_date.to_excel(writer, sheet_name='#0.2 잔존금액분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=df_ua_alives_summary_out.sum().values[0]
        Issued_Notional=df_ua_alives_summary_out.sum().values[2]
        df_ua_imsi = pd.DataFrame({'A':['총 잔존 종목수','총 잔존 발행총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.2 잔존금액분석', startrow=1, startcol=0, index=False, header=None)
        df_ua_alives_summary_out.to_excel(writer, sheet_name='#0.2 잔존금액분석',startrow=7)

        #############################################################
        ############## #0.3웍쉿 작성: Worstoff 분석 #################
        #############################################################
        #  df_ua,df_ua_summary_out=underlyings_for_ELS(file) 을 본 함수 시작 부분에서 실행하였음
        df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes=worst_off_alives_analysis(file,df_Daily_NAV,Biz_Dates)
        worst_off_alives_summary_out,df_ua_worstoff_ratio_alives_printing_ver=worst_off_alives_summary(df_ua_alives, df_ua_alives_summary_out,df_ua_worstoff_alives,df_ua_worstoff_ratio_alives,alived_codes)
        df_final_date.to_excel(writer, sheet_name='#0.3 Worstoff분석', startrow=0, startcol=0, index=False, header=None)
        Issued_Num=len(alived_codes) # 살아있는 발행종목 수
        Issued_Notional=df_ua_alives_summary_out.sum().values[2] # 10억 기준임
        df_ua_imsi = pd.DataFrame({'A':['총 잔존종목수','총 잔존총액(10억원)'],'B':[Issued_Num,Issued_Notional]})
        df_ua_imsi.to_excel(writer, sheet_name='#0.3 Worstoff분석', startrow=1, startcol=0, index=False, header=None)
        worst_off_alives_summary_out.iloc[:, 4:].to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7) # 마지막 4개 칼럼 출력
        worst_off_alives_summary_out.iloc[:, :4].to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7,startcol=6) # 처음 4개 칼럼 출력
        df_ua_worstoff_ratio_alives_printing_ver.to_excel(writer, sheet_name='#0.3 Worstoff분석',startrow=7,startcol=12) # worstoff 기준가 출력 (기초자산별-KR코드별)


        #############################################################
        ################# #1번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_01=df_daily_stats[['발행된ELS종목수','발행총액(10억)']]
        df_daily_stats_01_summary=df_daily_stats_01.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_01_summary.to_excel(writer, sheet_name='#1. 발행종목수&금액')
        df_daily_stats_01.to_excel(writer, sheet_name='#1. 발행종목수&금액',startrow=10)

        #############################################################
        ################# #2번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_02=df_daily_stats[['EW Index','Market Cap Index']]
        df_daily_stats_02_summary=df_daily_stats_02.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_02_summary.to_excel(writer, sheet_name='#2. ELS Index')
        df_daily_stats_02.to_excel(writer, sheet_name='#2. ELS Index',startrow=10)

        #############################################################
        ################# #3번째 웍쉿 작성  ########################
        #############################################################
        import datetime
        # 조회날짜 설정
        start=df_daily_stats.index[0]
        date_str = final_date
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')  # 문자열을 datetime 객체로 변환합니다.
        date_obj_plus_one_day = date_obj + datetime.timedelta(days=1)  # 날짜에 하루를 더해줍니다.
        end=date_obj_plus_one_day.strftime('%Y-%m-%d')

        #yfin.pdr_override()
        tickers=['^KS200','^HSCE','^N225','^SPX','^STOXX50E','TSLA','AMD','NVDA','005930.KS','005380.KS']

        # 빈 데이터프레임 생성
        combined_data = pd.DataFrame()

        # 각 티커의 종가 데이터를 가져와서 결합
        for t in tickers:
            # 각 티커의 데이터 다운로드 및 'Close' 열 선택
            df = yfin.download(t, start=start, end=end,auto_adjust=False)[['Close']]
            
            # 타임존 제거
            df.index = df.index.tz_localize(None)
            
            # 각 티커의 데이터에 이름을 지정하여 'Close' 열만 남긴 상태로 결합
            df.columns = [t]  # 열 이름을 티커로 지정
            combined_data = pd.concat([combined_data, df], axis=1)  # 열 기준으로 결합
        df_underlyings=combined_data

        # 없는 데이터 채우기
        #df_underlyings = df_underlyings.fillna(method='ffill') # 빈 데이터는 앞데이터로
        #df_underlyings = df_underlyings.fillna(method='bfill') # 앞에도 없으면 뒤데이터로
        df_underlyings = df_underlyings.ffill() # 빈 데이터는 앞데이터로
        df_underlyings = df_underlyings.bfill() # 앞에도 없으면 뒤데이터로

        # 날짜 포맷 변경
        df_underlyings.index = pd.to_datetime(df_underlyings.index)
        df_underlyings.index = df_underlyings.index.strftime('%Y-%m-%d')

        # 통계량 작성
        out_stats_underlying=df_underlyings.describe().loc[['min','mean', '50%','max']]
        df_out_stats_underlying=pd.DataFrame(out_stats_underlying)
        df_daily_stats_03=df_daily_stats[['EW Index']]
        df_daily_stats_03_summary=df_daily_stats_03.describe().loc[['min','mean', '50%','max']]

        # 데이터 타입 확인 및 변환
        df_daily_stats_03.index = df_daily_stats_03.index.astype(str)
        df_underlyings.index = df_underlyings.index.astype(str)

        # 인덱스 정렬
        df_daily_stats_03 = df_daily_stats_03.sort_index()
        df_underlyings = df_underlyings.sort_index()

        # 인덱스 이름 확인 및 변경
        df_daily_stats_03 = df_daily_stats_03.rename_axis('date')
        df_underlyings = df_underlyings.rename_axis('date')

        # 각 주가를 정규화시키기
        df_underlyings=df_underlyings.iloc[:, :5] #첫 5개의 칼럼만 발췌
        df_normalized = df_underlyings / df_underlyings.iloc[0,:]

        # 정규화된 주가의 통계량 구하기
        out_stats_underlying=df_normalized.describe().loc[['min','mean', '50%','max']]
        df_out_stats_underlying=pd.DataFrame(out_stats_underlying)

        # 통계량 병합
        df_daily_stats_03_summary=pd.concat([df_daily_stats_03_summary, df_out_stats_underlying], axis=1, join='inner')
        df_daily_stats_03_summary.to_excel(writer, sheet_name='#3. ELS&GEI')

        # 병합
        merged_df = df_daily_stats_03.merge(df_normalized, left_index=True, right_index=True, how='inner')
        merged_df.to_excel(writer, sheet_name='#3. ELS&GEI',startrow=10)

        #############################################################
        ################# #4번째 웍쉿 작성  ########################
        #############################################################

        df_daily_stats_04=df_daily_stats[['EW Index','잔존 ELS 종목수']]
        df_daily_stats_04_summary=df_daily_stats_04.describe().loc[['min','mean', '50%','max']]
        df_daily_stats_04_summary.to_excel(writer, sheet_name='#4. EW&해당ELS')
        df_daily_stats_04.to_excel(writer, sheet_name='#4. EW&해당ELS',startrow=10)

        #############################################################
        ################# #5~9번째 웍쉿 작성  ########################
        #############################################################
        # 데이터프레임 생성
        total_issued=df_daily_stats_01_summary.iloc[3,0]
        df_t_issued = pd.DataFrame({'A':['발행된ELS종목수'],'B':[total_issued]})
        df_t_issued.to_excel(writer, sheet_name='#5.상환비율', startrow=0, startcol=1, index=False, header=None)

        # try-except 블록을 사용하여 에러 발생시 코드를 스킵
        try:
            df_daily_stats_05 = df_monthly_stats_for_redeemed[['Durations_count']]
            #df_daily_stats_05.rename(columns={'Durations_count': '조기/만기상환갯수'}, inplace=True)
            #df_daily_stats_05['조기/만기상환비율'] = df_daily_stats_05['조기/만기상환갯수'] / total_issued
            df_daily_stats_05 = df_daily_stats_05.rename(columns={'Durations_count': '조기/만기상환갯수'}).copy()
            df_daily_stats_05.loc[:, '조기/만기상환비율'] = df_daily_stats_05['조기/만기상환갯수'] / total_issued
            df_daily_stats_05 = df_daily_stats_05.loc[:, ['조기/만기상환비율', '조기/만기상환갯수']]
            df_daily_stats_05.to_excel('output.xlsx', sheet_name='#5.상환비율', startrow=10)

            df_daily_stats_06=df_daily_stats_05['조기/만기상환비율']
            df_daily_stats_06 = pd.concat([df_daily_stats_06, df_monthly_stats_for_redeemed['p.a._ret_mean']], axis=1)
            df_daily_stats_06.rename(columns={'p.a._ret_mean':'평균 연환산 수익율'},inplace=True)
            df_t_issued.to_excel(writer, sheet_name='#6.상환비율&연환산수익율', startrow=0, startcol=1, index=False, header=None)
            df_daily_stats_06.to_excel(writer, sheet_name='#6.상환비율&연환산수익율',startrow=10)

            df_daily_stats_06_01 =pd.concat([df_daily_stats_06, df_monthly_stats_for_redeemed[['Durations_mean','(+)abs_ret_count']]], axis=1)
            df_daily_stats_06_01['+상환비율']=df_daily_stats_06_01['(+)abs_ret_count']/total_issued
            df_daily_stats_06_01.drop(columns=['(+)abs_ret_count'],inplace=True)
            df_daily_stats_06_01 =pd.concat([df_daily_stats_06_01, df_monthly_stats_for_redeemed[['min_pareturn_KR_code','max_pareturn_KR_code']]], axis=1)
            df_t_issued.to_excel(writer, sheet_name='#6.참고', startrow=0, startcol=1, index=False, header=None)
            df_daily_stats_06_01.to_excel(writer, sheet_name='#6.참고',startrow=10)

            ############## 상환된 자료 분석 #############################
            # 데이터의 마지막 인덱 날짜를 찾기

            out=hist_for_redeemded(df_Daily_NAV,final_date)
            out_stats=out.describe().loc[['min','mean', '50%','max']]
            df_out_stats=pd.DataFrame(out_stats)
            df_out_stats.rename(columns={'p.a.return':'연환산 수익율'},inplace=True)
            min_redeemed_code=out.idxmin()
            max_redeemed_code=out.idxmax()
            df_out_stats['해당 KR Code 값']=[min_redeemed_code,np.nan,np.nan,max_redeemed_code]
            df_stats_07=pd.DataFrame(out)
            df_stats_07.rename(columns={'p.a.return':'연환산 수익율'},inplace=True)

            df_final_date.to_excel(writer, sheet_name='#7.상환완료된 ELS 연환산수익율 분포', startrow=0, startcol=0, index=False, header=None)
            df_out_stats.to_excel(writer,sheet_name='#7.상환완료된 ELS 연환산수익율 분포',startrow=2)
            df_stats_07.to_excel(writer,sheet_name='#7.상환완료된 ELS 연환산수익율 분포',startrow=10)
            
            # #7 sheet 상환개수 추가
            num_rows = df_stats_07.shape[0]
            df_redeemed_count = pd.DataFrame({'A':['상환완료된 ELS 개수'],'B':[num_rows]})
            df_redeemed_count.to_excel(writer, sheet_name='#7.상환완료된 ELS 연환산수익율 분포', startrow=1, startcol=0, index=False, header=None)

            # Worst Performer 분석
            NAVs = df_Daily_NAV.loc[df_Daily_NAV[min_redeemed_code] != 0, min_redeemed_code]
            df_Worst=pd.DataFrame(NAVs)/10000
            df_Worst.rename(columns={ min_redeemed_code:'ELS % NAV'},inplace=True)
            # 날짜 포맷 변경
            df_Worst.index = pd.to_datetime(df_Worst.index)
            df_Worst.index = df_Worst.index.strftime('%Y-%m-%d')

            df_Issuance_Info.columns=df_Issuance_Info.iloc[7,:] # 칼럼 네이밍
            Issuers=df_Issuance_Info.iloc[9][min_redeemed_code] #발행사 정보
            Underlyings=list(df_Issuance_Info.iloc[24:28][min_redeemed_code]) #기초자산 정보
            Worst_info=[]
            Worst_info.append(min_redeemed_code)
            Worst_info.append(Issuers)
            Worst_info.extend(Underlyings) # 리스트 병합
            df_Worst_info=pd.DataFrame(data=Worst_info)
            df_Worst_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
            df_final_date.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=0, startcol=0, index=False, header=None)
            df_Worst_info.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=2,header=None)
            df_Worst.to_excel(writer, sheet_name='#8.Worst-Performer', startrow=10)

            # Best Performer 분석
            NAVs = df_Daily_NAV.loc[df_Daily_NAV[max_redeemed_code] != 0, max_redeemed_code]
            df_Best=pd.DataFrame(NAVs)/10000
            df_Best.rename(columns={ max_redeemed_code:'ELS % NAV'},inplace=True)
            # 날짜 포맷 변경
            df_Best.index = pd.to_datetime(df_Best.index)
            df_Best.index = df_Best.index.strftime('%Y-%m-%d')

            Issuers=df_Issuance_Info.iloc[9][max_redeemed_code] #발행사 정보
            Underlyings=list(df_Issuance_Info.iloc[24:28][max_redeemed_code]) #기초자산 정보
            Best_info=[]
            Best_info.append(max_redeemed_code)
            Best_info.append(Issuers)
            Best_info.extend(Underlyings) # 리스트 병합
            df_Best_info=pd.DataFrame(data=Best_info)
            df_Best_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
            df_final_date.to_excel(writer, sheet_name='#9.Best-Performer', startrow=0, startcol=0, index=False, header=None)
            df_Best_info.to_excel(writer, sheet_name='#9.Best-Performer', startrow=2,header=None)
            df_Best.to_excel(writer, sheet_name='#9.Best-Performer', startrow=10)

        except KeyError:
            df_Issuance_Info.columns=df_Issuance_Info.iloc[7,:] # 칼럼 네이밍
            print("상환된 종목이 없어서 #5~#9번 윅쉬트의 내용은 생략합니다")

        #############################################################
        ############## #10번째 웍쉿: Outstanding 자료 분석 ########################
        #############################################################
        df_Alives=pa_return_for_alives(df_Daily_NAV,final_date) # 새로 작성한 함수 호출

        out1=df_Alives['연환산수익율']
        out_stats1=out1.describe().loc[['min','mean', '50%','max']]
        df_out_stats_1=pd.DataFrame(out_stats1)
        min_code=out1.idxmin()
        max_code=out1.idxmax()
        df_out_stats_1['해당 KR Code 값']=[min_code,np.nan,np.nan,max_code]
        df_stats_10=pd.DataFrame(out1)
        df_final_date.to_excel(writer, sheet_name='#10.살아있는 ELS 수익율 분포', startrow=0, startcol=0, index=False, header=None)
        df_out_stats_1.to_excel(writer,sheet_name='#10.살아있는 ELS 수익율 분포',startrow=2)
        df_stats_10.to_excel(writer,sheet_name='#10.살아있는 ELS 수익율 분포',startrow=10)

        df_Alives['NAV']=pd.to_numeric(df_Alives['NAV'], errors='coerce')
        out2=df_Alives['NAV']/10000
        out_stats2=out2.describe().loc[['min','mean', '50%','max']]
        df_out_stats_2=pd.DataFrame(out_stats2)
        min_code=out2.idxmin()
        max_code=out2.idxmax()
        df_out_stats_2['해당 KR Code 값']=[min_code,np.nan,np.nan,max_code]
        df_stats_10_0=pd.DataFrame(out2)
        df_final_date.to_excel(writer, sheet_name='#10.0 살아있는 ELS NAV 분포', startrow=0, startcol=0, index=False, header=None)
        df_out_stats_2.to_excel(writer,sheet_name='#10.0 살아있는 ELS NAV 분포',startrow=2)
        df_stats_10_0.to_excel(writer,sheet_name='#10.0 살아있는 ELS NAV 분포',startrow=10)

        #############################################################
        ############## #11번째 웍쉿 작성 ########################
        #############################################################
        # Worst Performer 분석
        NAVs = df_Daily_NAV.loc[df_Daily_NAV[min_code] != 0, min_code]
        df_Worst_alive=pd.DataFrame(NAVs)/10000
        df_Worst_alive.rename(columns={ min_code:'ELS % NAV'},inplace=True)
        # 날짜 포맷 변경
        df_Worst_alive.index = pd.to_datetime(df_Worst_alive.index)
        df_Worst_alive.index = df_Worst_alive.index.strftime('%Y-%m-%d')

        Issuers=df_Issuance_Info.iloc[9][min_code] #발행사 정보
        Underlyings=list(df_Issuance_Info.iloc[24:28][min_code]) #기초자산 정보
        Worst_alive_info=[]
        Worst_alive_info.append(min_code)
        Worst_alive_info.append(Issuers)
        Worst_alive_info.extend(Underlyings) # 리스트 병합
        df_Worst_alive_info=pd.DataFrame(data=Worst_alive_info)
        df_Worst_alive_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
        df_final_date.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=0, startcol=0, index=False, header=None)
        df_Worst_alive_info.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=2,header=None)
        df_Worst_alive.to_excel(writer, sheet_name='#11.Worst-Performer', startrow=10)


        #############################################################
        ############## #12번째 웍쉿 작성 ########################
        #############################################################
        # Best Performer 분석
        NAVs = df_Daily_NAV.loc[df_Daily_NAV[max_code] != 0, max_code]
        df_alive_Best=pd.DataFrame(NAVs)/10000
        df_alive_Best.rename(columns={ max_code:'ELS % NAV'},inplace=True)
        # 날짜 포맷 변경
        df_alive_Best.index = pd.to_datetime(df_alive_Best.index)
        df_alive_Best.index = df_alive_Best.index.strftime('%Y-%m-%d')

        Issuers=df_Issuance_Info.iloc[9][max_code] #발행사 정보
        Underlyings=list(df_Issuance_Info.iloc[24:28][max_code]) #기초자산 정보
        Best_alive_info=[]
        Best_alive_info.append(max_code)
        Best_alive_info.append(Issuers)
        Best_alive_info.extend(Underlyings) # 리스트 병합
        df_Best_alive_info=pd.DataFrame(data=Best_alive_info)
        df_Best_alive_info.index=['KR Code','발행증권사','기초자산1','기초자산2','기초자산3','기초자산4']
        df_final_date.to_excel(writer, sheet_name='#12.Best-Performer', startrow=0, startcol=0, index=False, header=None)
        df_Best_alive_info.to_excel(writer, sheet_name='#12.Best-Performer', startrow=2,header=None)
        df_alive_Best.to_excel(writer, sheet_name='#12.Best-Performer', startrow=10)

        #############################################################
        ######### #13번째 웍쉿 작성 ##############
        #############################################################
        # 기본정보들은 #3번째 웍쉿 작성 중에 이미 만들어져 있음
        # 엑셀 쉬트에 집어넣기
        df_underlyings.to_excel(writer, sheet_name='#13.Underlyings', startrow=10)
        df_out_stats_underlying.to_excel(writer, sheet_name='#13.Underlyings')