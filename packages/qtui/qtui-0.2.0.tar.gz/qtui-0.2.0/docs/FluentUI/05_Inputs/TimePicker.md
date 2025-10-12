# Fluent UI 시간 선택 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTimePicker` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 버튼 형태로 시간을 표시하고, 클릭 시 팝업을 통해 시간을 선택할 수 있게 합니다.

## 공통 임포트 방법

Fluent UI 시간 선택 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluTimePicker

버튼 형태로 현재 선택된 시간을 보여주며, 버튼 클릭 시 시/분(및 필요한 경우 AM/PM)을 스크롤하여 선택할 수 있는 팝업 메뉴를 제공합니다. `FluButton`을 기반으로 합니다.

### 주요 상속 프로퍼티 (FluButton)

`FluTimePicker`는 `FluButton`의 스타일 관련 프로퍼티(색상, 배경 등)를 상속받습니다. 버튼의 기본적인 시각적 스타일은 `FluButton`과 유사합니다.

### 고유/특징적 프로퍼티

| 이름         | 타입    | 기본값                            | 설명                                                                                         |
| :----------- | :------ | :-------------------------------- | :------------------------------------------------------------------------------------------- |
| `current`    | `var`   | `undefined`                       | 현재 선택된 시간 (`Date` 객체). 이 값을 설정하면 초기 시간이 지정됩니다. 시간 정보만 유효합니다.          |
| `hourFormat` | `enum`  | `FluTimePickerType.H` (12시간제) | 시간 표시 형식. `FluTimePickerType.H` (1-12, AM/PM 표시) 또는 `FluTimePickerType.HH` (0-23) 중 선택. |
| `amText`     | `string`| `qsTr("AM")`                    | 12시간제에서 오전(AM)을 나타내는 텍스트.                                                        |
| `pmText`     | `string`| `qsTr("PM")`                    | 12시간제에서 오후(PM)를 나타내는 텍스트.                                                        |
| `hourText`   | `string`| `qsTr("Hour")`                  | 시간이 선택되지 않았을 때 또는 팝업의 시간 컬럼 레이블로 사용될 수 있는 텍스트.                    |
| `minuteText` | `string`| `qsTr("Minute")`                | 분이 선택되지 않았을 때 또는 팝업의 분 컬럼 레이블로 사용될 수 있는 텍스트.                     |
| `cancelText` | `string`| `qsTr("Cancel")`                | 팝업 내 '취소' 버튼의 텍스트.                                                                |
| `okText`     | `string`| `qsTr("OK")`                    | 팝업 내 '확인' 버튼의 텍스트.                                                                |

*참고: `FluTimePickerType` 열거형은 `H`(12시간제)와 `HH`(24시간제) 두 가지 값을 가집니다.* 

### 고유 시그널

| 이름        | 파라미터 | 반환타입 | 설명                                               |
| :---------- | :------- | :------- | :------------------------------------------------- |
| `accepted()`| 없음     | -        | 사용자가 팝업에서 '확인' 버튼을 눌러 시간 선택을 완료했을 때 발생. |

### 예제

```qml
Column {
    spacing: 10

    FluTimePicker {
        id: timePicker12H
        width: 200
        hourFormat: FluTimePickerType.H // 12시간제 (기본값)
        current: new Date(0, 0, 0, 14, 30) // 오후 2시 30분으로 초기화

        onAccepted: {
            console.log("선택된 시간 (12H):", current.toLocaleTimeString(Qt.locale(), "h:mm AP"))
        }
    }

    FluTimePicker {
        id: timePicker24H
        width: 150
        hourFormat: FluTimePickerType.HH // 24시간제
        current: new Date() // 현재 시간으로 초기화

        // 버튼 텍스트 형식 변경 (HH:mm)
        text: current ? current.toLocaleTimeString(Qt.locale(), "HH:mm") : qsTr("시간 선택")

        onAccepted: {
            console.log("선택된 시간 (24H):", current.toLocaleTimeString(Qt.locale(), "HH:mm"))
        }
    }
}
```

### 참고 사항

*   `current` 프로퍼티는 JavaScript `Date` 객체를 사용하지만, 주로 시간 정보(시, 분)가 중요합니다. 날짜 부분은 현재 날짜 또는 1970년 1월 1일 기준으로 설정될 수 있습니다.
*   버튼에 표시되는 텍스트는 기본적으로 로캘 형식에 따라 다를 수 있으며, `text` 프로퍼티를 직접 설정하여 원하는 형식으로 변경할 수 있습니다.
*   팝업 UI는 시/분(및 AM/PM)을 각각 스크롤하는 `ListView`로 구성됩니다.
*   `hourFormat` 프로퍼티에 따라 팝업 UI 구성(AM/PM 컬럼 유무) 및 시간 선택 로직이 변경됩니다.
*   각종 텍스트 프로퍼티(`amText`, `pmText`, `hourText` 등)를 통해 팝업 및 버튼의 텍스트를 지역화하거나 변경할 수 있습니다. 