# Fluent UI 이미지 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 이미지 관련 컴포넌트인 `FluImage`에 대해 설명합니다. 이 컴포넌트는 기본적인 `QtQuick.Image`를 확장하여 로딩 및 오류 상태에 대한 시각적 피드백 기능을 추가합니다.

## 공통 임포트 방법

Fluent UI 이미지 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluImage

`QtQuick.Image`를 기반으로, 이미지 로딩 중 상태와 로딩 실패 시 오류 상태를 시각적으로 표시해주는 컴포넌트입니다.

### 주요 상속 프로퍼티 (QtQuick.Image)

`FluImage`는 `QtQuick.Image`의 모든 프로퍼티를 상속받습니다. 자주 사용되는 주요 프로퍼티는 다음과 같습니다.

| 이름       | 타입     | 기본값                         | 설명                                                                 |
| :--------- | :------- | :----------------------------- | :------------------------------------------------------------------- |
| `source`   | `url`    | `""`                           | 표시할 이미지의 URL 또는 로컬 경로.                                    |
| `status`   | `enum`   | `Image.Null`                 | 이미지의 현재 상태 (`Image.Null`, `Image.Ready`, `Image.Loading`, `Image.Error`). (읽기 전용) |
| `progress` | `real`   | `0.0`                          | 이미지 로딩 진행률 (0.0 ~ 1.0). (읽기 전용)                            |
| `fillMode` | `enum`   | `Image.PreserveAspectFit`    | 이미지가 컴포넌트 영역을 채우는 방식 (예: `Image.PreserveAspectFit`).    |
| `asynchronous`| `bool` | `false`                        | 이미지를 비동기적으로 로드할지 여부.                                 |
| `cache`    | `bool`   | `true`                         | 이미지 캐시 사용 여부.                                               |
| `width`    | `real`   | (내용에 따라 다름)             | 컴포넌트 너비.                                                       |
| `height`   | `real`   | (내용에 따라 다름)             | 컴포넌트 높이.                                                       |

### 고유/특징적 프로퍼티

| 이름                | 타입       | 기본값                            | 설명                                                              |
| :------------------ | :--------- | :-------------------------------- | :---------------------------------------------------------------- |
| `errorButtonText`   | `string`   | `qsTr("Reload")`                 | 이미지 로딩 오류 시 표시될 버튼의 텍스트.                             |
| `clickErrorListener`| `function` | 기본 재로드 함수                    | 오류 상태의 버튼 클릭 시 실행될 함수. 기본적으로 이미지 재로드를 시도합니다. |
| `errorItem`         | `Component`| `FluFilledButton`이 포함된 `Rectangle` | `status`가 `Image.Error`일 때 표시될 컴포넌트.                      |
| `loadingItem`       | `Component`| `FluProgressRing`이 포함된 `Rectangle` | `status`가 `Image.Loading`일 때 표시될 컴포넌트.                    |

### 주요 상속 시그널 (QtQuick.Image)

| 이름             | 파라미터 | 반환타입   | 설명                                 |
| :--------------- | :------- | :--------- | :----------------------------------- |
| `statusChanged()`  | 없음     | -          | `status` 프로퍼티 값이 변경될 때 발생. |
| `progressChanged()`| 없음     | -          | `progress` 프로퍼티 값이 변경될 때 발생. |

### 예제

```