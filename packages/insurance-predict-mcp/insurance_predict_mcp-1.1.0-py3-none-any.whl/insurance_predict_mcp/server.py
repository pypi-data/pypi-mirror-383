"""
LightGBM Insurance Premium Prediction MCP Server

이 서버는 보험료 예측 모델을 MCP 프로토콜을 통해 노출합니다.
"""

from fastmcp import FastMCP
import joblib
import numpy as np
from pathlib import Path
from typing import Optional, Annotated

# FastMCP 서버 생성
mcp = FastMCP("Insurance Premium Predictor 🏥")

# 모델 로드 (서버 시작 시 1회만 수행)
# 패키지 내의 모델 파일 경로 찾기
_package_dir = Path(__file__).parent
_model_path = _package_dir / "models" / "lightgbm.pkl"

print(f"모델을 로드합니다... ({_model_path})")
model = joblib.load(_model_path)
feature_names = model.feature_name_
print(f"모델 로드 완료! (특성 개수: {model.n_features_})")

# 피처 경계값 및 기본값 정의 (모델 시그니처 기반)
FEATURE_BOUNDS = {
    'age': {
        'min': 19,
        'max': 65,
        'median': 37,
        'description': '가입자 나이 (세)',
        'example': 37
    },
    'annual_income': {
        'min': 0,
        'max': 149997,
        'median': 32000,
        'description': '연간 소득 (달러)',
        'example': 50000
    },
    'number_of_dependents': {
        'min': 0,
        'max': 5,
        'median': 2,
        'description': '부양 가족 수',
        'example': 2
    },
    'health_score': {
        'min': 0.04,
        'max': 93.88,
        'median': 26.4,
        'description': '건강 점수 (0-100)',
        'example': 26.4
    },
    'previous_claims': {
        'min': 0,
        'max': 9,
        'median': 1,
        'description': '과거 보험금 청구 횟수',
        'example': 1
    },
    'vehicle_age': {
        'min': 0,
        'max': 17,
        'median': 10,
        'description': '차량 연식 (년)',
        'example': 5
    },
    'credit_score': {
        'min': 300,
        'max': 849,
        'median': 595,
        'description': '신용 점수 (300-850)',
        'example': 650
    },
    'insurance_duration': {
        'min': 0,
        'max': 10,
        'median': 3,
        'description': '보험 가입 기간 (년)',
        'example': 3
    }
}


def fill_missing_values(features: dict) -> dict:
    """
    누락된 피처 값을 중앙값(median)으로 채웁니다.
    
    Args:
        features: 입력 피처 딕셔너리 (None 값 포함 가능)
    
    Returns:
        중앙값으로 채워진 피처 딕셔너리
    """
    filled_features = {}
    for feature_name, value in features.items():
        if feature_name in FEATURE_BOUNDS:
            if value is None:
                # None인 경우 중앙값(median)으로 대체
                filled_features[feature_name] = FEATURE_BOUNDS[feature_name]['median']
            else:
                filled_features[feature_name] = value
        else:
            filled_features[feature_name] = value
    
    return filled_features


def validate_input_features(features: dict) -> tuple[bool, Optional[str]]:
    """
    입력 피처의 유효성을 검증합니다.
    
    Args:
        features: 검증할 피처 딕셔너리
    
    Returns:
        (유효성 여부, 에러 메시지)
    """
    for feature_name, value in features.items():
        if feature_name not in FEATURE_BOUNDS:
            continue
        
        # None 값은 검증 스킵 (fill_missing_values에서 처리됨)
        if value is None:
            continue
        
        bounds = FEATURE_BOUNDS[feature_name]
        min_val = bounds['min']
        max_val = bounds['max']
        desc = bounds['description']
        
        if value < min_val or value > max_val:
            return False, (
                f"'{feature_name}' ({desc})의 값이 유효 범위를 벗어났습니다. "
                f"입력값: {value}, 유효 범위: [{min_val}, {max_val}]"
            )
    
    return True, None


