# Fluent UI 캐러셀 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluCarousel` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 이미지나 카드 같은 아이템 컬렉션을 순환하며 보여주는 인터페이스를 제공합니다.

## 공통 임포트 방법

Fluent UI 캐러셀 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluCarousel

`FluCarousel`은 여러 아이템(일반적으로 이미지 배너 또는 카드)을 한 번에 하나씩 보여주고, 사용자가 좌우로 스와이프하여 탐색할 수 있게 해주는 컴포넌트입니다. 설정된 시간 간격에 따라 자동으로 아이템이 전환되는 자동 재생 기능과, 마지막 아이템에서 첫 아이템으로 (또는 그 반대로) 자연스럽게 넘어가는 무한 루프 기능을 지원합니다. 현재 표시 중인 아이템의 위치를 나타내는 페이지 표시기(점)를 옵션으로 표시할 수 있습니다.

### 기반 클래스

`Item` (내부적으로 `ListView`를 사용하여 아이템 표시 및 스크롤 구현)

### 고유/특징적 프로퍼티

| 이름                    | 타입        | 기본값                             | 설명                                                                                                                               |
| :---------------------- | :---------- | :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `model`                 | `var`       | -                                  | 캐러셀에 표시할 데이터 모델. 일반적으로 QML `ListModel` 또는 JavaScript 배열(객체 리스트)을 사용합니다.                                        |
| `delegate`              | `Component` | -                                  | `model`의 각 아이템을 표시하는 데 사용될 QML 컴포넌트. 델리게이트 컨텍스트 내에서 `model`(해당 아이템 데이터) 및 `displayIndex`(원본 모델에서의 인덱스) 프로퍼티를 사용할 수 있습니다. | 
| `autoPlay`              | `bool`      | `true`                             | `true`이면 `loopTime` 간격으로 자동으로 다음 아이템으로 전환됩니다.                                                                  |
| `loopTime`              | `int`       | `2000`                             | 자동 재생 시 아이템 전환 간격 (밀리초).                                                                                             |
| `showIndicator`         | `bool`      | `true`                             | 페이지 위치를 나타내는 표시기(점)를 표시할지 여부.                                                                                   |
| `indicatorGravity`      | `enum`      | `Qt.AlignBottom | Qt.AlignHCenter` | 표시기 컨테이너의 정렬 방식. `Qt.Align...` 플래그 조합을 사용합니다. (예: `Qt.AlignTop | Qt.AlignRight`)                               |
| `indicatorMarginLeft`   | `int`       | `0`                                | 표시기 컨테이너의 왼쪽 여백.                                                                                                      |
| `indicatorMarginRight`  | `int`       | `0`                                | 표시기 컨테이너의 오른쪽 여백.                                                                                                     |
| `indicatorMarginTop`    | `int`       | `0`                                | 표시기 컨테이너의 위쪽 여백.                                                                                                      |
| `indicatorMarginBottom` | `int`       | `20`                               | 표시기 컨테이너의 아래쪽 여백.                                                                                                     |
| `indicatorSpacing`      | `int`       | `10`                               | 표시기 점들 사이의 간격.                                                                                                          |
| `indicatorDelegate`     | `Component` | (기본 원형 점 컴포넌트)              | 각 표시기 점을 위한 사용자 정의 QML 컴포넌트. 컨텍스트 내에서 `checked`(현재 페이지 여부, bool), `realIndex`(내부 ListView 인덱스) 프로퍼티 사용 가능.    |
| `indicatorAnchors`      | `alias`     | -                                  | 표시기 컨테이너(`Row` 레이아웃)의 `anchors` 프로퍼티에 대한 별칭. 고급 위치 조정을 위해 사용될 수 있습니다.                                           |

### 고유 메소드

| 이름             | 파라미터      | 반환타입 | 설명                                                                                                                                 |
| :--------------- | :------------ | :------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `changedIndex` | `int`: `index`| `void`   | 지정된 `index` (내부 `ListView` 기준, 1부터 시작)에 해당하는 아이템으로 캐러셀 뷰를 프로그래밍 방식으로 전환합니다. 자동 재생 타이머도 재시작됩니다. |

### 고유 시그널

`FluCarousel` 자체에 고유한 시그널은 정의되어 있지 않습니다. 내부 `ListView`의 `currentIndex` 변경 등 표준 프로퍼티 변경 시그널을 활용할 수 있습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    width: 400
    spacing: 20

    // 기본 이미지 캐러셀
    FluCarousel {
        id: carousel1
        width: parent.width
        height: 300
        model: [
            { url: "qrc:/example/res/image/banner_1.jpg" },
            { url: "qrc:/example/res/image/banner_2.jpg" },
            { url: "qrc:/example/res/image/banner_3.jpg" }
        ]
        delegate: Component {
            Image {
                anchors.fill: parent
                source: model.url // 모델 데이터 접근
                asynchronous: true
                fillMode: Image.PreserveAspectCrop
            }
        }
    }

    // 사용자 정의 델리게이트 및 표시기 위치 변경
    FluCarousel {
        id: carousel2
        width: parent.width
        height: 300
        loopTime: 1500 // 더 빠른 자동 재생
        indicatorGravity: Qt.AlignHCenter | Qt.AlignTop // 표시기 상단 중앙 배치
        indicatorMarginTop: 15
        model: [
            { url: "qrc:/example/res/image/banner_1.jpg", title: "제목 1" },
            { url: "qrc:/example/res/image/banner_2.jpg", title: "제목 2" },
            { url: "qrc:/example/res/image/banner_3.jpg", title: "제목 3" }
        ]
        delegate: Component {
            Item {
                anchors.fill: parent
                Image {
                    id: img
                    anchors.fill: parent
                    source: model.url
                    asynchronous: true
                    fillMode: Image.PreserveAspectCrop
                }
                Rectangle { // 텍스트 오버레이
                    width: parent.width; height: 40
                    anchors.bottom: parent.bottom
                    color: "#33000000"
                    FluText {
                        anchors.centerIn: parent
                        text: model.title // 모델 데이터 접근
                        color: "white"
                    }
                }
            }
        }
    }
}
```

### 참고 사항

*   **무한 루프**: 내부에 실제 표시할 모델 앞뒤로 마지막 아이템과 첫 아이템을 추가하여 자연스러운 무한 루프 스크롤을 구현합니다. 따라서 내부 `ListView`의 인덱스는 실제 모델 인덱스와 1만큼 차이가 날 수 있습니다 (`delegate`의 `displayIndex`는 원본 모델 인덱스를 제공).
*   **상호작용**: 사용자가 캐러셀을 스와이프하면 `autoPlay`가 활성화되어 있어도 자동 재생 타이머가 일시적으로 중지됩니다. 스와이프가 끝나면 타이머가 다시 시작됩니다.
*   **최소 아이템 개수**: 자동 재생 및 무한 루프 기능은 모델의 아이템 개수가 3개 초과일 때(`model.length > 3`) 활성화됩니다. (내부 `isAnimEnable` 로직 참고 - 실제로는 3개여도 가능할 수 있으나 코드상 3 초과 조건으로 보임, 확인 필요)
*   **표시기 커스터마이징**: `indicatorDelegate` 프로퍼티에 사용자 정의 QML 컴포넌트를 지정하여 표시기 점의 모양과 동작을 변경할 수 있습니다. 델리게이트 내에서 `checked` 프로퍼티를 사용하여 현재 활성화된 점을 구분할 수 있습니다.
*   **프로그래밍 방식 제어**: `changedIndex(index)` 메소드를 사용하여 특정 아이템으로 뷰를 이동시킬 수 있습니다. 