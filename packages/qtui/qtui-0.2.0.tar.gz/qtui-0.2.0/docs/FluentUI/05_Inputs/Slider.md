# Fluent UI 슬라이더 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 슬라이더 컴포넌트인 `FluSlider`와 `FluRangeSlider`에 대해 설명합니다. 이 컴포넌트들은 기본적인 `QtQuick.Templates.Slider` 및 `QtQuick.Templates.RangeSlider`를 기반으로 하며, Fluent UI 스타일과 상호작용 시 값을 보여주는 툴팁 기능을 추가합니다.

## 공통 임포트 방법

Fluent UI 슬라이더 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// import QtQuick.Templates as T // 필요시 기본 템플릿 접근
```

## 공통 특징

*   **Fluent UI 스타일**: 핸들(handle)과 배경(background)에 Fluent UI 디자인 시스템에 맞는 시각적 스타일이 적용됩니다. 핸들은 호버 및 눌림 상태에 따라 시각적 피드백(크기 변경 등)을 제공합니다.
*   **툴팁**: 핸들을 호버하거나 누르고 있을 때 현재 값을 보여주는 `FluTooltip`이 표시될 수 있습니다 (`tooltipEnabled` 프로퍼티로 제어).
*   **기반 템플릿 상속**: `T.Slider`와 `T.RangeSlider`의 모든 기능(값 범위, 스텝, 방향, 스냅 모드 등)을 상속받습니다.

---

## 1. FluSlider

단일 값을 선택하기 위한 슬라이더입니다. `QtQuick.Templates.Slider` (`T.Slider`)를 기반으로 합니다.

### 주요 상속 프로퍼티 (T.Slider)

| 이름         | 타입     | 기본값   | 설명                                                                 |
| :----------- | :------- | :------- | :------------------------------------------------------------------- |
| `value`      | `real`   | `0`      | 슬라이더의 현재 값.                                                    |
| `from`       | `real`   | `0`      | 슬라이더 값의 최소 범위.                                                 |
| `to`         | `real`   | `100`    | 슬라이더 값의 최대 범위.                                                 |
| `stepSize`   | `real`   | `1`      | 슬라이더 값을 증가/감소시키는 단위. 0이면 연속적인 값을 가집니다.           |
| `orientation`| `enum`   | `Qt.Horizontal` | 슬라이더 방향 (`Qt.Horizontal` 또는 `Qt.Vertical`).                     |
| `live`       | `bool`   | `true`   | 핸들을 드래그하는 동안 `value`를 실시간으로 업데이트할지 여부.                |
| `snapMode`   | `enum`   | `Slider.NoSnap` | 핸들을 놓았을 때 값을 `stepSize`에 맞춰 조정할지 여부 (`NoSnap`, `SnapAlways`, `SnapOnRelease`). |
| `position`   | `real`   | (읽기 전용) | `from`과 `to` 사이에서 `value`의 상대적인 위치 (0.0 ~ 1.0).            |
| `visualPosition`| `real` | (읽기 전용) | `position`과 유사하지만 `live`가 false일 때도 실시간 업데이트됨.         |
| `pressed`    | `bool`   | (읽기 전용) | 핸들이 현재 눌려있는지 여부.                                           |
| `hovered`    | `bool`   | (읽기 전용) | 마우스 커서가 핸들 위에 있는지 여부.                                     |

### 고유/특징적 프로퍼티

| 이름            | 타입     | 기본값                  | 설명                                                     |
| :-------------- | :------- | :---------------------- | :------------------------------------------------------- |
| `tooltipEnabled`| `bool`   | `true`                  | 핸들 호버/눌림 시 툴팁 표시 여부.                            |
| `text`          | `string` | `String(control.value)` | 툴팁에 표시될 텍스트. 기본적으로 현재 `value`를 문자열로 표시. |

### 주요 상속 시그널 (T.Slider)

| 이름          | 파라미터 | 반환타입 | 설명                                                         |
| :------------ | :------- | :------- | :----------------------------------------------------------- |
| `moved()`       | 없음     | -        | 사용자가 핸들을 드래그하여 `value`가 변경되었을 때 발생합니다.     |
| `valueChanged()`| 없음     | -        | `value` 프로퍼티의 값이 변경될 때마다 발생합니다 (코드로 변경 포함). |

### 예제

```qml
Row {
    spacing: 20
    FluSlider {
        id: horizontalSlider
        width: 200
        from: 0
        to: 10
        stepSize: 0.1
        value: 5
        // 툴팁 텍스트 사용자 정의 (소수점 한 자리까지 표시)
        text: value.toFixed(1)
        onValueChanged: console.log("수평 슬라이더 값:", value)
    }
    FluSlider {
        orientation: Qt.Vertical
        height: 150
        tooltipEnabled: false // 툴팁 비활성화
        onMoved: console.log("수직 슬라이더 이동 완료:", value)
    }
}
```

### 참고 사항

*   `value` 프로퍼티를 통해 슬라이더의 현재 값을 얻거나 설정할 수 있습니다.
*   툴팁에 표시되는 텍스트는 `text` 프로퍼티를 통해 사용자 정의할 수 있습니다. 기본값은 현재 `value`입니다.

---

## 2. FluRangeSlider

범위를 선택하기 위한 두 개의 핸들을 가진 슬라이더입니다. `QtQuick.Templates.RangeSlider` (`T.RangeSlider`)를 기반으로 합니다.

### 주요 상속 프로퍼티 (T.RangeSlider)

`T.RangeSlider`는 `from`, `to`, `stepSize`, `orientation`, `live`, `snapMode` 등의 프로퍼티를 `FluSlider`와 유사하게 상속받습니다. 가장 큰 차이점은 단일 `value` 대신 `first`와 `second` 객체를 통해 두 핸들의 값을 관리한다는 것입니다.

*   **`first`**: 첫 번째 핸들(보통 왼쪽 또는 아래쪽)을 나타내는 객체.
    *   `first.value`: 첫 번째 핸들의 현재 값.
    *   `first.position`: `value`의 상대적 위치 (0.0 ~ 1.0, 읽기 전용).
    *   `first.visualPosition`: `live`가 false여도 실시간 업데이트되는 위치 (읽기 전용).
    *   `first.pressed`: 첫 번째 핸들의 눌림 상태 (읽기 전용).
    *   `first.hovered`: 첫 번째 핸들의 호버 상태 (읽기 전용).
*   **`second`**: 두 번째 핸들(보통 오른쪽 또는 위쪽)을 나타내는 객체. `first`와 동일한 프로퍼티들을 가집니다.

| 이름       | 타입   | 기본값                 | 설명                             |
| :--------- | :----- | :--------------------- | :------------------------------- |
| `from`     | `real` | `0`                    | 전체 값 범위의 최소값.           |
| `to`       | `real` | `100`                  | 전체 값 범위의 최대값.           |
| `stepSize` | `real` | `1`                    | 값 변경 단위.                  |
| `snapMode` | `enum` | `RangeSlider.SnapAlways` | 핸들을 놓을 때 값 스냅 방식.     |
| `first.value` | `real`| `0` (또는 `from`)      | 첫 번째 핸들 값.                 |
| `second.value`| `real`| `100` (또는 `to`)      | 두 번째 핸들 값.                 |

### 고유/특징적 프로퍼티

| 이름            | 타입   | 기본값 | 설명                                                               |
| :-------------- | :----- | :----- | :----------------------------------------------------------------- |
| `tooltipEnabled`| `bool` | `true` | 각 핸들 호버/눌림 시 툴팁 표시 여부.                                 |
| `isTipInt`      | `bool` | `true` | 툴팁에 표시되는 값을 정수로 반올림할지 여부 (`Math.round` 사용). |

### 주요 상속 시그널 (T.RangeSlider)

각 핸들(`first`, `second`)에 대해 `moved`와 `valueChanged` 시그널이 개별적으로 발생합니다.

| 이름                  | 파라미터 | 반환타입 | 설명                                         |
| :-------------------- | :------- | :------- | :------------------------------------------- |
| `first.moved()`       | 없음     | -        | 첫 번째 핸들을 드래그하여 값이 변경되었을 때 발생. |
| `first.valueChanged()`| 없음     | -        | `first.value` 프로퍼티 값이 변경될 때 발생.   |
| `second.moved()`      | 없음     | -        | 두 번째 핸들을 드래그하여 값이 변경되었을 때 발생. |
| `second.valueChanged()`| 없음     | -        | `second.value` 프로퍼티 값이 변경될 때 발생.  |

### 예제

```qml
FluRangeSlider {
    width: 300
    from: 0
    to: 100
    first.value: 20
    second.value: 80
    stepSize: 5
    snapMode: RangeSlider.SnapOnRelease
    tooltipEnabled: true
    isTipInt: true // 툴팁 값을 정수로 표시

    onFirstValueChanged: {
        console.log("첫 번째 값 변경:", first.value)
    }
    onSecondValueChanged: {
        console.log("두 번째 값 변경:", second.value)
    }
}
```

### 참고 사항

*   `first.value`와 `second.value`를 통해 각 핸들의 값을 개별적으로 설정하거나 읽을 수 있습니다.
*   두 핸들 사이의 영역이 강조 표시됩니다.
*   `isTipInt` 프로퍼티를 `false`로 설정하면 툴팁에 소수점 값이 그대로 표시됩니다.
