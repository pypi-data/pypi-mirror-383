# Fluent UI 그룹 상자 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluGroupBox` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 관련 UI 요소들을 시각적으로 그룹화하고, 제목과 테두리를 제공하는 컨테이너입니다.

## 공통 임포트 방법

Fluent UI 그룹 상자 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluGroupBox

`FluGroupBox`는 관련 컨트롤이나 콘텐츠를 시각적으로 그룹화하는 데 사용되는 컨테이너입니다. `QtQuick.Templates.GroupBox`를 기반으로 하며, Fluent UI 디자인 원칙에 맞는 스타일(테두리, 배경색, 제목 폰트 등)을 적용합니다. 그룹 상자는 제목 텍스트와 내용 영역 주위의 테두리로 구성됩니다.

### 주요 상속 프로퍼티 (QtQuick.Templates.GroupBox)

`FluGroupBox`는 `QtQuick.Templates.GroupBox`의 모든 표준 프로퍼티를 상속받습니다. 자주 사용되는 프로퍼티는 다음과 같습니다:

*   `title`: 그룹 상자 상단에 표시될 제목 텍스트.
*   `contentItem`: 그룹 상자 내부에 배치될 실제 콘텐츠 아이템 (일반적으로 레이아웃).
*   `padding`: 내부 콘텐츠와 그룹 상자 테두리 사이의 여백.
*   `spacing`: 제목과 콘텐츠 사이의 수직 간격.
*   `font`: 제목 레이블에 사용될 기본 글꼴 (스타일링 프로퍼티에서 재정의됨).

### 고유/스타일링 프로퍼티

`FluGroupBox`는 Fluent UI 스타일을 적용하기 위해 다음과 같은 프로퍼티를 제공하거나 기본값을 재정의합니다:

| 이름          | 타입    | 기본값                      | 설명                                                               |
| :------------ | :------ | :-------------------------- | :----------------------------------------------------------------- |
| `borderWidth` | `int`   | `1`                         | 그룹 상자 테두리의 두께.                                             |
| `borderColor` | `color` | `FluTheme.dividerColor`     | 그룹 상자 테두리의 색상. Fluent UI 테마의 구분선 색상을 따릅니다.        |
| `color`       | `color` | (테마 및 창 활성 상태 따름) | 그룹 상자 배경의 색상. 창이 활성화 상태일 때와 아닐 때 다른 테마 색상을 사용합니다. |
| `radius`      | `int`   | `4`                         | 배경 사각형의 모서리 둥글기 반경.                                        |
| `label`       | `Item`  | `FluText` 인스턴스          | 제목을 표시하는 기본 대리자. `FluText`를 사용하고 `FluTextStyle.BodyStrong` 폰트 스타일이 적용됩니다. |
| `background`  | `Item`  | `Rectangle` 인스턴스        | 배경을 그리는 기본 대리자. `borderColor`, `borderWidth`, `color`, `radius` 프로퍼티를 사용하여 사각형을 그립니다. |

### 고유 시그널

`FluGroupBox` 자체에 고유한 시그널은 정의되어 있지 않습니다.

### 고유 메소드

`FluGroupBox` 자체에 고유한 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    width: 300

    FluGroupBox {
        title: qsTr("체크박스 그룹")
        Layout.fillWidth: true

        ColumnLayout { // contentItem에 해당
            anchors.fill: parent // GroupBox 크기에 맞게 채움
            spacing: 10

            FluCheckBox { text: qsTr("이메일") }
            FluCheckBox { text: qsTr("캘린더") }
            FluCheckBox { text: qsTr("연락처") }
        }
    }

    FluGroupBox {
        title: qsTr("라디오 버튼 그룹")
        Layout.fillWidth: true

        FluRadioButtons { // contentItem에 해당
            anchors.fill: parent
            padding: 12 // GroupBox 패딩과 별개로 내부 여백 추가
            spacing: 10

            FluRadioButton { text: qsTr("옵션 1") }
            FluRadioButton { text: qsTr("옵션 2") }
            FluRadioButton { text: qsTr("옵션 3") }
        }
    }
}
```

### 참고 사항

*   `FluGroupBox`는 주로 관련 컨트롤들을 시각적으로 묶어 UI 구조를 명확하게 하는 데 사용됩니다.
*   기본 스타일은 Fluent UI 테마를 따르며, `borderColor`, `color`, `radius` 등의 프로퍼티를 통해 일부 외관을 조정할 수 있습니다.
*   그룹 상자 내부에 콘텐츠를 배치하려면 일반적으로 `ColumnLayout`, `RowLayout`, `GridLayout` 또는 다른 컨테이너 아이템을 `contentItem`으로 사용합니다.
*   `padding` 프로퍼티는 그룹 상자 테두리와 내부 `contentItem` 사이의 여백을 제어합니다. 