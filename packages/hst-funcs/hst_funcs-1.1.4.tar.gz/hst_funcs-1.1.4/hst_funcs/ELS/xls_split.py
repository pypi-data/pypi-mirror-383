# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 14:05:38 2025

@author: S.T.Hwang
"""

def splitter(file_path,output_dir):
    # 엑셀파일 생성
    import pandas as pd
    import numpy as np
    import os
    
  
    # 폴더가 존재하지 않으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df = pd.read_excel(file_path, header=None)  # 헤더 없이 불러오기
    
    # 12번째 행(인덱스 11)에서 유니크한 값 찾기
    saler = df.iloc[11, 3:].dropna().to_numpy()  # NaN 제거 후 NumPy 배열 변환
    S_name, _ = np.unique(saler, return_counts=True)  # 고유한 값 추출
    
    # 각 S_name 값에 대해 해당 컬럼만 유지하고 저장
    for name in S_name:
        # 해당 S_name이 있는 컬럼 찾기
        selected_cols = [col for col in df.columns if df.iloc[11, col] == name]
        
        # 해당 컬럼만 포함하는 새로운 데이터프레임 생성 (A열~C열은 항상 유지)
        filtered_df = df.iloc[:, [0, 1, 2] + selected_cols]  # A, B, C 컬럼 유지
    
        # 저장할 파일 경로 설정
        output_file = os.path.join(output_dir, f"{name}_filtered.xlsx")
        
        # 엑셀 파일 저장
        filtered_df.to_excel(output_file, index=False, header=False)
    
        print(f"파일 저장 완료: {output_file}")
    
    print("✅ 모든 파일이 성공적으로 생성되었습니다!")