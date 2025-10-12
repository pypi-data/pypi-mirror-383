# Fluent UI 날짜 선택 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluDatePicker` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 버튼 형태로 날짜를 표시하고, 클릭 시 팝업을 통해 날짜를 선택할 수 있게 합니다.

## 공통 임포트 방법

Fluent UI 날짜 선택 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluDatePicker

버튼 형태로 현재 선택된 날짜를 보여주며, 버튼 클릭 시 년/월/일을 스크롤하여 선택할 수 있는 팝업 메뉴를 제공합니다. `FluButton`을 기반으로 합니다.

### 주요 상속 프로퍼티 (FluButton)

`FluDatePicker`는 `FluButton`의 스타일 관련 프로퍼티(색상, 배경 등)를 상속받습니다. 버튼의 기본적인 시각적 스타일은 `FluButton`과 유사합니다.

### 고유/특징적 프로퍼티

| 이름         | 타입    | 기본값                 | 설명                                                                         |
| :----------- | :------ | :--------------------- | :--------------------------------------------------------------------------- |
| `current`    | `var`   | `undefined`            | 현재 선택된 날짜 (`Date` 객체). 이 값을 설정하면 초기 날짜가 지정됩니다.               |
| `showYear`   | `bool`  | `true`                 | 팝업에서 '년도' 선택 스크롤 리스트를 표시할지 여부. `false`이면 월/일만 표시됩니다. |
| `yearText`   | `string`| `qsTr("Year")`       | 년도가 선택되지 않았을 때 또는 팝업의 년도 컬럼 레이블로 사용될 수 있는 텍스트.       |
| `monthText`  | `string`| `qsTr("Month")`      | 월이 선택되지 않았을 때 또는 팝업의 월 컬럼 레이블로 사용될 수 있는 텍스트.         |
| `dayText`    | `string`| `qsTr("Day")`        | 일이 선택되지 않았을 때 또는 팝업의 일 컬럼 레이블로 사용될 수 있는 텍스트.         |
| `cancelText` | `string`| `qsTr("Cancel")`     | 팝업 내 '취소' 버튼의 텍스트.                                                |
| `okText`     | `string`| `qsTr("OK")`         | 팝업 내 '확인' 버튼의 텍스트.                                                |

### 고유 시그널

| 이름        | 파라미터 | 반환타입 | 설명                                               |
| :---------- | :------- | :------- | :------------------------------------------------- |
| `accepted()`| 없음     | -        | 사용자가 팝업에서 '확인' 버튼을 눌러 날짜 선택을 완료했을 때 발생. |

### 예제

```qml
Column {
    spacing: 10

    FluDatePicker {
        id: datePicker1
        current: new Date() // 오늘 날짜로 초기화
        width: 200

        onAccepted: {
            console.log("선택된 날짜:", current.toLocaleDateString())
        }
    }

    FluDatePicker {
        id: datePicker2
        showYear: false // 년도 선택 숨김
        width: 150
        current: new Date(2023, 11, 25) // 특정 날짜로 초기화 (월은 0부터 시작)

        // 버튼 텍스트 형식 변경 (월/일 만 표시)
        text: current ? current.toLocaleDateString(Qt.locale(), "M/d") : qsTr("날짜 선택")

        onAccepted: {
            console.log("선택된 월/일:", current.getMonth() + 1, current.getDate())
        }
    }
}
```

### 참고 사항

*   `current` 프로퍼티는 JavaScript `Date` 객체를 사용합니다. 날짜를 설정하거나 읽을 때 이 타입을 사용해야 합니다.
*   버튼에 표시되는 텍스트는 기본적으로 `current` 날짜를 시스템 로캘의 기본 형식(`yyyy/M/d`)으로 보여줍니다. `text` 프로퍼티를 직접 설정하여 표시 형식을 변경할 수 있습니다.
*   팝업 UI는 년/월/일을 각각 스크롤하는 `ListView`로 구성됩니다.
*   `yearText`, `monthText`, `dayText`, `cancelText`, `okText` 프로퍼티를 통해 팝업 및 버튼의 기본 텍스트를 지역화하거나 변경할 수 있습니다.
*   년도 선택 범위는 내부적으로 1924년부터 2048년까지로 설정되어 있습니다. (QML 코드 확인 필요 시 변경 가능) 