def trace_tree_path(tree_dict, leaf_idx, feature_names_list, x_sample):
    """
    특정 트리 내에서 leaf_idx까지의 경로를 추적합니다.
    
    Args:
        tree_dict: 트리 구조 딕셔너리
        leaf_idx: 목표 리프 인덱스
        feature_names_list: 피처 이름 리스트
        x_sample: 입력 샘플 (1D array)
    
    Returns:
        경로 조건 리스트
    """
    path = []
    
    def recurse(node, conditions):
        if "leaf_index" in node:  # 리프에 도달
            if node["leaf_index"] == leaf_idx:
                path.extend(conditions)
            return
        
        feature_idx = node["split_feature"]
        threshold = node["threshold"]
        feature_name = feature_names_list[feature_idx]
        value = x_sample[feature_idx]
        
        # 왼쪽/오른쪽 노드 선택
        if value <= threshold:
            recurse(node["left_child"], conditions + 
                    [{"feature": feature_name, "value": value, 
                      "threshold": threshold, "direction": "left",
                      "condition": f"{feature_name}({value:.2f}) ≤ {threshold:.2f}"}])
        else:
            recurse(node["right_child"], conditions + 
                    [{"feature": feature_name, "value": value, 
                      "threshold": threshold, "direction": "right",
                      "condition": f"{feature_name}({value:.2f}) > {threshold:.2f}"}])
    
    recurse(tree_dict["tree_structure"], [])
    return path


def generate_prediction_explanation(X, num_trees_to_explain=5):
    """
    예측에 대한 설명을 생성합니다.
    
    Args:
        X: 입력 numpy 배열
        num_trees_to_explain: 설명할 트리 개수 (기본: 5)
    
    Returns:
        설명 딕셔너리
    """
    # 각 트리에서 도달한 리프 인덱스 가져오기
    leaf_indices = model.predict(X, pred_leaf=True)[0]
    
    # 모델 구조 덤프
    dump = model.booster_.dump_model()
    feature_names_list = model.booster_.feature_name()
    
    # 각 트리의 경로 추적
    tree_explanations = []
    for tree_id in range(min(num_trees_to_explain, len(leaf_indices))):
        leaf_id = leaf_indices[tree_id]
        tree = dump["tree_info"][tree_id]
        path = trace_tree_path(tree, leaf_id, feature_names_list, X[0])
        
        tree_explanations.append({
            "tree_id": tree_id,
            "leaf_index": int(leaf_id),
            "path": path,
            "path_description": " → ".join([step["condition"] for step in path])
        })
    
    # 주요 피처 추출 (경로에 자주 등장하는 피처)
    feature_importance = {}
    for tree_exp in tree_explanations:
        for step in tree_exp["path"]:
            feature = step["feature"]
            feature_importance[feature] = feature_importance.get(feature, 0) + 1
    
    # 중요도 순으로 정렬
    sorted_features = sorted(feature_importance.items(), 
                            key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "tree_paths": tree_explanations,
        "key_features": [{"feature": f, "usage_count": c} for f, c in sorted_features],
        "total_trees": len(leaf_indices),
        "explained_trees": len(tree_explanations)
    }


def _predict_insurance_premium_impl(
    age: Optional[float],
    annual_income: Optional[float],
    number_of_dependents: Optional[float],
    health_score: Optional[float],
    previous_claims: Optional[float],
    vehicle_age: Optional[float],
    credit_score: Optional[float],
    insurance_duration: Optional[float],
) -> dict:
    """
    보험료를 예측합니다.
    
    Args:
        age: 나이 (세) - 범위: [19, 65], 기본값: 37 (중앙값)
        annual_income: 연간 소득 (달러) - 범위: [0, 149997], 기본값: 32000 (중앙값)
        number_of_dependents: 부양 가족 수 - 범위: [0, 5], 기본값: 2 (중앙값)
        health_score: 건강 점수 - 범위: [0.04, 93.88], 기본값: 26.4 (중앙값)
        previous_claims: 이전 청구 건수 - 범위: [0, 9], 기본값: 1 (중앙값)
        vehicle_age: 차량 연식 (년) - 범위: [0, 17], 기본값: 10 (중앙값)
        credit_score: 신용 점수 - 범위: [300, 849], 기본값: 595 (중앙값)
        insurance_duration: 보험 기간 (년) - 범위: [0, 10], 기본값: 3 (중앙값)
    
    Returns:
        예측된 보험료와 입력 정보를 포함한 딕셔너리
    
    Raises:
        ValueError: 입력값이 유효 범위를 벗어난 경우
    """
    # 입력된 기본 특성들
    test_data = {
        'age': age,
        'annual_income': annual_income,
        'number_of_dependents': number_of_dependents,
        'health_score': health_score,
        'previous_claims': previous_claims,
        'vehicle_age': vehicle_age,
        'credit_score': credit_score,
        'insurance_duration': insurance_duration,
    }
    
    # 입력 피처 검증 (None 값은 검증하지 않음)
    is_valid, error_message = validate_input_features(test_data)
    if not is_valid:
        raise ValueError(error_message)
    
    # None 값을 중앙값으로 채우기
    test_data = fill_missing_values(test_data)
    
    # 모든 특성을 포함하는 딕셔너리 생성 (누락된 특성은 중앙값으로 초기화)
    input_dict = {}
    for feature in feature_names:
        if feature in test_data:
            input_dict[feature] = test_data[feature]
        else:
            # 모델의 다른 피처들은 중앙값으로 초기화 (있으면 사용, 없으면 0)
            if feature in FEATURE_BOUNDS:
                input_dict[feature] = FEATURE_BOUNDS[feature]['median']
            else:
                input_dict[feature] = 0.0
    
    # 특성 순서를 모델이 기대하는 순서대로 정렬하여 numpy 배열 생성
    X = np.array([[input_dict[feature] for feature in feature_names]])
    
    # 예측 수행
    prediction = model.predict(X)[0]
    
    # 예측 설명 생성
    explanation = generate_prediction_explanation(X, num_trees_to_explain=5)
    
    return {
        "predicted_premium": round(float(prediction), 2),
        "input_data": test_data,
        "message": f"예측된 보험료는 ${prediction:,.2f} 입니다.",
        "explanation": explanation
    }


