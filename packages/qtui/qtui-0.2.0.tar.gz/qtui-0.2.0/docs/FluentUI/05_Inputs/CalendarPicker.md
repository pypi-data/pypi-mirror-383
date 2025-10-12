# Fluent UI 달력 선택 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluCalendarPicker` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 텍스트 입력 필드와 달력 팝업을 결합하여 사용자가 날짜를 쉽게 선택하고 표시할 수 있도록 합니다.

## 공통 임포트 방법

Fluent UI 달력 선택 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluCalendarPicker

선택된 날짜를 보여주는 텍스트 입력 필드와 달력 아이콘 모양의 버튼으로 구성됩니다. 버튼을 클릭하면 월별 달력 뷰가 포함된 팝업이 나타나 사용자가 특정 날짜를 선택할 수 있습니다. 내부적으로 `FluTextBox`, `FluButton`, 달력 로직 및 `FluPopup` 등을 활용하여 구현될 수 있습니다.

### 주요 구성 요소 및 특징

*   **텍스트 입력 필드**: 선택된 날짜를 `dateFormat`에 지정된 형식으로 표시합니다. 사용자가 직접 날짜를 입력할 수도 있습니다 (구현에 따라 다름).
*   **달력 아이콘 버튼**: 클릭 시 달력 팝업을 엽니다.
*   **달력 팝업**: 월 단위의 달력 그리드를 표시하여 날짜를 시각적으로 선택할 수 있습니다. 년/월 이동 기능을 포함합니다.

### 고유/특징적 프로퍼티

| 이름              | 타입    | 기본값                         | 설명                                                                   |
| :---------------- | :------ | :----------------------------- | :--------------------------------------------------------------------- |
| `date`            | `Date`  | `undefined`                    | 현재 선택된 날짜 (`Date` 객체). 이 값을 설정하면 초기 날짜가 지정됩니다.         |
| `dateFormat`      | `string`| `"yyyy-MM-dd"`               | 텍스트 필드에 날짜를 표시할 형식. `Qt.formatDateTime` 형식을 따릅니다.      |
| `placeholderText` | `string`| `qsTr("Select a date")`      | 날짜가 선택되지 않았을 때 텍스트 필드에 표시되는 안내 문구.                   |
| `minimumDate`     | `Date`  | `undefined` (제한 없음)        | 달력 팝업에서 선택 가능한 최소 날짜. 이 날짜 이전은 비활성화됩니다.         |
| `maximumDate`     | `Date`  | `undefined` (제한 없음)        | 달력 팝업에서 선택 가능한 최대 날짜. 이 날짜 이후는 비활성화됩니다.         |

### 고유 시그널

| 이름           | 파라미터 | 반환타입 | 설명                                                         |
| :------------- | :------- | :------- | :----------------------------------------------------------- |
| `accepted()`   | 없음     | -        | 사용자가 달력 팝업에서 날짜를 선택하고 확인했을 때 발생.           |
| `dateChanged()`| `date`   | -        | `date` 프로퍼티 값이 변경될 때 발생하며, 변경된 날짜를 파라미터로 전달합니다. |

### 예제

```qml
import QtQuick 2.15
import FluentUI 1.0
import QtQuick.Layouts 1.15

ColumnLayout {
    spacing: 10

    FluCalendarPicker {
        id: calendarPicker
        Layout.preferredWidth: 250
        date: new Date(2024, 5, 15) // 초기 날짜 설정 (2024년 6월 15일)
        dateFormat: "MMMM d, yyyy" // 날짜 표시 형식 변경

        // 2024년 6월 1일부터 2024년 6월 30일까지만 선택 가능하도록 제한
        minimumDate: new Date(2024, 5, 1)
        maximumDate: new Date(2024, 5, 30)

        onAccepted: {
            console.log("팝업 확인됨. 최종 선택 날짜:", date.toLocaleDateString())
        }

        onDateChanged: {
            console.log("날짜 변경됨:", date.toLocaleDateString())
            statusText.text = "선택된 날짜: " + date.toLocaleDateString(Qt.locale(), dateFormat)
        }
    }

    FluText {
        id: statusText
        text: "날짜를 선택하세요."
    }
}
```

### 참고 사항

*   `FluCalendarPicker`는 `FluDatePicker`와 달리 팝업에서 월별 달력 그리드를 보여주어 날짜 선택 경험이 다릅니다.
*   `date`, `minimumDate`, `maximumDate` 프로퍼티는 JavaScript `Date` 객체를 사용합니다.
*   `dateFormat`은 Qt의 날짜/시간 형식 문자열을 따릅니다. (예: `yyyy`, `MM`, `M`, `dd`, `d`, `ddd`, `dddd` 등)
*   `minimumDate`와 `maximumDate`를 설정하여 사용자가 선택할 수 있는 날짜 범위를 제한할 수 있습니다. 설정하지 않으면 제한이 없습니다.
*   `dateChanged` 시그널은 사용자가 팝업에서 날짜를 클릭할 때마다 발생할 수 있으며, `accepted`는 최종적으로 확인 버튼을 눌렀을 때 발생합니다. 