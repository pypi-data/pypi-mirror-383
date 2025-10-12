# Fluent UI 피벗 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluPivot` 및 `FluPivotItem` 컴포넌트에 대해 설명합니다. `FluPivot`은 탭 기반 탐색 인터페이스를 제공하여 사용자가 여러 콘텐츠 섹션 간에 전환할 수 있도록 합니다.

## 공통 임포트 방법

Fluent UI 피벗 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts 등 추가
import QtQuick.Layouts 1.15 
```

---

## FluPivot

`FluPivot`는 상단에 탭 헤더를 표시하고, 선택된 탭에 해당하는 콘텐츠를 아래 영역에 보여주는 컨테이너 컨트롤입니다. 사용자는 헤더의 탭 제목을 클릭하여 다른 콘텐츠 섹션으로 전환할 수 있습니다. `Page` 컴포넌트를 기반으로 구현되었습니다.

### 기반 클래스

`Page`

### 주요 사용법

`FluPivot` 컴포넌트 내부에 하나 이상의 `FluPivotItem` 인스턴스를 자식으로 추가하여 각 탭과 해당 콘텐츠를 정의합니다. `currentIndex` 프로퍼티를 사용하여 초기에 표시할 탭을 설정하거나 현재 선택된 탭을 프로그래밍 방식으로 변경할 수 있습니다.

### 고유/특징적 프로퍼티

| 이름               | 타입         | 기본값                      | 설명                                                                                                  |
| :----------------- | :----------- | :-------------------------- | :---------------------------------------------------------------------------------------------------- |
| `content`          | `alias`      | (내부 `d.children`)       | **기본 프로퍼티**. `FluPivotItem` 자식 객체들을 담고 있는 내부 목록에 대한 별칭입니다.                              |
| `currentIndex`     | `alias`      | (내부 `ListView`의 값)      | 현재 활성화된(선택된) 탭의 인덱스 번호(0부터 시작). 이 값을 변경하면 표시되는 탭과 콘텐츠가 전환됩니다.                        |
| `textNormalColor`  | `color`      | (테마 기반 `FluColors.Grey120`) | 헤더에 있는 탭 제목 텍스트의 기본 색상입니다.                                                               |
| `textHoverColor`   | `color`      | (테마 기반 `Grey10`/`Black`) | 헤더의 탭 제목 위에 마우스 커서를 올렸을 때의 텍스트 색상입니다.                                                         |
| `headerSpacing`    | `int`        | `20`                        | 헤더 영역에서 각 탭(버튼) 사이의 가로 간격입니다.                                                              |
| `headerHeight`     | `int`        | `40`                        | 헤더 영역의 높이입니다.                                                                                 |
| `header`           | `ListView`   | (내부 `ListView`)         | 탭 제목들을 가로로 표시하고 클릭 가능한 버튼으로 구현하는 `ListView` 컴포넌트입니다.                                    |
| `highlight`        | `Item`       | (애니메이션 밑줄 `Item`)      | 현재 선택된 탭 아래에 표시되는 애니메이션 효과가 있는 밑줄 표시기(`Rectangle`)를 포함하는 `Item`입니다.                      |
| `font`             | `font`       | `FluTextStyle.Title`        | 헤더 탭 제목에 사용될 기본 글꼴입니다.                                                                      |

*   `FluPivot`은 `Page`에서 상속된 `width`, `height`, `implicitWidth`, `implicitHeight` 등의 프로퍼티도 사용합니다.

### 고유 메소드 / 시그널

`FluPivot` 자체에 고유하게 추가된 메소드나 시그널은 없습니다. `currentIndex` 프로퍼티가 변경될 때 `currentIndexChanged` 시그널이 자동으로 발생합니다.

---

## FluPivotItem

`FluPivotItem`은 `FluPivot` 컨트롤 내의 개별 탭 페이지를 정의하는 데 사용되는 비시각적(`QtObject` 기반) 컴포넌트입니다. 각 `FluPivotItem`은 탭 헤더에 표시될 제목과 해당 탭이 선택되었을 때 표시될 콘텐츠를 정의합니다.

### 기반 클래스

`QtObject`

### 주요 사용법

`FluPivot` 컴포넌트의 직접적인 자식으로 배치합니다. `FluPivot`은 내부에 있는 `FluPivotItem`들을 자동으로 인식하여 탭 구조를 생성합니다.

### 고유 프로퍼티

| 이름          | 타입        | 기본값 | 설명                                                                                                  |
| :------------ | :---------- | :----- | :---------------------------------------------------------------------------------------------------- |
| `title`       | `string`    | `""`   | 이 탭 항목의 제목으로, `FluPivot`의 헤더 영역에 표시될 텍스트입니다.                                                |
| `contentItem` | `Component` | -      | 이 탭이 활성화되었을 때 `FluPivot`의 콘텐츠 영역에 표시될 QML 컴포넌트입니다. `Component { ... }` 형태로 정의합니다. |
| `argument`    | `var`       | -      | `contentItem` 컴포넌트가 로드될 때 `FluLoader`를 통해 전달될 수 있는 추가 데이터입니다 (선택 사항).                      |

---

## 종합 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluFrame {
    width: 500
    height: 300
    padding: 10

    FluPivot {
        anchors.fill: parent
        currentIndex: 1 // 초기에 "읽지 않음" 탭을 선택

        FluPivotItem {
            title: qsTr("전체")
            contentItem: Component {
                FluText {
                    text: qsTr("모든 이메일 내용")
                    anchors.centerIn: parent
                }
            }
        }
        FluPivotItem {
            title: qsTr("읽지 않음")
            contentItem: Component {
                FluText {
                    text: qsTr("읽지 않은 이메일 내용")
                    anchors.centerIn: parent
                }
            }
        }
        FluPivotItem {
            title: qsTr("플래그 지정됨")
            contentItem: Component {
                FluText {
                    text: qsTr("플래그가 지정된 이메일 내용")
                    anchors.centerIn: parent
                }
            }
        }
    }
}
```

### 참고 사항

*   **탭 정의**: `FluPivot` 내부에 `FluPivotItem` 객체를 필요한 만큼 추가하여 탭을 정의합니다.
*   **콘텐츠 표시**: 각 `FluPivotItem`의 `contentItem` 프로퍼티에 QML `Component`를 지정합니다. `FluPivot`은 현재 선택된 탭(`currentIndex`)에 해당하는 `contentItem`을 내부의 `FluLoader`를 사용하여 동적으로 로드하고 표시합니다. 이 방식은 모든 탭의 콘텐츠를 미리 로드하지 않아 성능에 유리합니다.
*   **탐색**: 사용자는 헤더의 탭 제목을 클릭하여 탭 간에 전환할 수 있으며, 이는 `currentIndex` 값을 변경합니다. 프로그래밍 방식으로 `currentIndex` 값을 변경하여 탭을 전환할 수도 있습니다.
*   **스타일**: 헤더의 탭 제목 모양, 텍스트 색상, 간격 및 선택 표시기(밑줄)는 `FluPivot`의 관련 프로퍼티를 통해 제어되며 Fluent UI 스타일을 따릅니다. 