@mcp.tool()
def predict_insurance_premium(
    age: Annotated[
        Optional[float], 
        "가입자의 나이 (세). 유효 범위: 19-65세. 미입력 시 중앙값 37세 사용. 예: 30"
    ] = None,
    annual_income: Annotated[
        Optional[float], 
        "연간 소득 (달러). 유효 범위: 0-149,997. 미입력 시 중앙값 $32,000 사용. 예: 50000"
    ] = None,
    number_of_dependents: Annotated[
        Optional[float], 
        "부양 가족 수. 유효 범위: 0-5명. 미입력 시 중앙값 2명 사용. 예: 2"
    ] = None,
    health_score: Annotated[
        Optional[float], 
        "건강 점수 (0-100). 유효 범위: 0.04-93.88. 미입력 시 중앙값 26.4 사용. 예: 25.5"
    ] = None,
    previous_claims: Annotated[
        Optional[float], 
        "과거 보험금 청구 횟수. 유효 범위: 0-9회. 미입력 시 중앙값 1회 사용. 예: 1"
    ] = None,
    vehicle_age: Annotated[
        Optional[float], 
        "차량 연식 (년). 유효 범위: 0-17년. 미입력 시 중앙값 10년 사용. 예: 5"
    ] = None,
    credit_score: Annotated[
        Optional[float], 
        "신용 점수. 유효 범위: 300-849. 미입력 시 중앙값 595 사용. 예: 650"
    ] = None,
    insurance_duration: Annotated[
        Optional[float], 
        "보험 가입 기간 (년). 유효 범위: 0-10년. 미입력 시 중앙값 3년 사용. 예: 3"
    ] = None,
) -> dict:
    """
    보험료를 예측합니다. 모든 파라미터는 선택적(Optional)이며, 미입력 시 중앙값으로 자동 대체됩니다.
    
    Args:
        age: 가입자 나이 (세) - 범위: [19, 65], 기본: 37
        annual_income: 연간 소득 (달러) - 범위: [0, 149997], 기본: 32000
        number_of_dependents: 부양 가족 수 - 범위: [0, 5], 기본: 2
        health_score: 건강 점수 - 범위: [0.04, 93.88], 기본: 26.4
        previous_claims: 과거 청구 횟수 - 범위: [0, 9], 기본: 1
        vehicle_age: 차량 연식 (년) - 범위: [0, 17], 기본: 10
        credit_score: 신용 점수 - 범위: [300, 849], 기본: 595
        insurance_duration: 보험 기간 (년) - 범위: [0, 10], 기본: 3
    
    Returns:
        예측된 보험료와 입력 정보를 포함한 딕셔너리
        - predicted_premium: 예측된 보험료 (달러)
        - input_data: 사용된 입력 데이터 (중앙값으로 채워진 값 포함)
        - message: 사람이 읽을 수 있는 결과 메시지
        - explanation: 예측 설명 (디시젼 트리 경로 분석)
          - tree_paths: 각 트리의 경로 정보
          - key_features: 예측에 중요한 피처 목록
          - total_trees: 전체 트리 개수
          - explained_trees: 설명에 포함된 트리 개수
    
    Raises:
        ValueError: 입력값이 유효 범위를 벗어난 경우
    
    Examples:
        # 모든 값 제공
        predict_insurance_premium(age=30, annual_income=50000, ...)
        
        # 일부 값만 제공 (나머지는 중앙값 사용)
        predict_insurance_premium(age=35, credit_score=700)
        
        # 값을 제공하지 않음 (모두 중앙값 사용)
        predict_insurance_premium()
    """
    return _predict_insurance_premium_impl(
        age=age,
        annual_income=annual_income,
        number_of_dependents=number_of_dependents,
        health_score=health_score,
        previous_claims=previous_claims,
        vehicle_age=vehicle_age,
        credit_score=credit_score,
        insurance_duration=insurance_duration
    )


def _get_model_info_impl() -> dict:
    """
    모델의 정보를 반환합니다.
    
    Returns:
        모델 특성 개수, 특성 이름 목록, 입력 범위 정보
    """
    return {
        "n_features": model.n_features_,
        "feature_names": feature_names,
        "model_type": str(type(model).__name__),
        "required_input_features": [
            "age", "annual_income", "number_of_dependents", 
            "health_score", "previous_claims", "vehicle_age",
            "credit_score", "insurance_duration"
        ],
        "feature_bounds": FEATURE_BOUNDS
    }


@mcp.tool()
def get_model_info() -> dict:
    """
    모델의 정보를 반환합니다.
    
    Returns:
        모델 특성 개수, 특성 이름 목록, 각 피처의 유효 범위 정보를 포함한 딕셔너리
    """
    return _get_model_info_impl()


@mcp.tool()
def get_feature_bounds() -> dict:
    """
    각 입력 피처의 유효 범위를 반환합니다.
    
    Returns:
        각 피처별 최소값, 최대값, 설명을 포함한 딕셔너리
    """
    return {
        "feature_bounds": FEATURE_BOUNDS,
        "description": "각 피처의 최소값(min), 최대값(max), 설명(description)을 제공합니다."
    }


@mcp.prompt()
def explain_insurance_prediction(prediction_result: str) -> str:
    """
    보험료 예측 결과를 자연어로 설명하는 방법을 안내합니다.
    
    이 프롬프트는 predict_insurance_premium의 결과를 사람이 이해하기 쉬운 
    자연어 설명으로 변환하는 방법을 제시합니다.
    
    Args:
        prediction_result: predict_insurance_premium 함수의 JSON 결과
    
    Returns:
        설명 생성 가이드 프롬프트
    """
    return f"""당신은 보험료 예측 결과를 고객에게 친절하게 설명하는 보험 전문가입니다.

다음 예측 결과를 분석하고 자연어로 설명해주세요:

{prediction_result}

## 설명 작성 가이드

### 1. 예측 결과 요약
- 예측된 보험료를 명확히 제시
- 입력된 고객 정보를 간단히 요약

### 2. 주요 영향 요인 설명
`explanation.key_features`를 참고하여:
- 보험료 산정에 가장 큰 영향을 준 요인 3-5개 설명
- 각 요인이 왜 중요한지 설명

### 3. 디시젼 트리 경로 해석
`explanation.tree_paths`를 참고하여:
- 주요 트리 1-2개를 선택하여 의사결정 과정 설명
- 각 분기 조건을 고객이 이해할 수 있는 언어로 변환

**피처 설명 매핑:**
{chr(10).join([f"- {name}: {info['description']}" for name, info in FEATURE_BOUNDS.items()])}

### 4. 예시 설명 패턴

**좋은 설명:**
"예측된 보험료는 $XXX입니다. 이 금액은 고객님의 나이(XX세), 신용점수(XXX), 
과거 청구 이력(X회) 등을 종합적으로 고려하여 산정되었습니다. 

특히 이번 예측에서:
1. 신용점수가 XXX점으로 평균(595점)보다 높아 보험료에 긍정적 영향을 주었습니다.
2. 과거 청구 횟수가 X회로 적어 우량 고객으로 평가되었습니다.
3. 차량 연식이 XX년으로 비교적 새 차량이어서 위험도가 낮게 평가되었습니다.

모델의 의사결정 과정을 살펴보면, 첫 번째 주요 분기에서 신용점수가 
XXX점 이상인 것으로 확인되어 저위험 그룹으로 분류되었고, 이후 건강점수와 
차량 연식을 고려하여 최종 보험료가 결정되었습니다."

**나쁜 설명:**
"보험료는 $XXX입니다. age(35.00) ≤ 40.00 → health_score(25.50) > 20.00 → ..."
(단순히 기술적인 조건만 나열하지 마세요)

### 5. 개선 제안 (선택)
고객이 보험료를 낮출 수 있는 방법을 제안:
- 개선 가능한 요인 제시
- 구체적인 액션 아이템 제공

이제 위 가이드를 따라 예측 결과를 고객 친화적으로 설명해주세요."""


if __name__ == "__main__":
    # MCP 서버 실행
    mcp.run()


